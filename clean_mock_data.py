import oracledb
from server import DB_CONFIG

conn = oracledb.connect(**DB_CONFIG)
cursor = conn.cursor()

# 1. Clean Orders/Payments for dummy users (User IDs 2 to 11)
cursor.execute('DELETE FROM payments WHERE order_id IN (SELECT order_id FROM orders WHERE user_id BETWEEN 2 AND 11)')
cursor.execute('DELETE FROM order_items WHERE order_id IN (SELECT order_id FROM orders WHERE user_id BETWEEN 2 AND 11)')
cursor.execute('DELETE FROM orders WHERE user_id BETWEEN 2 AND 11')

# 2. Clean Cart for dummy users
cursor.execute('DELETE FROM cart_items WHERE cart_id IN (SELECT cart_id FROM cart WHERE user_id BETWEEN 2 AND 11)')
cursor.execute('DELETE FROM cart WHERE user_id BETWEEN 2 AND 11')

# 3. Clean dummy users (Keep Admin = 1)
cursor.execute('DELETE FROM users WHERE user_id BETWEEN 2 AND 11')

# 4. Clean dummy products (IDs 1 to 12)
# Need to remove from cart_items and order_items just in case any admin order contained them
cursor.execute('DELETE FROM cart_items WHERE product_id BETWEEN 1 AND 12')
cursor.execute('DELETE FROM order_items WHERE product_id BETWEEN 1 AND 12')
cursor.execute('DELETE FROM products WHERE product_id BETWEEN 1 AND 12')

# 5. Clean dummy categories (IDs 1 to 10) only if they have no products
cursor.execute('DELETE FROM categories WHERE category_id BETWEEN 1 AND 10 AND category_id NOT IN (SELECT category_id FROM products)')

conn.commit()
print('Mock data cleaned successfully!')
