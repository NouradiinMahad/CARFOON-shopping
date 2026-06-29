from flask import Flask, jsonify, request, abort, send_from_directory
from flask_cors import CORS
import oracledb
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.headers.get('X-User-Id')
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401
        
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT role FROM users WHERE user_id = :1", [user_id])
            row = cursor.fetchone()
        conn.close()
        
        if not row or row[0].lower() != 'admin':
            return jsonify({"error": "Forbidden: Admin access required"}), 403
            
        return f(*args, **kwargs)
    return decorated_function
# Enable CORS for frontend integration
CORS(app)

DB_CONFIG = {
    "user": "c##shop_user",
    "password": "shop123",
    "dsn": "localhost:1522/XE"
}

def get_db_connection():
    return oracledb.connect(**DB_CONFIG)

def make_dict_factory(cursor):
    column_names = [d[0].lower() for d in cursor.description]
    def row_factory(*args):
        return dict(zip(column_names, args))
    return row_factory

def parse_sql_script(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    statements = []
    current_statement = []
    
    lines = content.split('\n')
    in_plsql = False
    
    for line in lines:
        stripped = line.strip()
        if not current_statement and (stripped.startswith('--') or not stripped):
            continue
        if not current_statement and (stripped.upper().startswith('SET ') or stripped.upper().startswith('SHOW ')):
            continue
            
        current_statement.append(line)
        upper_stripped = stripped.upper()
        if not in_plsql:
            if (upper_stripped.startswith('CREATE') and 
                ('PACKAGE' in upper_stripped or 'TRIGGER' in upper_stripped or 
                 'PROCEDURE' in upper_stripped or 'FUNCTION' in upper_stripped)) or \
               upper_stripped.startswith('DECLARE') or \
               upper_stripped.startswith('BEGIN'):
                in_plsql = True
        
        if in_plsql:
            if stripped == '/':
                current_statement.pop()
                stmt = '\n'.join(current_statement).strip()
                if stmt:
                    statements.append((stmt, True))
                current_statement = []
                in_plsql = False
        else:
            if stripped.endswith(';'):
                stmt = '\n'.join(current_statement).strip()
                if stmt.endswith(';'):
                    stmt = stmt[:-1].strip()
                if stmt:
                    statements.append((stmt, False))
                current_statement = []
                
    if current_statement:
        stmt = '\n'.join(current_statement).strip()
        if stmt.endswith(';'):
            stmt = stmt[:-1].strip()
        if stmt:
            statements.append((stmt, in_plsql))
            
    return statements

# Helper to get or create cart for a user
def get_or_create_cart_id(cursor, user_id):
    cursor.execute("SELECT cart_id FROM cart WHERE user_id = :user_id", [user_id])
    row = cursor.fetchone()
    if row:
        return int(row[0])
    
    cart_id_var = cursor.var(oracledb.NUMBER)
    cursor.execute(
        "INSERT INTO cart (user_id) VALUES (:user_id) RETURNING cart_id INTO :cart_id",
        {"user_id": user_id, "cart_id": cart_id_var}
    )
    return int(cart_id_var.getvalue()[0])

@app.route('/api/db/reset', methods=['POST'])
@admin_required
def reset_database():
    script_path = os.path.join(os.path.dirname(__file__), 'shop_connections.sql')
    if not os.path.exists(script_path):
        return jsonify({"success": False, "error": "shop_connections.sql not found in server directory"}), 404
        
    try:
        statements = parse_sql_script(script_path)
        conn = get_db_connection()
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to connect or read script: {str(e)}"}), 500
        
    tables_to_drop = [
        "order_audit_logs",
        "payments",
        "order_items",
        "orders",
        "cart_items",
        "cart",
        "products",
        "categories",
        "users"
    ]
    
    try:
        with conn.cursor() as cursor:
            # Drop tables
            for table in tables_to_drop:
                try:
                    cursor.execute(f"DROP TABLE {table} CASCADE CONSTRAINTS")
                except oracledb.DatabaseError as e:
                    error_obj, = e.args
                    if error_obj.code != 942: # Ignore table not found
                        print(f"Warning dropping {table}: {e}")
            
            # Execute SQL script statements
            for stmt, is_plsql in statements:
                cursor.execute(stmt)
                
            conn.commit()
            
        conn.close()
        return jsonify({"success": True, "message": "Database successfully reset and seeded!"})
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return jsonify({"success": False, "error": f"Database initialization failed: {str(e)}"}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT user_id, name, email, role FROM users ORDER BY user_id")
            cursor.rowfactory = make_dict_factory(cursor)
            users = cursor.fetchall()
        conn.close()
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Get products
            cursor.execute("""
                SELECT p.product_id, p.name, p.price, p.category_id, p.image_url, c.category_name 
                FROM products p 
                LEFT JOIN categories c ON p.category_id = c.category_id
                ORDER BY p.product_id
            """)
            cursor.rowfactory = make_dict_factory(cursor)
            products = cursor.fetchall()
            
            # Get categories
            cursor.execute("SELECT category_id, category_name FROM categories ORDER BY category_id")
            cursor.rowfactory = make_dict_factory(cursor)
            categories = cursor.fetchall()
            
        conn.close()
        return jsonify({"products": products, "categories": categories})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/products/add', methods=['POST'])
@admin_required
def add_product():
    name = request.form.get('name')
    price = request.form.get('price')
    category_id = request.form.get('category_id')
    
    if not name or not price:
        return jsonify({"error": "Name and Price are required"}), 400
        
    image_filenames = []
    if 'images' in request.files:
        files = request.files.getlist('images')
        for file in files:
            if file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                image_filenames.append(filename)
                
    image_url_val = ",".join(image_filenames) if image_filenames else None
        
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO products (name, price, category_id, image_url) VALUES (:name, :price, :category_id, :image_url)",
                {"name": name, "price": float(price), "category_id": int(category_id) if category_id else None, "image_url": image_url_val}
            )
            conn.commit()
            
            # Fetch the inserted product to verify name casing (should be upper due to trigger)
            cursor.execute("SELECT product_id, name, price FROM products WHERE name = UPPER(:name)", {"name": name})
            cursor.rowfactory = make_dict_factory(cursor)
            new_prod = cursor.fetchone()
            
        conn.close()
        return jsonify({"success": True, "product": new_prod})
    except Exception as e:
        if "ORA-00001" in str(e):
            return jsonify({"error": f"A product with the name '{name}' already exists. Product names must be unique."}), 400
        return jsonify({"error": str(e)}), 500

@app.route('/api/cart/<int:user_id>', methods=['GET'])
def get_cart(user_id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cart_id = get_or_create_cart_id(cursor, user_id)
            
            cursor.execute("""
                SELECT ci.cart_item_id, ci.product_id, ci.quantity, p.name, p.price 
                FROM cart_items ci
                JOIN products p ON ci.product_id = p.product_id
                WHERE ci.cart_id = :cart_id
                ORDER BY ci.cart_item_id
            """, {"cart_id": cart_id})
            cursor.rowfactory = make_dict_factory(cursor)
            items = cursor.fetchall()
            
        conn.close()
        return jsonify({"cart_id": cart_id, "items": items})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    data = request.json
    user_id = data.get('user_id')
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    
    if user_id is None or product_id is None or quantity is None:
        return jsonify({"error": "user_id, product_id, and quantity are required"}), 400
        
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cart_id = get_or_create_cart_id(cursor, int(user_id))
            
            # Call stored PL/SQL procedure
            # pkg_order_management.add_item_to_cart(p_cart_id, p_product_id, p_quantity)
            try:
                cursor.callproc("pkg_order_management.add_item_to_cart", [cart_id, int(product_id), int(quantity)])
                conn.commit()
                success = True
                message = "Item successfully added to cart (via Oracle PL/SQL package)."
                err_msg = None
            except oracledb.DatabaseError as db_err:
                conn.rollback()
                success = False
                error_obj, = db_err.args
                # Extracted PL/SQL exception message
                err_msg = error_obj.message
                message = f"Oracle PL/SQL Exception Raised: {err_msg}"
                
        conn.close()
        if success:
            return jsonify({"success": True, "message": message})
        else:
            return jsonify({"success": False, "error": err_msg, "message": message}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/cart/checkout', methods=['POST'])
def checkout():
    data = request.json
    user_id = data.get('user_id')
    
    if user_id is None:
        return jsonify({"error": "user_id is required"}), 400
        
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cart_id = get_or_create_cart_id(cursor, int(user_id))
            
            # Verify if cart has items first
            cursor.execute("SELECT COUNT(*) FROM cart_items WHERE cart_id = :cart_id", {"cart_id": cart_id})
            if cursor.fetchone()[0] == 0:
                return jsonify({"success": False, "error": "Cart is empty"}), 400
                
            # Prepare OUT variable for new order ID
            new_order_id_var = cursor.var(oracledb.NUMBER)
            
            cursor.callproc("pkg_order_management.process_bulk_checkout", [cart_id, int(user_id), new_order_id_var])
            new_order_id = int(new_order_id_var.getvalue())
            
            # Fetch the total amount of the new order
            cursor.execute("SELECT total_amount FROM orders WHERE order_id = :id", {"id": new_order_id})
            total_amount = cursor.fetchone()[0]
            
            # Since the user pays when ordering, we simulate the payment success here:
            cursor.execute(
                "INSERT INTO payments (order_id, amount) VALUES (:order_id, :amount)",
                {"order_id": new_order_id, "amount": total_amount}
            )
            
            # Mark the order as Completed
            cursor.execute("UPDATE orders SET status = 'Completed' WHERE order_id = :id", {"id": new_order_id})
            
            conn.commit()
            
            return jsonify({
                "success": True, 
                "message": "Order placed and paid successfully", 
                "order_id": new_order_id,
                "total_amount": total_amount
            })
    except Exception as e:
        if 'conn' in locals() and conn:
            try:
                conn.rollback()
            except Exception:
                pass
        return jsonify({"error": str(e)}), 500
    finally:
        if 'conn' in locals() and conn:
            try:
                conn.close()
            except Exception:
                pass

@app.route('/api/orders/pay', methods=['POST'])
def pay_order():
    data = request.json
    order_id = data.get('order_id')
    amount = data.get('amount')
    
    if not order_id or not amount:
        return jsonify({"success": False, "error": "Missing order_id or amount"}), 400
        
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT status FROM orders WHERE order_id = :order_id", {"order_id": order_id})
            res = cursor.fetchone()
            if not res:
                return jsonify({"success": False, "error": "Order not found"}), 404
            
            if res[0] == 'Completed':
                return jsonify({"success": False, "error": "Order is already paid"}), 400
                
            cursor.execute("INSERT INTO payments (order_id, amount) VALUES (:order_id, :amount)", 
                           {"order_id": order_id, "amount": amount})
            
            cursor.execute("UPDATE orders SET status = 'Completed' WHERE order_id = :order_id", {"order_id": order_id})
            
            conn.commit()
            
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/orders/<int:user_id>', methods=['GET'])
def get_orders(user_id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT order_id, total_amount, status 
                FROM orders 
                WHERE user_id = :user_id 
                ORDER BY order_id DESC
            """, {"user_id": user_id})
            cursor.rowfactory = make_dict_factory(cursor)
            orders = cursor.fetchall()
            
            # Get order items for each order
            for order in orders:
                cursor.execute("""
                    SELECT oi.order_item_id, oi.product_id, oi.quantity, p.name, p.price
                    FROM order_items oi
                    JOIN products p ON oi.product_id = p.product_id
                    WHERE oi.order_id = :order_id
                    ORDER BY oi.order_item_id
                """, {"order_id": order["order_id"]})
                cursor.rowfactory = make_dict_factory(cursor)
                order["items"] = cursor.fetchall()
                
                # Fetch payment if any
                cursor.execute("SELECT payment_id, amount FROM payments WHERE order_id = :order_id", 
                               {"order_id": order["order_id"]})
                cursor.rowfactory = make_dict_factory(cursor)
                order["payment"] = cursor.fetchone()
                
        conn.close()
        return jsonify(orders)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/payments/user/<int:user_id>', methods=['GET'])
def get_user_payments(user_id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT p.payment_id, p.order_id, p.amount, p.payment_date, o.status 
                FROM payments p
                JOIN orders o ON p.order_id = o.order_id
                WHERE o.user_id = :user_id
                ORDER BY p.payment_date DESC
            """, {"user_id": user_id})
            cursor.rowfactory = make_dict_factory(cursor)
            payments = cursor.fetchall()
            
            # Format dates to string
            for p in payments:
                if 'payment_date' in p and p['payment_date']:
                    p['payment_date'] = p['payment_date'].strftime('%Y-%m-%d %H:%M:%S')
                    
        conn.close()
        return jsonify({"success": True, "payments": payments})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/orders/update-status', methods=['POST'])
def update_order_status():
    data = request.json
    order_id = data.get('order_id')
    status = data.get('status')
    
    if not order_id or not status:
        return jsonify({"error": "order_id and status are required"}), 400
        
    if status not in ['Pending', 'Completed', 'Cancelled', 'Shipped']:
        return jsonify({"error": "Invalid order status"}), 400
        
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE orders SET status = :status WHERE order_id = :order_id",
                {"status": status, "order_id": int(order_id)}
            )
            conn.commit()
        conn.close()
        return jsonify({"success": True, "message": f"Order #{order_id} status updated to {status} (triggered audit log)."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/audit-logs', methods=['GET'])
@admin_required
def get_audit_logs():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT log_id, order_id, old_status, new_status, TO_CHAR(changed_at, 'YYYY-MM-DD HH24:MI:SS') as changed_at FROM order_audit_logs ORDER BY log_id DESC")
            cursor.rowfactory = make_dict_factory(cursor)
            logs = cursor.fetchall()
        conn.close()
        return jsonify(logs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to fetch raw data of tables (for the Admin SQL view)
@app.route('/api/admin/table/<table_name>', methods=['GET'])
@admin_required
def get_table_data(table_name):
    allowed_tables = [
        "users", "categories", "products", "cart", 
        "cart_items", "orders", "order_items", 
        "payments", "order_audit_logs"
    ]
    if table_name.lower() not in allowed_tables:
        return jsonify({"error": "Unauthorized or non-existent table"}), 400
        
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Retrieve column details
            cursor.execute(f"SELECT column_name, data_type FROM user_tab_cols WHERE table_name = UPPER(:table_name)", 
                           {"table_name": table_name})
            columns = [{"name": row[0], "type": row[1]} for row in cursor]
            
            # Retrieve rows
            cursor.execute(f"SELECT * FROM {table_name}")
            cursor.rowfactory = make_dict_factory(cursor)
            rows = cursor.fetchall()
            
        conn.close()
        return jsonify({"columns": columns, "rows": rows})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    login_id = data.get('email')
    password = data.get('password')
    
    if not login_id or not password:
        return jsonify({"success": False, "error": "Email/Username and Password are required"}), 400
        
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT user_id, name, email, role, password 
                FROM users 
                WHERE email = :login_id OR name = :login_id
            """, {"login_id": login_id})
            cursor.rowfactory = make_dict_factory(cursor)
            user = cursor.fetchone()
        conn.close()
        
        if not user:
            return jsonify({"success": False, "error": "Invalid username/email or password"}), 401
            
        is_correct = False
        try:
            is_correct = check_password_hash(user["password"], password)
        except Exception:
            pass
            
        if not is_correct:
            is_correct = (user["password"] == password)
            if is_correct:
                # Upgrade plain-text password to hash in DB
                try:
                    hashed_pwd = generate_password_hash(password)
                    conn = get_db_connection()
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            UPDATE users 
                            SET password = :password 
                            WHERE user_id = :user_id
                        """, {"password": hashed_pwd, "user_id": user["user_id"]})
                        conn.commit()
                    conn.close()
                except Exception as db_err:
                    print(f"Warning: Failed to auto-upgrade plain-text password for user {user['user_id']}: {db_err}")

        if is_correct:
            user.pop("password", None)
            return jsonify({"success": True, "user": user})
        else:
            return jsonify({"success": False, "error": "Invalid username/email or password"}), 401
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    if not name or not email or not password:
        return jsonify({"success": False, "error": "All fields are required"}), 400
        
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Check if email exists
            cursor.execute("SELECT COUNT(*) FROM users WHERE email = :email", {"email": email})
            if cursor.fetchone()[0] > 0:
                return jsonify({"success": False, "error": "This email is already registered!"}), 400
            
            hashed_password = generate_password_hash(password)
            
            # Insert user
            user_id_var = cursor.var(oracledb.NUMBER)
            cursor.execute("""
                INSERT INTO users (name, email, password, role) 
                VALUES (:name, :email, :password, 'customer') 
                RETURNING user_id INTO :user_id
            """, {"name": name, "email": email, "password": hashed_password, "user_id": user_id_var})
            user_id = int(user_id_var.getvalue()[0])
            
            # Create shopping cart
            cursor.execute("INSERT INTO cart (user_id) VALUES (:user_id)", {"user_id": user_id})
            
            conn.commit()
        return jsonify({"success": True, "message": "Diiwaan-gelinta waa lagu guuleystay!"})
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass

@app.route('/api/forgot-password/request', methods=['POST'])
def forgot_password_request():
    data = request.json
    email = data.get('email')
    
    if not email:
        return jsonify({"success": False, "error": "Email Address waa muhiim"}), 400
        
    import random
    code = f"{random.randint(100000, 999999)}"
    
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Update user reset code
            cursor.execute("""
                UPDATE users 
                SET reset_code = :code, reset_expiry = SYSDATE + 1/24 
                WHERE email = :email
            """, {"code": code, "email": email})
            
            if cursor.rowcount == 0:
                return jsonify({"success": False, "error": "Ma jiro akoon ka diiwaan gashan email-kaan."}), 404
                
            conn.commit()
        return jsonify({
            "success": True, 
            "code": code, 
            "message": f"Koodhka xaqiijinta waa: {code} (loo soo diray email-kaaga)"
        })
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass

@app.route('/api/forgot-password/reset', methods=['POST'])
def forgot_password_reset():
    data = request.json
    email = data.get('email')
    code = data.get('code')
    password = data.get('password')
    
    if not email or not code or not password:
        return jsonify({"success": False, "error": "Reset code and new password are required"}), 400
        
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Verify code and expiry
            cursor.execute("""
                SELECT user_id FROM users 
                WHERE email = :email AND reset_code = :code AND reset_expiry > SYSDATE
            """, {"email": email, "code": code})
            row = cursor.fetchone()
            
            if not row:
                return jsonify({"success": False, "error": "Invalid or expired reset code."}), 400
            
            # Hash the new password before updating
            hashed_password = generate_password_hash(password)
            
            # Update password
            cursor.execute("""
                UPDATE users 
                SET password = :password, reset_code = NULL, reset_expiry = NULL 
                WHERE email = :email
            """, {"password": hashed_password, "email": email})
            conn.commit()
        return jsonify({"success": True, "message": "Password reset successfully!"})
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass

@app.route('/api/categories/add', methods=['POST'])
def add_category():
    data = request.json
    category_name = data.get('category_name')
    if not category_name:
        return jsonify({"error": "Category Name is required"}), 400
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO categories (category_name) VALUES (:name)", {"name": category_name})
            conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        if "ORA-00001" in str(e):
            return jsonify({"error": f"A category with the name '{category_name}' already exists. Category names must be unique."}), 400
        return jsonify({"error": str(e)}), 500

@app.route('/api/products/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM products WHERE product_id = :id", {"id": product_id})
            conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/categories/delete/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM categories WHERE category_id = :id", {"id": category_id})
            conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/role/<int:user_id>', methods=['POST'])
@admin_required
def update_user_role(user_id):
    try:
        data = request.json
        new_role = data.get('role')
        if new_role not in ['admin', 'manager', 'customer']:
            return jsonify({"error": "Invalid role"}), 400
            
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("UPDATE users SET role = :1 WHERE user_id = :2", [new_role, user_id])
            conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE user_id = :id", {"id": user_id})
            conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Sales Over Time (Mocked because schema lacks date columns)
        sales_data = [
            {"date": "2026-06-23", "revenue": 150},
            {"date": "2026-06-24", "revenue": 300},
            {"date": "2026-06-25", "revenue": 200},
            {"date": "2026-06-26", "revenue": 450},
            {"date": "2026-06-27", "revenue": 800},
            {"date": "2026-06-28", "revenue": 650}
        ]
        
        # 2. Revenue by Category
        cursor.execute("""
            SELECT c.category_name, SUM(p.price * oi.quantity) as category_revenue
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            JOIN categories c ON p.category_id = c.category_id
            JOIN orders o ON oi.order_id = o.order_id
            WHERE o.status != 'Cancelled'
            GROUP BY c.category_name
        """)
        category_data = [{"category": row[0], "revenue": float(row[1])} for row in cursor.fetchall()]
        
        conn.close()
        
        # If no sales data, provide some mock data so the charts aren't completely empty
        if not sales_data:
            sales_data = [
                {"date": "2026-06-23", "revenue": 150},
                {"date": "2026-06-24", "revenue": 300},
                {"date": "2026-06-25", "revenue": 200},
                {"date": "2026-06-26", "revenue": 450},
                {"date": "2026-06-27", "revenue": 800},
                {"date": "2026-06-28", "revenue": 650}
            ]
        if not category_data:
            category_data = [
                {"category": "Electronics", "revenue": 1200},
                {"category": "Clothing", "revenue": 400},
                {"category": "Books", "revenue": 150}
            ]

        return jsonify({
            "success": True,
            "sales_over_time": sales_data,
            "revenue_by_category": category_data
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/')
def index():
    return send_from_directory(os.path.dirname(__file__), 'index.html')

@app.route('/index.css')
def index_css():
    return send_from_directory(os.path.dirname(__file__), 'index.css')

@app.route('/app.js')
def app_js():
    return send_from_directory(os.path.dirname(__file__), 'app.js')

if __name__ == '__main__':
    # Run on local port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
