# ==============================================================================
# SIMAD University - Faculty of Computing
# Course: Oracle Database & PL/SQL Programming
# Project: Online Shopping Management System Desktop Client
# Technology: Python 3, Tkinter, python-oracledb (Thin Mode)
# ==============================================================================

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import oracledb
import re
import os
import shutil
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

try:
    from werkzeug.security import generate_password_hash, check_password_hash
except ImportError:
    # Safe fallbacks if werkzeug is not installed
    def generate_password_hash(password):
        return password
    def check_password_hash(hash_str, password):
        return hash_str == password

# ==============================================================================
# DESIGN CONFIGURATION & COLORS
# ==============================================================================
COLOR_PRIMARY = "#0073e6"        # Vibrant Blue from CARFOON Logo
COLOR_PRIMARY_HOVER = "#0084ff"  # Hover Blue
COLOR_SECONDARY = "#072146"      # Deep Navy Blue from CARFOON Logo
COLOR_BACKGROUND = "#f8fafc"     # Cool gray background
COLOR_CARD_BG = "#ffffff"        # White card background
COLOR_TEXT = "#1e293b"           # Dark text
COLOR_TEXT_LIGHT = "#64748b"     # Light gray text
COLOR_BORDER = "#cbd5e1"         # Slate border
COLOR_SUCCESS = "#10b981"        # Emerald green
COLOR_WARNING = "#f26522"        # Vibrant Orange from CARFOON Logo
COLOR_DANGER = "#ef4444"         # Red

FONT_HEADER = ("Segoe UI", 16, "bold")
FONT_TITLE = ("Segoe UI", 12, "bold")
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_NORMAL = ("Segoe UI", 10)
FONT_SMALL = ("Segoe UI", 9)




# Database config matching server.py
DB_USER = "c##shop_user"
DB_PASSWORD = "shop123"
DB_DSN = "localhost:1522/XE"

# ==============================================================================
# DATABASE CONNECTION FUNCTIONS
# ==============================================================================
def get_db_connection():
    """Establishes connection to Oracle Database in Thin Mode (no Oracle client needed)"""
    return oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)

def test_db_connection():
    """Helper function to quickly verify connection health"""
    try:
        conn = get_db_connection()
        conn.close()
        return True, "Connected"
    except Exception as e:
        return False, str(e)

# ==============================================================================
# MAIN APPLICATION ROOT
# ==============================================================================
class OnlineShoppingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CARFOON online shopping - Oracle Desktop Client")
        self.configure(bg=COLOR_BACKGROUND)
        
        # Set Window Titlebar Icon
        try:
            if os.path.exists("carfoon_logo.ico"):
                self.iconbitmap("carfoon_logo.ico")
        except Exception as e:
            print(f"Error loading custom icon: {e}")
        
        # Configure styles
        self.setup_styles()
        
        # Application Session State
        self.current_user = None  # Holds dict containing: user_id, name, email, role
        self.db_status = "Disconnected"
        
        # Check connection on start
        success, err = test_db_connection()
        if success:
            self.db_status = "Connected"
        else:
            self.db_status = "Disconnected"
            messagebox.showwarning("Database Connection Failed", 
                                    f"Could not connect to Oracle database automatically.\nError: {err}\n\nPlease check if database is running.")

        # Show Login Screen by default
        self.show_login_screen()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Customize Treeview Colors & Borders
        self.style.configure("Treeview", 
                             background=COLOR_CARD_BG, 
                             foreground=COLOR_TEXT,
                             fieldbackground=COLOR_CARD_BG, 
                             rowheight=28,
                             font=FONT_NORMAL)
        self.style.map("Treeview", background=[('selected', COLOR_PRIMARY)])
        
        self.style.configure("Treeview.Heading", 
                             background=COLOR_BACKGROUND, 
                             foreground=COLOR_TEXT, 
                             font=FONT_BOLD,
                             borderwidth=1)
        
        # Customize Buttons
        self.style.configure("TButton", 
                             font=FONT_BOLD, 
                             background=COLOR_PRIMARY, 
                             foreground="#ffffff", 
                             borderwidth=0, 
                             focuscolor="")
        self.style.map("TButton", background=[('active', COLOR_PRIMARY_HOVER)])
        
        self.style.configure("Danger.TButton", background=COLOR_DANGER)
        self.style.map("Danger.TButton", background=[('active', "#dc2626")])

        self.style.configure("Success.TButton", background=COLOR_SUCCESS)
        self.style.map("Success.TButton", background=[('active', "#059669")])

        # Customize Frames
        self.style.configure("TFrame", background=COLOR_BACKGROUND)

    def clear_screen(self):
        """Destroys all widgets currently packed or grid inside the root window"""
        for widget in self.winfo_children():
            widget.destroy()

    def show_login_screen(self):
        self.clear_screen()
        self.resizable(False, False)  # Login screen is a compact fixed dialog
        self.geometry("400x570")
        self.title("CARFOON online shopping - Login")
        LoginScreen(self)

    def login_user(self, user_info):
        """Callback from LoginScreen to enter dashboard"""
        self.clear_screen()  # Clear the login screen frames to allow dashboard loading cleanly
        self.current_user = user_info
        
        # Make the dashboard fully resizable and spacious
        self.resizable(True, True)
        self.minsize(1050, 680)
        self.geometry("1150x720")
        
        if user_info["role"] == "admin":
            self.title(f"CARFOON online shopping - Admin Console ({user_info['name']})")
            AdminDashboard(self)
        else:
            self.title(f"CARFOON online shopping - Customer Dashboard ({user_info['name']})")
            CustomerDashboard(self)

    def logout_user(self):
        """Closes dashboard session and returns to login screen"""
        self.current_user = None
        self.show_login_screen()


# ==============================================================================
# LOGIN SCREEN COMPONENT & SUBVIEWS (LOGIN, REGISTER, FORGOT PASSWORD)
# ==============================================================================
class LoginScreen(tk.Frame):
    def __init__(self, app):
        super().__init__(app, bg=COLOR_BACKGROUND)
        self.app = app
        self.pack(expand=True, fill="both")
        
        self.current_view = None
        self.show_login_view()
        
    def show_login_view(self):
        if self.current_view:
            self.current_view.destroy()
        self.current_view = LoginView(self)
        self.current_view.pack(expand=True, fill="both")
        
    def show_register_view(self):
        if self.current_view:
            self.current_view.destroy()
        self.current_view = RegisterView(self)
        self.current_view.pack(expand=True, fill="both")
        
    def show_forgot_view(self):
        if self.current_view:
            self.current_view.destroy()
        self.current_view = ForgotPasswordView(self)
        self.current_view.pack(expand=True, fill="both")


class LoginView(tk.Frame):
    def __init__(self, controller):
        super().__init__(controller, bg=COLOR_BACKGROUND)
        self.controller = controller
        self.app = controller.app
        self.app.geometry("400x560")
        
        # Centered Outer Container Frame
        self.frame = tk.Frame(self, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1)
        self.frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Brand Logo Area
        brand_frame = tk.Frame(self.frame, bg=COLOR_PRIMARY, height=110)
        brand_frame.pack(fill="x")
        
        # Load brand logo image
        self.logo_photo = None
        try:
            if os.path.exists("carfoon_logo.png"):
                from PIL import Image, ImageTk
                img = Image.open("carfoon_logo.png")
                img = img.resize((50, 50), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(img)
                lbl_logo = tk.Label(brand_frame, image=self.logo_photo, bg=COLOR_PRIMARY)
                lbl_logo.pack(pady=(12, 4))
            else:
                lbl_logo = tk.Label(brand_frame, text="🛒", font=("Segoe UI", 28), fg="#ffffff", bg=COLOR_PRIMARY)
                lbl_logo.pack(pady=(10, 0))
        except Exception:
            lbl_logo = tk.Label(brand_frame, text="🛒", font=("Segoe UI", 28), fg="#ffffff", bg=COLOR_PRIMARY)
            lbl_logo.pack(pady=(10, 0))
            
        lbl_brand = tk.Label(brand_frame, text="CARFOON online shopping", font=FONT_TITLE, fg="#ffffff", bg=COLOR_PRIMARY)
        lbl_brand.pack(pady=(2, 10))
        
        # Inputs Body Frame
        body = tk.Frame(self.frame, bg=COLOR_CARD_BG)
        body.pack(fill="both", expand=True, padx=30, pady=15)
        
        lbl_welcome = tk.Label(body, text="Welcome Back", font=FONT_HEADER, fg=COLOR_SECONDARY, bg=COLOR_CARD_BG)
        lbl_welcome.pack(anchor="w")
        
        lbl_sub = tk.Label(body, text="Enter credentials to manage shopping operations", font=FONT_SMALL, fg=COLOR_TEXT_LIGHT, bg=COLOR_CARD_BG)
        lbl_sub.pack(anchor="w", pady=(0, 15))
        
        # Email Field
        lbl_email = tk.Label(body, text="Email Address", font=FONT_BOLD, fg=COLOR_TEXT, bg=COLOR_CARD_BG)
        lbl_email.pack(anchor="w", pady=(5, 2))
        self.entry_email = tk.Entry(body, font=FONT_NORMAL, width=35, highlightthickness=1, highlightbackground=COLOR_BORDER, bd=0)
        self.entry_email.pack(fill="x", ipady=8, pady=(0, 12))
        
        # Password Field
        lbl_password = tk.Label(body, text="Password", font=FONT_BOLD, fg=COLOR_TEXT, bg=COLOR_CARD_BG)
        lbl_password.pack(anchor="w", pady=(5, 2))
        self.entry_password = tk.Entry(body, font=FONT_NORMAL, show="*", width=35, highlightthickness=1, highlightbackground=COLOR_BORDER, bd=0)
        self.entry_password.pack(fill="x", ipady=8, pady=(0, 5))
        
        # Options Row
        options_frame = tk.Frame(body, bg=COLOR_CARD_BG)
        options_frame.pack(fill="x", pady=(0, 15))
        
        self.show_pass_var = tk.BooleanVar(value=False)
        chk_show = tk.Checkbutton(options_frame, text="Show password", variable=self.show_pass_var, 
                                  command=self.toggle_password, font=FONT_SMALL, fg=COLOR_TEXT_LIGHT, bg=COLOR_CARD_BG, activebackground=COLOR_CARD_BG)
        chk_show.pack(side="left")
        
        btn_forgot = tk.Button(options_frame, text="Forgot Password?", font=FONT_SMALL, fg=COLOR_PRIMARY, bg=COLOR_CARD_BG, borderwidth=0, activeforeground=COLOR_PRIMARY_HOVER, cursor="hand2", command=self.controller.show_forgot_view)
        btn_forgot.pack(side="right")
        
        # Submit Button
        btn_login = ttk.Button(body, text="Login →", command=self.handle_login, style="TButton")
        btn_login.pack(fill="x", ipady=6, pady=(0, 10))
        
        # Switch to Register Row
        register_frame = tk.Frame(body, bg=COLOR_CARD_BG)
        register_frame.pack(fill="x", pady=5)
        lbl_no_acct = tk.Label(register_frame, text="Don't have an account?", font=FONT_SMALL, fg=COLOR_TEXT_LIGHT, bg=COLOR_CARD_BG)
        lbl_no_acct.pack(side="left", padx=(30, 5))
        btn_reg = tk.Button(register_frame, text="Sign Up", font=FONT_SMALL, fg=COLOR_PRIMARY, bg=COLOR_CARD_BG, borderwidth=0, activeforeground=COLOR_PRIMARY_HOVER, cursor="hand2", command=self.controller.show_register_view)
        btn_reg.pack(side="left")
        
        # DB Status Indicator
        status_color = COLOR_SUCCESS if self.app.db_status == "Connected" else COLOR_DANGER
        status_text = f"● Database Status: {self.app.db_status}"
        lbl_status = tk.Label(body, text=status_text, font=FONT_SMALL, fg=status_color, bg=COLOR_CARD_BG)
        lbl_status.pack(pady=5)

    def toggle_password(self):
        if self.show_pass_var.get():
            self.entry_password.config(show="")
        else:
            self.entry_password.config(show="*")

    def handle_login(self):
        email = self.entry_email.get().strip()
        password = self.entry_password.get()
        
        if not email or not password:
            messagebox.showerror("Validation Error", "Email Address and Password cannot be empty.")
            return
            
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            messagebox.showerror("Validation Error", "Please enter a valid email format.")
            return
            
        try:
            conn = get_db_connection()
            user_info = None
            login_failed_msg = None
            
            with conn.cursor() as cursor:
                query = "SELECT user_id, name, email, role, password FROM users WHERE email = :email"
                cursor.execute(query, {"email": email})
                row = cursor.fetchone()
                
                if row:
                    user_id, name, role, db_pass = row[0], row[1], row[3], row[4]
                    
                    is_correct = False
                    try:
                        is_correct = check_password_hash(db_pass, password)
                    except Exception:
                        pass
                        
                    if not is_correct:
                        is_correct = (db_pass == password)
                        if is_correct:
                            # Upgrade plain-text password to hash in DB
                            try:
                                hashed_pwd = generate_password_hash(password)
                                cursor.execute("""
                                    UPDATE users 
                                    SET password = :password 
                                    WHERE user_id = :user_id
                                """, {"password": hashed_pwd, "user_id": user_id})
                                conn.commit()
                            except Exception as db_err:
                                print(f"Warning: Failed to auto-upgrade plain-text password in GUI: {db_err}")
                                
                    if is_correct:
                        user_info = {
                            "user_id": user_id,
                            "name": name,
                            "email": email,
                            "role": role
                        }
                    else:
                        login_failed_msg = "Email ama Password oo khalad ah!"
                else:
                    login_failed_msg = "User not found with this email."
            
            # Close connection after cursor context is fully exited
            conn.close()
            
            if user_info:
                self.app.login_user(user_info)
            else:
                messagebox.showerror("Login Failed", login_failed_msg)
                
        except Exception as e:
            messagebox.showerror("Database Connection Error", 
                                 f"Failed to query database credentials.\nDetails: {str(e)}")


class RegisterView(tk.Frame):
    def __init__(self, controller):
        super().__init__(controller, bg=COLOR_BACKGROUND)
        self.controller = controller
        self.app = controller.app
        self.app.geometry("400x630")
        
        # Centered Outer Container Frame
        self.frame = tk.Frame(self, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1)
        self.frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Brand Logo Area
        brand_frame = tk.Frame(self.frame, bg=COLOR_PRIMARY, height=90)
        brand_frame.pack(fill="x")
        lbl_logo = tk.Label(brand_frame, text="🛒", font=("Segoe UI", 24), fg="#ffffff", bg=COLOR_PRIMARY)
        lbl_logo.pack(pady=(8, 0))
        lbl_brand = tk.Label(brand_frame, text="Create Account", font=FONT_TITLE, fg="#ffffff", bg=COLOR_PRIMARY)
        lbl_brand.pack(pady=(2, 8))
        
        # Inputs Body Frame
        body = tk.Frame(self.frame, bg=COLOR_CARD_BG)
        body.pack(fill="both", expand=True, padx=30, pady=10)
        
        # Name Field
        lbl_name = tk.Label(body, text="Full Name *", font=FONT_BOLD, fg=COLOR_TEXT, bg=COLOR_CARD_BG)
        lbl_name.pack(anchor="w", pady=(2, 2))
        self.entry_name = tk.Entry(body, font=FONT_NORMAL, width=35, highlightthickness=1, highlightbackground=COLOR_BORDER, bd=0)
        self.entry_name.pack(fill="x", ipady=6, pady=(0, 10))
        
        # Email Field
        lbl_email = tk.Label(body, text="Email Address *", font=FONT_BOLD, fg=COLOR_TEXT, bg=COLOR_CARD_BG)
        lbl_email.pack(anchor="w", pady=(2, 2))
        self.entry_email = tk.Entry(body, font=FONT_NORMAL, width=35, highlightthickness=1, highlightbackground=COLOR_BORDER, bd=0)
        self.entry_email.pack(fill="x", ipady=6, pady=(0, 10))
        
        # Password Field
        lbl_password = tk.Label(body, text="Password *", font=FONT_BOLD, fg=COLOR_TEXT, bg=COLOR_CARD_BG)
        lbl_password.pack(anchor="w", pady=(2, 2))
        self.entry_password = tk.Entry(body, font=FONT_NORMAL, show="*", width=35, highlightthickness=1, highlightbackground=COLOR_BORDER, bd=0)
        self.entry_password.pack(fill="x", ipady=6, pady=(0, 10))
        
        # Confirm Password Field
        lbl_confirm = tk.Label(body, text="Confirm Password *", font=FONT_BOLD, fg=COLOR_TEXT, bg=COLOR_CARD_BG)
        lbl_confirm.pack(anchor="w", pady=(2, 2))
        self.entry_confirm = tk.Entry(body, font=FONT_NORMAL, show="*", width=35, highlightthickness=1, highlightbackground=COLOR_BORDER, bd=0)
        self.entry_confirm.pack(fill="x", ipady=6, pady=(0, 15))
        
        # Submit Button
        btn_register = ttk.Button(body, text="Sign Up →", command=self.handle_register, style="TButton")
        btn_register.pack(fill="x", ipady=6, pady=(0, 10))
        
        # Back to Login link
        back_frame = tk.Frame(body, bg=COLOR_CARD_BG)
        back_frame.pack(fill="x", pady=5)
        lbl_have_acct = tk.Label(back_frame, text="Already have an account?", font=FONT_SMALL, fg=COLOR_TEXT_LIGHT, bg=COLOR_CARD_BG)
        lbl_have_acct.pack(side="left", padx=(25, 5))
        btn_back = tk.Button(back_frame, text="Login", font=FONT_SMALL, fg=COLOR_PRIMARY, bg=COLOR_CARD_BG, borderwidth=0, activeforeground=COLOR_PRIMARY_HOVER, cursor="hand2", command=self.controller.show_login_view)
        btn_back.pack(side="left")

    def handle_register(self):
        name = self.entry_name.get().strip()
        email = self.entry_email.get().strip()
        password = self.entry_password.get()
        confirm = self.entry_confirm.get()
        
        if not name:
            messagebox.showerror("Validation Error", "Full Name is required.")
            return
        if not email:
            messagebox.showerror("Validation Error", "Email Address is required.")
            return
        if not password:
            messagebox.showerror("Validation Error", "Password is required.")
            return
        if password != confirm:
            messagebox.showerror("Validation Error", "Passwords do not match.")
            return
            
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            messagebox.showerror("Validation Error", "Please enter a valid email format.")
            return
            
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                # Check if email exists
                cursor.execute("SELECT COUNT(*) FROM users WHERE email = :email", {"email": email})
                if cursor.fetchone()[0] > 0:
                    messagebox.showerror("Registration Error", "Email address is already registered!")
                    conn.close()
                    return
                
                # Hash the password first
                hashed_pwd = generate_password_hash(password)
                
                # Insert user
                user_id_var = cursor.var(oracledb.NUMBER)
                cursor.execute("""
                    INSERT INTO users (name, email, password, role) 
                    VALUES (:name, :email, :password, 'customer') 
                    RETURNING user_id INTO :user_id
                """, {"name": name, "email": email, "password": hashed_pwd, "user_id": user_id_var})
                user_id = int(user_id_var.getvalue()[0])
                
                # Create shopping cart
                cursor.execute("INSERT INTO cart (user_id) VALUES (:user_id)", {"user_id": user_id})
                
                conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Registration completed successfully! Please login with your new credentials.")
            self.controller.show_login_view()
        except Exception as e:
            messagebox.showerror("Database Error", f"Registration failed:\n{e}")


class ForgotPasswordView(tk.Frame):
    def __init__(self, controller):
        super().__init__(controller, bg=COLOR_BACKGROUND)
        self.controller = controller
        self.app = controller.app
        self.app.geometry("400x530")
        
        # Centered Outer Container Frame
        self.frame = tk.Frame(self, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1)
        self.frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Brand Logo Area
        brand_frame = tk.Frame(self.frame, bg=COLOR_PRIMARY, height=90)
        brand_frame.pack(fill="x")
        lbl_logo = tk.Label(brand_frame, text="🔑", font=("Segoe UI", 24), fg="#ffffff", bg=COLOR_PRIMARY)
        lbl_logo.pack(pady=(8, 0))
        lbl_brand = tk.Label(brand_frame, text="Reset Password", font=FONT_TITLE, fg="#ffffff", bg=COLOR_PRIMARY)
        lbl_brand.pack(pady=(2, 8))
        
        # Inputs Body Frame
        self.body = tk.Frame(self.frame, bg=COLOR_CARD_BG)
        self.body.pack(fill="both", expand=True, padx=30, pady=15)
        
        self.saved_email = ""
        self.saved_code = ""
        
        self.build_request_phase()

    def build_request_phase(self):
        for w in self.body.winfo_children():
            w.destroy()
            
        lbl_title = tk.Label(self.body, text="Forgot Password", font=FONT_HEADER, fg=COLOR_SECONDARY, bg=COLOR_CARD_BG)
        lbl_title.pack(anchor="w")
        
        lbl_desc = tk.Label(self.body, text="Enter your email to receive a 6-digit verification code.", font=FONT_SMALL, fg=COLOR_TEXT_LIGHT, bg=COLOR_CARD_BG, justify="left", wraplength=300)
        lbl_desc.pack(anchor="w", pady=(0, 15))
        
        # Email Field
        lbl_email = tk.Label(self.body, text="Email Address *", font=FONT_BOLD, fg=COLOR_TEXT, bg=COLOR_CARD_BG)
        lbl_email.pack(anchor="w", pady=(5, 2))
        self.entry_email = tk.Entry(self.body, font=FONT_NORMAL, width=35, highlightthickness=1, highlightbackground=COLOR_BORDER, bd=0)
        self.entry_email.pack(fill="x", ipady=8, pady=(0, 20))
        
        # Submit Button
        btn_send = ttk.Button(self.body, text="Send Verification Code →", command=self.handle_send_code, style="TButton")
        btn_send.pack(fill="x", ipady=6, pady=(0, 15))
        
        # Back to Login
        btn_back = tk.Button(self.body, text="← Back to Login", font=FONT_SMALL, fg=COLOR_PRIMARY, bg=COLOR_CARD_BG, borderwidth=0, activeforeground=COLOR_PRIMARY_HOVER, cursor="hand2", command=self.controller.show_login_view)
        btn_back.pack()

    def handle_send_code(self):
        email = self.entry_email.get().strip()
        if not email:
            messagebox.showerror("Validation Error", "Email Address is required.")
            return
            
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            messagebox.showerror("Validation Error", "Please enter a valid email format.")
            return
            
        import random
        code = f"{random.randint(100000, 999999)}"
        
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                # Update users reset code
                cursor.execute("""
                    UPDATE users 
                    SET reset_code = :code, reset_expiry = SYSDATE + 1/24 
                    WHERE email = :email
                """, {"code": code, "email": email})
                
                if cursor.rowcount == 0:
                    messagebox.showerror("Error", "No user account found with this email.")
                    conn.close()
                    return
                
                conn.commit()
            conn.close()
            
            self.saved_email = email
            self.saved_code = code
            
            messagebox.showinfo("Verification Sent", 
                                f"Verification code generated!\n\nFor testing, your 6-digit code is: {code}\n\n(Printed here since there is no live SMTP server).")
            self.build_reset_phase()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to generate reset code:\n{e}")

    def build_reset_phase(self):
        for w in self.body.winfo_children():
            w.destroy()
            
        lbl_title = tk.Label(self.body, text="Reset Password", font=FONT_HEADER, fg=COLOR_SECONDARY, bg=COLOR_CARD_BG)
        lbl_title.pack(anchor="w")
        
        lbl_desc = tk.Label(self.body, text="Enter the verification code and set your new password.", font=FONT_SMALL, fg=COLOR_TEXT_LIGHT, bg=COLOR_CARD_BG, justify="left", wraplength=300)
        lbl_desc.pack(anchor="w", pady=(0, 10))
        
        # Verification Code
        lbl_code = tk.Label(self.body, text="Verification Code *", font=FONT_BOLD, fg=COLOR_TEXT, bg=COLOR_CARD_BG)
        lbl_code.pack(anchor="w", pady=(2, 2))
        self.entry_code = tk.Entry(self.body, font=FONT_NORMAL, width=35, highlightthickness=1, highlightbackground=COLOR_BORDER, bd=0)
        self.entry_code.pack(fill="x", ipady=6, pady=(0, 8))
        
        # New Password
        lbl_password = tk.Label(self.body, text="New Password *", font=FONT_BOLD, fg=COLOR_TEXT, bg=COLOR_CARD_BG)
        lbl_password.pack(anchor="w", pady=(2, 2))
        self.entry_password = tk.Entry(self.body, font=FONT_NORMAL, show="*", width=35, highlightthickness=1, highlightbackground=COLOR_BORDER, bd=0)
        self.entry_password.pack(fill="x", ipady=6, pady=(0, 8))
        
        # Confirm Password
        lbl_confirm = tk.Label(self.body, text="Confirm New Password *", font=FONT_BOLD, fg=COLOR_TEXT, bg=COLOR_CARD_BG)
        lbl_confirm.pack(anchor="w", pady=(2, 2))
        self.entry_confirm = tk.Entry(self.body, font=FONT_NORMAL, show="*", width=35, highlightthickness=1, highlightbackground=COLOR_BORDER, bd=0)
        self.entry_confirm.pack(fill="x", ipady=6, pady=(0, 12))
        
        # Submit
        btn_reset = ttk.Button(self.body, text="Reset Password →", command=self.handle_reset_password, style="TButton")
        btn_reset.pack(fill="x", ipady=6, pady=(0, 10))
        
        # Cancel link
        btn_back = tk.Button(self.body, text="← Cancel and Back to Login", font=FONT_SMALL, fg=COLOR_PRIMARY, bg=COLOR_CARD_BG, borderwidth=0, activeforeground=COLOR_PRIMARY_HOVER, cursor="hand2", command=self.controller.show_login_view)
        btn_back.pack()

    def handle_reset_password(self):
        code = self.entry_code.get().strip()
        password = self.entry_password.get()
        confirm = self.entry_confirm.get()
        
        if not code:
            messagebox.showerror("Validation Error", "Verification Code is required.")
            return
        if not password:
            messagebox.showerror("Validation Error", "New Password is required.")
            return
        if password != confirm:
            messagebox.showerror("Validation Error", "Passwords do not match.")
            return
            
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                # Verify code and expiry
                cursor.execute("""
                    SELECT user_id FROM users 
                    WHERE email = :email AND reset_code = :code AND reset_expiry > SYSDATE
                """, {"email": self.saved_email, "code": code})
                row = cursor.fetchone()
                
                if not row:
                    messagebox.showerror("Verification Error", "Invalid or expired verification code.")
                    conn.close()
                    return
                
                # Hash the new password before updating
                hashed_pwd = generate_password_hash(password)
                
                # Update password
                cursor.execute("""
                    UPDATE users 
                    SET password = :password, reset_code = NULL, reset_expiry = NULL 
                    WHERE email = :email
                """, {"password": hashed_pwd, "email": self.saved_email})
                conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Password reset successfully! Please login with your new password.")
            self.controller.show_login_view()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to reset password:\n{e}")


# ==============================================================================
# BASE SIDEBAR DASHBOARD CLASS
# ==============================================================================
class BaseDashboard(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLOR_BACKGROUND)
        self.app = parent
        self.pack(fill="both", expand=True)
        
        # Sidebar Menu Left
        self.sidebar = tk.Frame(self, bg=COLOR_SECONDARY, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        # Header banner inside sidebar
        logo_frame = tk.Frame(self.sidebar, bg=COLOR_PRIMARY, height=70)
        logo_frame.pack(fill="x")
        
        # Try loading custom logo image in sidebar header
        self.logo_photo = None
        try:
            if os.path.exists("carfoon_logo.png"):
                from PIL import Image, ImageTk
                img = Image.open("carfoon_logo.png")
                img = img.resize((35, 35), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(img)
                lbl_logo = tk.Label(logo_frame, text=" CARFOON", image=self.logo_photo, compound="left", font=FONT_HEADER, fg="#ffffff", bg=COLOR_PRIMARY)
            else:
                lbl_logo = tk.Label(logo_frame, text="🛒 CARFOON Online", font=FONT_TITLE, fg="#ffffff", bg=COLOR_PRIMARY)
        except Exception:
            lbl_logo = tk.Label(logo_frame, text="🛒 CARFOON Online", font=FONT_TITLE, fg="#ffffff", bg=COLOR_PRIMARY)
        
        lbl_logo.pack(pady=15)
        
        # Current User Badge inside sidebar
        user_frame = tk.Frame(self.sidebar, bg=COLOR_SECONDARY, pady=10)
        user_frame.pack(fill="x", padx=10)
        lbl_hi = tk.Label(user_frame, text="Welcome Back,", font=FONT_SMALL, fg=COLOR_TEXT_LIGHT, bg=COLOR_SECONDARY)
        lbl_hi.pack(anchor="w")
        lbl_username = tk.Label(user_frame, text=self.app.current_user["name"], font=FONT_BOLD, fg="#ffffff", bg=COLOR_SECONDARY)
        lbl_username.pack(anchor="w")
        lbl_role = tk.Label(user_frame, text=f"Role: {self.app.current_user['role'].upper()}", font=FONT_SMALL, fg=COLOR_SUCCESS, bg=COLOR_SECONDARY)
        lbl_role.pack(anchor="w", pady=(2, 0))
        
        sep = tk.Frame(self.sidebar, bg=COLOR_BORDER, height=1)
        sep.pack(fill="x", padx=10, pady=10)
        
        # Sidebar menu buttons container
        self.menu_container = tk.Frame(self.sidebar, bg=COLOR_SECONDARY)
        self.menu_container.pack(fill="both", expand=True)
        
        # Logout button placed at bottom of sidebar
        btn_logout = tk.Button(self.sidebar, text="Logout ↩", font=FONT_BOLD, bg="#dc2626", fg="#ffffff", 
                               activebackground="#b91c1c", activeforeground="#ffffff", borderwidth=0, cursor="hand2", command=self.app.logout_user)
        btn_logout.pack(side="bottom", fill="x", padx=15, pady=15, ipady=8)
        
        def on_enter_logout(e):
            btn_logout.config(bg="#b91c1c")
        def on_leave_logout(e):
            btn_logout.config(bg="#dc2626")
        btn_logout.bind("<Enter>", on_enter_logout)
        btn_logout.bind("<Leave>", on_leave_logout)
        
        # Right Main Content Canvas
        self.main_content = tk.Frame(self, bg=COLOR_BACKGROUND)
        self.main_content.pack(side="right", fill="both", expand=True)
        
        self.current_frame = None
        self.sidebar_buttons = {}
        self.active_view = None

    def add_menu_item(self, text, icon, frame_class):
        """Adds a navigation item to the sidebar menu"""
        btn = tk.Button(self.menu_container, text=f"{icon}  {text}", font=FONT_NORMAL, bg=COLOR_SECONDARY, fg="#cbd5e1",
                        activebackground=COLOR_PRIMARY, activeforeground="#ffffff", borderwidth=0, anchor="w", padx=20, cursor="hand2",
                        command=lambda: self.switch_view(text, frame_class))
        btn.pack(fill="x", ipady=10, pady=2)
        self.sidebar_buttons[text] = btn
        
        # Bind hover transitions to inactive buttons
        def on_enter(e):
            if self.active_view != text:
                btn.config(bg="#112d59", fg="#ffffff")
        def on_leave(e):
            if self.active_view != text:
                btn.config(bg=COLOR_SECONDARY, fg="#cbd5e1")
                
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    def switch_view(self, text, frame_class):
        """Switches the main content canvas to the selected view"""
        self.active_view = text
        # Highlight active sidebar button
        for key, btn in self.sidebar_buttons.items():
            if key == text:
                btn.config(bg=COLOR_PRIMARY, fg="#ffffff")
            else:
                btn.config(bg=COLOR_SECONDARY, fg="#cbd5e1")
                
        # Clear existing view
        if self.current_frame:
            self.current_frame.destroy()
            
        # Instantiate new view
        self.current_frame = frame_class(self.main_content, self)
        self.current_frame.pack(fill="both", expand=True, padx=25, pady=20)

# ==============================================================================
# ADMIN DASHBOARD COMPONENT
# ==============================================================================
class AdminDashboard(BaseDashboard):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Admin menu items
        self.add_menu_item("Dashboard", "📊", AdminDashboardHome)
        self.add_menu_item("Products", "📦", AdminProductsView)
        self.add_menu_item("Categories", "🏷️", AdminCategoriesView)
        self.add_menu_item("Orders", "📝", AdminOrdersView)
        self.add_menu_item("Payments", "💵", AdminPaymentsView)
        self.add_menu_item("Users List", "👥", AdminUsersView)
        self.add_menu_item("Audit Logs", "🕒", AdminAuditLogsView)
        
        # Load Dashboard by default
        self.switch_view("Dashboard", AdminDashboardHome)

# --- 1. ADMIN HOME VIEW ---
class AdminDashboardHome(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BACKGROUND)
        self.controller = controller
        
        # Page Title
        lbl_title = tk.Label(self, text="Admin Management System Dashboard", font=FONT_HEADER, fg=COLOR_SECONDARY, bg=COLOR_BACKGROUND)
        lbl_title.pack(anchor="w", pady=(0, 20))
        
        # Stats summary row
        stats_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
        stats_frame.pack(fill="x", pady=10)
        
        self.card_users = self.create_stat_card(stats_frame, "Registered Users", "0", COLOR_PRIMARY, "👥")
        self.card_products = self.create_stat_card(stats_frame, "Active SKUs", "0", COLOR_SUCCESS, "📦")
        self.card_orders = self.create_stat_card(stats_frame, "Total Orders", "0", COLOR_WARNING, "🛒")
        self.card_revenue = self.create_stat_card(stats_frame, "Total Sales", "$0.00", "#8b5cf6", "💰")
        
        # Charts Area
        self.charts_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
        self.charts_frame.pack(fill="both", expand=True, pady=10, padx=10)
        
        self.fig = Figure(figsize=(8, 4), dpi=100, facecolor=COLOR_BACKGROUND)
        self.ax1 = self.fig.add_subplot(121)
        self.ax2 = self.fig.add_subplot(122)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.charts_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Load Statistics
        self.load_statistics()

    def create_stat_card(self, parent, label, value, color, icon):
        card = tk.Frame(parent, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1, pady=12, padx=15)
        card.pack(side="left", padx=8, fill="both", expand=True)
        
        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=0)
        
        lbl_lbl = tk.Label(card, text=label.upper(), font=("Segoe UI", 8, "bold"), fg=COLOR_TEXT_LIGHT, bg=COLOR_CARD_BG)
        lbl_lbl.grid(row=0, column=0, sticky="w")
        
        lbl_icon = tk.Label(card, text=icon, font=("Segoe UI", 16), fg=color, bg="#f1f5f9", width=3, height=1)
        lbl_icon.grid(row=0, column=1, rowspan=2, sticky="e", padx=(10, 0))
        
        lbl_val = tk.Label(card, text=value, font=("Segoe UI", 20, "bold"), fg=COLOR_TEXT, bg=COLOR_CARD_BG)
        lbl_val.grid(row=1, column=0, sticky="w", pady=(4, 0))
        
        return lbl_val

    def load_statistics(self):
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                # Users count
                cursor.execute("SELECT COUNT(*) FROM users")
                u_cnt = cursor.fetchone()[0]
                self.card_users.config(text=str(u_cnt))
                
                # Products count
                cursor.execute("SELECT COUNT(*) FROM products")
                p_cnt = cursor.fetchone()[0]
                self.card_products.config(text=str(p_cnt))
                
                # Orders count
                cursor.execute("SELECT COUNT(*) FROM orders")
                o_cnt = cursor.fetchone()[0]
                self.card_orders.config(text=str(o_cnt))
                
                # Revenue total
                cursor.execute("SELECT SUM(amount) FROM payments")
                rev = cursor.fetchone()[0]
                rev = rev if rev is not None else 0.0
                self.card_revenue.config(text=f"${rev:,.2f}")
                
                # Category Revenue Chart
                cursor.execute("""
                    SELECT c.category_name, SUM(p.price * oi.quantity) as category_revenue
                    FROM order_items oi
                    JOIN products p ON oi.product_id = p.product_id
                    JOIN categories c ON p.category_id = c.category_id
                    JOIN orders o ON oi.order_id = o.order_id
                    WHERE o.status != 'Cancelled'
                    GROUP BY c.category_name
                """)
                cat_data = cursor.fetchall()
            conn.close()
            
            # Plot Sales Line Chart (Mock Data)
            self.ax1.clear()
            dates = ['Jun 23', 'Jun 24', 'Jun 25', 'Jun 26', 'Jun 27', 'Jun 28']
            revs = [150, 300, 200, 450, 800, 650]
            self.ax1.plot(dates, revs, marker='o', color='#6366f1', linewidth=2)
            self.ax1.set_title("Sales Over Time", color=COLOR_TEXT)
            self.ax1.set_facecolor(COLOR_CARD_BG)
            self.ax1.tick_params(colors=COLOR_TEXT_LIGHT)
            self.ax1.spines['bottom'].set_color(COLOR_BORDER)
            self.ax1.spines['top'].set_visible(False)
            self.ax1.spines['right'].set_visible(False)
            self.ax1.spines['left'].set_color(COLOR_BORDER)
            
            # Plot Category Pie Chart
            self.ax2.clear()
            if cat_data:
                labels = [row[0] for row in cat_data]
                sizes = [row[1] for row in cat_data]
                colors = ['#3b82f6', '#ec4899', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444']
                self.ax2.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, textprops={'color': COLOR_TEXT})
            else:
                self.ax2.text(0.5, 0.5, "No Category Data", ha='center', va='center', color=COLOR_TEXT_LIGHT)
            self.ax2.set_title("Revenue by Category", color=COLOR_TEXT)
            self.ax2.set_facecolor(COLOR_BACKGROUND)
            
            self.fig.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            print(f"Error loading statistics: {e}")

    def reset_database(self):
        if not messagebox.askyesno("Confirm Reset", "Are you sure you want to drop and re-seed the entire database?"):
            return
            
        import os
        script_path = os.path.join(os.path.dirname(__file__), 'shop_connections.sql')
        if not os.path.exists(script_path):
            messagebox.showerror("Error", "shop_connections.sql file not found in current directory.")
            return
            
        try:
            # Re-use the statement parsing from server.py (or a simplified version)
            with open(script_path, 'r', encoding='utf-8') as f:
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
                            statements.append(stmt)
                        current_statement = []
                        in_plsql = False
                else:
                    if stripped.endswith(';'):
                        stmt = '\n'.join(current_statement).strip()
                        if stmt.endswith(';'):
                            stmt = stmt[:-1].strip()
                        if stmt:
                            statements.append(stmt)
                        current_statement = []
            
            conn = get_db_connection()
            with conn.cursor() as cursor:
                # Drop tables in proper constraint order
                tables_to_drop = ["order_audit_logs", "payments", "order_items", "orders", "cart_items", "cart", "products", "categories", "users"]
                for tbl in tables_to_drop:
                    try:
                        cursor.execute(f"DROP TABLE {tbl} CASCADE CONSTRAINTS")
                    except oracledb.DatabaseError as e:
                        err_obj, = e.args
                        if err_obj.code != 942: # Ignore table not found
                            raise e
                
                # Execute creation script
                for stmt in statements:
                    cursor.execute(stmt)
                    
                conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Oracle database schema reset and seeded successfully!")
            self.load_statistics()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reset database: {e}")

# --- 2. ADMIN PRODUCTS VIEW ---
class AdminProductsView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BACKGROUND)
        self.controller = controller
        
        # Top Bar
        top_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
        top_frame.pack(fill="x", pady=(0, 15))
        
        lbl_title = tk.Label(top_frame, text="Inventory Management (Products)", font=FONT_HEADER, fg=COLOR_SECONDARY, bg=COLOR_BACKGROUND)
        lbl_title.pack(side="left")
        
        # Search Box
        search_frame = tk.Frame(top_frame, bg=COLOR_BACKGROUND)
        search_frame.pack(side="right")
        self.entry_search = tk.Entry(search_frame, font=FONT_NORMAL, width=25, highlightthickness=1, highlightbackground=COLOR_BORDER, bd=0)
        self.entry_search.pack(side="left", ipady=5, padx=5)
        self.entry_search.insert(0, "Search by name/category...")
        self.entry_search.bind("<FocusIn>", lambda e: self.entry_search.delete(0, 'end') if self.entry_search.get() == "Search by name/category..." else None)
        
        btn_search = ttk.Button(search_frame, text="🔍 Search", command=self.search_products, style="TButton")
        btn_search.pack(side="left")
        
        btn_refresh = ttk.Button(search_frame, text="🔄 Refresh", command=self.load_data, style="TButton")
        btn_refresh.pack(side="left", padx=5)
        
        # Layout: Grid containing treeview on left and CRUD form on right
        body_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
        body_frame.pack(fill="both", expand=True)
        
        # Treeview Table
        tree_container = tk.Frame(body_frame, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1)
        tree_container.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        self.tree = ttk.Treeview(tree_container, columns=("id", "name", "price", "cat_id", "category"), show="headings")
        self.tree.heading("id", text="Product ID")
        self.tree.heading("name", text="Product Name")
        self.tree.heading("price", text="Price")
        self.tree.heading("cat_id", text="Category ID")
        self.tree.heading("category", text="Category")
        
        self.tree.column("id", width=80, anchor="center")
        self.tree.column("name", width=220, anchor="w")
        self.tree.column("price", width=100, anchor="e")
        self.tree.column("cat_id", width=50, stretch=False) # Hide or narrow
        self.tree.column("category", width=150, anchor="w")
        
        # Hide category ID column from view visually
        self.tree["displaycolumns"] = ("id", "name", "price", "category")
        
        sb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        
        self.tree.bind("<<TreeviewSelect>>", self.on_select_item)
        
        # CRUD Form panel on right
        form_frame = tk.LabelFrame(body_frame, text="Product Details Form", font=FONT_BOLD, fg=COLOR_SECONDARY, bg=COLOR_CARD_BG, padx=15, pady=10, borderwidth=1, relief="solid", width=280)
        form_frame.pack(side="right", fill="y")
        form_frame.pack_propagate(False)
        
        lbl_pname = tk.Label(form_frame, text="Product Name *", font=FONT_BOLD, fg=COLOR_TEXT, bg=COLOR_CARD_BG)
        lbl_pname.pack(anchor="w", pady=(2, 1))
        self.entry_name = tk.Entry(form_frame, font=FONT_NORMAL, highlightthickness=1, highlightbackground=COLOR_BORDER, bd=0)
        self.entry_name.pack(fill="x", ipady=4, pady=(0, 6))
        
        lbl_price = tk.Label(form_frame, text="Price ($) *", font=FONT_BOLD, fg=COLOR_TEXT, bg=COLOR_CARD_BG)
        lbl_price.pack(anchor="w", pady=(2, 1))
        self.entry_price = tk.Entry(form_frame, font=FONT_NORMAL, highlightthickness=1, highlightbackground=COLOR_BORDER, bd=0)
        self.entry_price.pack(fill="x", ipady=4, pady=(0, 6))
        
        lbl_cat = tk.Label(form_frame, text="Category Name", font=FONT_BOLD, fg=COLOR_TEXT, bg=COLOR_CARD_BG)
        lbl_cat.pack(anchor="w", pady=(2, 1))
        self.combobox_cat = ttk.Combobox(form_frame, font=FONT_NORMAL, state="readonly")
        self.combobox_cat.pack(fill="x", ipady=3, pady=(0, 8))
        
        # Image Upload
        lbl_img = tk.Label(form_frame, text="Product Image", font=FONT_BOLD, fg=COLOR_TEXT, bg=COLOR_CARD_BG)
        lbl_img.pack(anchor="w", pady=(2, 1))
        
        img_frame = tk.Frame(form_frame, bg=COLOR_CARD_BG)
        img_frame.pack(fill="x", pady=(0, 10))
        
        self.btn_select_image = ttk.Button(img_frame, text="Select Image", command=self.select_image)
        self.btn_select_image.pack(side="left", padx=(0, 10))
        
        self.lbl_image_path = tk.Label(img_frame, text="No image selected", font=FONT_SMALL, fg=COLOR_TEXT_LIGHT, bg=COLOR_CARD_BG)
        self.lbl_image_path.pack(side="left", fill="x", expand=True)
        
        self.selected_image_path = None
        
        # Image Preview Container Frame (height reduced to 100 to show the delete button cleanly)
        self.preview_container = tk.Frame(form_frame, bg=COLOR_CARD_BG, width=240, height=100, highlightbackground=COLOR_BORDER, highlightthickness=1)
        self.preview_container.pack(pady=(0, 8))
        self.preview_container.pack_propagate(False)
        
        self.lbl_preview = tk.Label(self.preview_container, bg=COLOR_CARD_BG, text="[ Image Preview ]", font=FONT_SMALL, fg=COLOR_TEXT_LIGHT)
        self.lbl_preview.pack(fill="both", expand=True)
        self.lbl_preview.bind("<Button-1>", self.open_full_image)
        self.current_preview_filename = None
        
        # Control Buttons
        btn_add = ttk.Button(form_frame, text="➕ Add Product", command=self.add_product, style="Success.TButton")
        btn_add.pack(fill="x", ipady=3, pady=3)
        
        btn_update = ttk.Button(form_frame, text="📝 Update Details", command=self.update_product, style="TButton")
        btn_update.pack(fill="x", ipady=3, pady=3)
        
        btn_delete = ttk.Button(form_frame, text="🗑️ Delete Item", command=self.delete_product, style="Danger.TButton")
        btn_delete.pack(fill="x", ipady=3, pady=3)
        
        # Store categories list mapping
        self.categories_map = {} # Name -> ID
        
        self.load_categories()
        self.load_data()

    def load_categories(self):
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT category_id, category_name FROM categories ORDER BY category_name")
                rows = cursor.fetchall()
                self.categories_map = {row[1]: row[0] for row in rows}
                self.combobox_cat["values"] = list(self.categories_map.keys())
            conn.close()
        except Exception as e:
            print(f"Error loading categories: {e}")

    def load_data(self):
        # Clear Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT p.product_id, p.name, p.price, p.category_id, c.category_name, p.image_url 
                    FROM products p 
                    LEFT JOIN categories c ON p.category_id = c.category_id
                    ORDER BY p.product_id
                """)
                for row in cursor.fetchall():
                    self.tree.insert("", "end", values=(row[0], row[1], f"{row[2]:.2f}", row[3], row[4] or "", row[5] or ""))
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve products from database: {e}")

    def on_select_item(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        vals = self.tree.item(selected[0], "values")
        self.entry_name.delete(0, "end")
        self.entry_name.insert(0, vals[1])
        self.entry_price.delete(0, "end")
        self.entry_price.insert(0, vals[2])
        
        cat_name = vals[4]
        if cat_name in self.categories_map:
            self.combobox_cat.set(cat_name)
        else:
            self.combobox_cat.set("")
            
        # Display existing image preview if present
        img_url = vals[5] if len(vals) > 5 else None
        self.selected_image_path = None
        if img_url:
            self.lbl_image_path.config(text=img_url)
            self.update_image_preview(img_url)
        else:
            self.lbl_image_path.config(text="No image selected")
            self.update_image_preview(None)

    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Product Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")]
        )
        if file_path:
            self.selected_image_path = file_path
            self.lbl_image_path.config(text=os.path.basename(file_path))
            self.update_image_preview(file_path)

    def update_image_preview(self, path_or_filename):
        self.current_preview_filename = path_or_filename
        if not path_or_filename:
            self.lbl_preview.config(image="", text="[ Image Preview ]", cursor="")
            return
            
        if os.path.exists(path_or_filename):
            full_path = path_or_filename
        else:
            upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
            full_path = os.path.join(upload_dir, path_or_filename)
            
        if os.path.exists(full_path):
            try:
                from PIL import Image, ImageTk
                img = Image.open(full_path)
                img.thumbnail((240, 160))
                self.tk_img = ImageTk.PhotoImage(img)
                self.lbl_preview.config(image=self.tk_img, text="", cursor="hand2")
            except Exception:
                try:
                    self.tk_img = tk.PhotoImage(file=full_path)
                    if self.tk_img.width() > 240 or self.tk_img.height() > 160:
                        self.tk_img = self.tk_img.subsample(2, 2)
                    self.lbl_preview.config(image=self.tk_img, text="", cursor="hand2")
                except Exception:
                    self.lbl_preview.config(image="", text="[ Preview Unavailable ]", cursor="")
        else:
            self.lbl_preview.config(image="", text="[ No Image File ]", cursor="")

    def open_full_image(self, event):
        if not self.current_preview_filename:
            return
            
        if os.path.exists(self.current_preview_filename):
            full_path = self.current_preview_filename
        else:
            upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
            full_path = os.path.join(upload_dir, self.current_preview_filename)
            
        if os.path.exists(full_path):
            try:
                img_win = tk.Toplevel(self)
                img_win.title("Full Size Product Image")
                img_win.configure(bg=COLOR_CARD_BG)
                
                from PIL import Image, ImageTk
                img = Image.open(full_path)
                img.thumbnail((600, 600))
                self.full_tk_img = ImageTk.PhotoImage(img)
                
                lbl_full = tk.Label(img_win, image=self.full_tk_img, bg=COLOR_CARD_BG)
                lbl_full.pack(padx=20, pady=20)
                
                lbl_dims = tk.Label(img_win, text=f"Resolution: {img.width}x{img.height} pixels", font=FONT_SMALL, fg=COLOR_TEXT_LIGHT, bg=COLOR_CARD_BG)
                lbl_dims.pack(pady=(0, 15))
                
                img_win.update_idletasks()
                w = img_win.winfo_width()
                h = img_win.winfo_height()
                x = (img_win.winfo_screenwidth() // 2) - (w // 2)
                y = (img_win.winfo_screenheight() // 2) - (h // 2)
                img_win.geometry(f"+{x}+{y}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not load full size image: {e}")

    def add_product(self):
        name = self.entry_name.get().strip()
        price_str = self.entry_price.get().strip()
        cat_name = self.combobox_cat.get()
        
        if not name:
            messagebox.showerror("Validation Error", "Product Name is required.")
            return
        try:
            price = float(price_str)
            if price <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Validation Error", "Price must be a positive number.")
            return
        
        if not cat_name or cat_name not in self.categories_map:
            messagebox.showerror("Validation Error", "Please select a valid category.")
            return
            
        cat_id = self.categories_map[cat_name]
        
        # Handle Image Upload
        image_url = None
        if self.selected_image_path:
            try:
                upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
                os.makedirs(upload_dir, exist_ok=True)
                
                filename = os.path.basename(self.selected_image_path)
                safe_filename = filename.replace(" ", "_").replace("'", "")
                dest_path = os.path.join(upload_dir, safe_filename)
                
                shutil.copy2(self.selected_image_path, dest_path)
                image_url = safe_filename
            except Exception as e:
                messagebox.showwarning("Image Upload Failed", f"Could not save image: {e}")
        
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO products (name, price, category_id, image_url) VALUES (:name, :price, :cat_id, :image_url)",
                               {"name": name, "price": price, "cat_id": cat_id, "image_url": image_url})
                conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Product added successfully!")
            
            # Reset fields
            self.entry_name.delete(0, "end")
            self.entry_price.delete(0, "end")
            self.combobox_cat.set("")
            self.selected_image_path = None
            self.lbl_image_path.config(text="No image selected")
            self.update_image_preview(None)
            
            self.load_data()
            if hasattr(self.controller, 'store_view'):
                self.controller.store_view.load_products()
        except Exception as e:
            if "ORA-00001" in str(e):
                messagebox.showerror("Duplicate Product", f"A product with the name '{name}' already exists. Product names must be unique.")
            else:
                messagebox.showerror("Database Error", f"Could not add product:\n{e}")

    def update_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a product from the table first.")
            return
            
        prod_id = self.tree.item(selected[0], "values")[0]
        name = self.entry_name.get().strip()
        price_str = self.entry_price.get().strip()
        cat_name = self.combobox_cat.get()
        
        if not name:
            messagebox.showerror("Validation Error", "Product Name is required.")
            return
        try:
            price = float(price_str)
            if price <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Validation Error", "Price must be a valid number greater than 0.")
            return
            
        cat_id = self.categories_map.get(cat_name) if cat_name else None
        
        # Handle Image Upload for update
        image_url = None
        if self.selected_image_path:
            try:
                upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
                os.makedirs(upload_dir, exist_ok=True)
                
                filename = os.path.basename(self.selected_image_path)
                safe_filename = filename.replace(" ", "_").replace("'", "")
                dest_path = os.path.join(upload_dir, safe_filename)
                
                shutil.copy2(self.selected_image_path, dest_path)
                image_url = safe_filename
            except Exception as e:
                messagebox.showwarning("Image Upload Failed", f"Could not save image: {e}")
        
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                if image_url:
                    cursor.execute("""
                        UPDATE products 
                        SET name = :name, price = :price, category_id = :cat_id, image_url = :image_url 
                        WHERE product_id = :id
                    """, {"name": name, "price": price, "cat_id": cat_id, "image_url": image_url, "id": prod_id})
                else:
                    cursor.execute("""
                        UPDATE products 
                        SET name = :name, price = :price, category_id = :cat_id 
                        WHERE product_id = :id
                    """, {"name": name, "price": price, "cat_id": cat_id, "id": prod_id})
                conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Product details updated successfully.")
            
            # Reset selection and previews
            self.selected_image_path = None
            self.lbl_image_path.config(text="No image selected")
            self.update_image_preview(None)
            self.load_data()
        except Exception as e:
            if "ORA-00001" in str(e):
                messagebox.showerror("Duplicate Product", f"A product with the name '{name}' already exists. Product names must be unique.")
            else:
                messagebox.showerror("Database Error", f"Could not update product:\n{e}")

    def delete_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a product from the table first.")
            return
            
        vals = self.tree.item(selected[0], "values")
        prod_id, name = vals[0], vals[1]
        
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete product '{name}'?"):
            return
            
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM products WHERE product_id = :id", {"id": prod_id})
                conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Product successfully removed from catalog.")
            self.load_data()
        except Exception as e:
            err_str = str(e)
            if "ORA-02292" in err_str:
                messagebox.showerror("Integrity Error", 
                    f"Could not delete product '{name}':\nThis product is linked to existing customer order history and cannot be deleted to preserve sales records.")
            else:
                messagebox.showerror("Database Error", f"Could not delete product:\n{e}")

    def search_products(self):
        term = self.entry_search.get().strip().lower()
        if not term or term == "search by name/category...":
            self.load_data()
            return
            
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT p.product_id, p.name, p.price, p.category_id, c.category_name, p.image_url 
                    FROM products p 
                    LEFT JOIN categories c ON p.category_id = c.category_id
                    WHERE LOWER(p.name) LIKE :term OR LOWER(c.category_name) LIKE :term
                    ORDER BY p.product_id
                """, {"term": f"%{term}%"})
                for row in cursor.fetchall():
                    self.tree.insert("", "end", values=(row[0], row[1], f"{row[2]:.2f}", row[3], row[4] or "", row[5] or ""))
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not search products:\n{e}")

# --- 3. ADMIN CATEGORIES VIEW ---
class AdminCategoriesView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BACKGROUND)
        self.controller = controller
        
        # Top Bar
        top_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
        top_frame.pack(fill="x", pady=(0, 15))
        
        lbl_title = tk.Label(top_frame, text="Category Management", font=FONT_HEADER, fg=COLOR_SECONDARY, bg=COLOR_BACKGROUND)
        lbl_title.pack(side="left")
        
        btn_refresh = ttk.Button(top_frame, text="🔄 Refresh Table", command=self.load_data, style="TButton")
        btn_refresh.pack(side="right")
        
        # Grid layout
        body_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
        body_frame.pack(fill="both", expand=True)
        
        # Left Treeview
        tree_container = tk.Frame(body_frame, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1)
        tree_container.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        self.tree = ttk.Treeview(tree_container, columns=("id", "name"), show="headings")
        self.tree.heading("id", text="Category ID")
        self.tree.heading("name", text="Category Name")
        self.tree.column("id", width=100, anchor="center")
        self.tree.column("name", width=350, anchor="w")
        
        sb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        
        self.tree.bind("<<TreeviewSelect>>", self.on_select_item)
        
        # Right Form Frame
        form_frame = tk.LabelFrame(body_frame, text="Category Form", font=FONT_BOLD, fg=COLOR_SECONDARY, bg=COLOR_CARD_BG, padx=15, pady=15, borderwidth=1, relief="solid", width=280)
        form_frame.pack(side="right", fill="y")
        form_frame.pack_propagate(False)
        
        lbl_cname = tk.Label(form_frame, text="Category Name *", font=FONT_BOLD, fg=COLOR_TEXT, bg=COLOR_CARD_BG)
        lbl_cname.pack(anchor="w", pady=(5, 2))
        self.entry_name = tk.Entry(form_frame, font=FONT_NORMAL, highlightthickness=1, highlightbackground=COLOR_BORDER, bd=0)
        self.entry_name.pack(fill="x", ipady=5, pady=(0, 20))
        
        btn_add = ttk.Button(form_frame, text="➕ Add Category", command=self.add_category, style="Success.TButton")
        btn_add.pack(fill="x", ipady=4, pady=5)
        
        btn_update = ttk.Button(form_frame, text="📝 Update Category", command=self.update_category, style="TButton")
        btn_update.pack(fill="x", ipady=4, pady=5)
        
        btn_delete = ttk.Button(form_frame, text="🗑️ Delete Category", command=self.delete_category, style="Danger.TButton")
        btn_delete.pack(fill="x", ipady=4, pady=5)
        
        self.load_data()

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT category_id, category_name FROM categories ORDER BY category_id")
                for row in cursor.fetchall():
                    self.tree.insert("", "end", values=(row[0], row[1]))
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load categories: {e}")

    def on_select_item(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        vals = self.tree.item(selected[0], "values")
        self.entry_name.delete(0, "end")
        self.entry_name.insert(0, vals[1])

    def add_category(self):
        name = self.entry_name.get().strip()
        if not name:
            messagebox.showerror("Validation Error", "Category name cannot be empty.")
            return
        if len(name) < 3:
            messagebox.showerror("Validation Error", "Category name must be at least 3 characters.")
            return
            
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO categories (category_name) VALUES (:name)", {"name": name})
                conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"Category '{name}' created.")
            self.load_data()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not save category:\n{e}")

    def update_category(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a category from the table.")
            return
            
        cat_id = self.tree.item(selected[0], "values")[0]
        name = self.entry_name.get().strip()
        
        if not name:
            messagebox.showerror("Validation Error", "Category name cannot be empty.")
            return
        if len(name) < 3:
            messagebox.showerror("Validation Error", "Category name must be at least 3 characters.")
            return
            
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("UPDATE categories SET category_name = :name WHERE category_id = :id",
                               {"name": name, "id": cat_id})
                conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Category updated successfully.")
            self.load_data()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not update category:\n{e}")

    def delete_category(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a category from the table.")
            return
            
        vals = self.tree.item(selected[0], "values")
        cat_id, name = vals[0], vals[1]
        
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete category '{name}'?\nThis will set associated products' category to NULL."):
            return
            
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM categories WHERE category_id = :id", {"id": cat_id})
                conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Category removed.")
            self.load_data()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not delete category:\n{e}")

# --- 4. ADMIN ORDERS VIEW ---
class AdminOrdersView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BACKGROUND)
        self.controller = controller
        
        # Top Bar
        top_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
        top_frame.pack(fill="x", pady=(0, 15))
        
        lbl_title = tk.Label(top_frame, text="Order Tracking Console", font=FONT_HEADER, fg=COLOR_SECONDARY, bg=COLOR_BACKGROUND)
        lbl_title.pack(side="left")
        
        btn_refresh = ttk.Button(top_frame, text="🔄 Refresh", command=self.load_data, style="TButton")
        btn_refresh.pack(side="right")
        
        # Table Layout
        body_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
        body_frame.pack(fill="both", expand=True)
        
        tree_container = tk.Frame(body_frame, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1)
        tree_container.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        # Status Color mapping configuration
        self.tree = ttk.Treeview(tree_container, columns=("id", "uid", "uname", "total", "status", "location"), show="headings")
        self.tree.heading("id", text="Order ID")
        self.tree.heading("uid", text="User ID")
        self.tree.heading("uname", text="Customer Name")
        self.tree.heading("total", text="Total Invoice")
        self.tree.heading("status", text="Order Status")
        self.tree.heading("location", text="Delivery Location")
        
        self.tree.column("id", width=80, anchor="center")
        self.tree.column("uid", width=80, anchor="center")
        self.tree.column("uname", width=180, anchor="w")
        self.tree.column("total", width=100, anchor="e")
        self.tree.column("status", width=100, anchor="center")
        self.tree.column("location", width=220, anchor="w")
        
        # Tree tags for status coloration
        self.tree.tag_configure('Pending', foreground=COLOR_WARNING, font=FONT_BOLD)
        self.tree.tag_configure('Completed', foreground=COLOR_SUCCESS, font=FONT_BOLD)
        self.tree.tag_configure('Cancelled', foreground=COLOR_DANGER, font=FONT_BOLD)
        self.tree.tag_configure('Shipped', foreground=COLOR_PRIMARY, font=FONT_BOLD)
        self.tree.tag_configure('Delivered', foreground="#a855f7", font=FONT_BOLD)
        
        sb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        
        self.tree.bind("<<TreeviewSelect>>", self.on_select_item)
        
        # Right Form
        form_frame = tk.LabelFrame(body_frame, text="Update Status Panel", font=FONT_BOLD, fg=COLOR_SECONDARY, bg=COLOR_CARD_BG, padx=15, pady=15, borderwidth=1, relief="solid", width=280)
        form_frame.pack(side="right", fill="y")
        form_frame.pack_propagate(False)
        
        lbl_order_id_lbl = tk.Label(form_frame, text="Selected Order:", font=FONT_NORMAL, fg=COLOR_TEXT_LIGHT, bg=COLOR_CARD_BG)
        lbl_order_id_lbl.pack(anchor="w", pady=(5, 2))
        self.lbl_selected_order = tk.Label(form_frame, text="None Selected", font=FONT_TITLE, fg=COLOR_PRIMARY, bg=COLOR_CARD_BG)
        self.lbl_selected_order.pack(anchor="w", pady=(0, 10))
        
        # Shipping Location Label
        lbl_addr_title = tk.Label(form_frame, text="Shipping Location:", font=FONT_NORMAL, fg=COLOR_TEXT_LIGHT, bg=COLOR_CARD_BG)
        lbl_addr_title.pack(anchor="w", pady=(5, 2))
        self.lbl_address = tk.Label(form_frame, text="None Selected", font=FONT_BOLD, fg=COLOR_TEXT, bg=COLOR_CARD_BG, justify="left", wraplength=230)
        self.lbl_address.pack(anchor="w", pady=(0, 15))
        
        lbl_status = tk.Label(form_frame, text="Set Order Status *", font=FONT_BOLD, fg=COLOR_TEXT, bg=COLOR_CARD_BG)
        lbl_status.pack(anchor="w", pady=(5, 2))
        
        self.combobox_status = ttk.Combobox(form_frame, font=FONT_NORMAL, values=["Pending", "Completed", "Cancelled", "Shipped", "Delivered"], state="readonly")
        self.combobox_status.pack(fill="x", ipady=3, pady=(0, 20))
        
        btn_update = ttk.Button(form_frame, text="💾 Update Status", command=self.update_order_status, style="TButton")
        btn_update.pack(fill="x", ipady=5)
        
        lbl_trigger_note = tk.Label(form_frame, text="📝 Note: Changing status updates the tracking ledger and logs history into the Audit Log table.", font=FONT_SMALL, fg=COLOR_TEXT_LIGHT, bg=COLOR_CARD_BG, justify="left", wraplength=230)
        lbl_trigger_note.pack(side="bottom", pady=10)
        
        self.load_data()

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT o.order_id, o.user_id, u.name, o.total_amount, o.status, o.shipping_address 
                    FROM orders o 
                    JOIN users u ON o.user_id = u.user_id 
                    ORDER BY o.order_id DESC
                """)
                for row in cursor.fetchall():
                    self.tree.insert("", "end", values=(row[0], row[1], row[2], f"${row[3]:.2f}", row[4], row[5] or "No address"), tags=(row[4],))
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve orders: {e}")

    def on_select_item(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        vals = self.tree.item(selected[0], "values")
        self.lbl_selected_order.config(text=f"Order #{vals[0]} (Client: {vals[2]})")
        self.combobox_status.set(vals[4])
        
        # Load shipping location dynamically
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT shipping_address FROM orders WHERE order_id = :oid", {"oid": int(vals[0])})
                row = cursor.fetchone()
                addr = row[0] if row and row[0] else "No address provided"
                self.lbl_address.config(text=addr)
            conn.close()
        except Exception as e:
            print(f"Error loading order address: {e}")

    def update_order_status(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select an order from the table.")
            return
            
        order_id = self.tree.item(selected[0], "values")[0]
        status = self.combobox_status.get()
        
        if not status:
            messagebox.showerror("Validation Error", "Please select a valid order status.")
            return
            
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                # Update status
                cursor.execute("UPDATE orders SET status = :status WHERE order_id = :id",
                               {"status": status, "id": order_id})
                conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"Order #{order_id} status updated to '{status}'. Trigger logged transaction history.")
            self.load_data()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not update status:\n{e}")

# --- 5. ADMIN PAYMENTS VIEW ---
class AdminPaymentsView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BACKGROUND)
        self.controller = controller
        
        top_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
        top_frame.pack(fill="x", pady=(0, 15))
        
        lbl_title = tk.Label(top_frame, text="Payment Settlements View", font=FONT_HEADER, fg=COLOR_SECONDARY, bg=COLOR_BACKGROUND)
        lbl_title.pack(side="left")
        
        btn_refresh = ttk.Button(top_frame, text="🔄 Refresh", command=self.load_data, style="TButton")
        btn_refresh.pack(side="right")
        
        # Table
        tree_container = tk.Frame(self, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1)
        tree_container.pack(fill="both", expand=True)
        
        self.tree = ttk.Treeview(tree_container, columns=("id", "oid", "amt", "uname", "location"), show="headings")
        self.tree.heading("id", text="Payment ID")
        self.tree.heading("oid", text="Order Reference ID")
        self.tree.heading("amt", text="Amount Paid")
        self.tree.heading("uname", text="Client Name")
        self.tree.heading("location", text="Shipping Location")
        
        self.tree.column("id", width=100, anchor="center")
        self.tree.column("oid", width=120, anchor="center")
        self.tree.column("amt", width=120, anchor="e")
        self.tree.column("uname", width=200, anchor="w")
        self.tree.column("location", width=250, anchor="w")
        
        sb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        
        self.load_data()

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT p.payment_id, p.order_id, p.amount, u.name, o.shipping_address 
                    FROM payments p 
                    JOIN orders o ON p.order_id = o.order_id 
                    JOIN users u ON o.user_id = u.user_id 
                    ORDER BY p.payment_id DESC
                """)
                for row in cursor.fetchall():
                    self.tree.insert("", "end", values=(row[0], row[1], f"${row[2]:.2f}", row[3], row[4] or "No address"))
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve payments: {e}")

# --- 6. ADMIN USERS VIEW ---
class AdminUsersView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BACKGROUND)
        self.controller = controller
        
        top_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
        top_frame.pack(fill="x", pady=(0, 15))
        
        lbl_title = tk.Label(top_frame, text="Accounts & System Users", font=FONT_HEADER, fg=COLOR_SECONDARY, bg=COLOR_BACKGROUND)
        lbl_title.pack(side="left")
        
        # Search Box
        search_frame = tk.Frame(top_frame, bg=COLOR_BACKGROUND)
        search_frame.pack(side="right")
        self.entry_search = tk.Entry(search_frame, font=FONT_NORMAL, width=25, highlightthickness=1, highlightbackground=COLOR_BORDER, bd=0)
        self.entry_search.pack(side="left", ipady=5, padx=5)
        self.entry_search.insert(0, "Search name/email...")
        self.entry_search.bind("<FocusIn>", lambda e: self.entry_search.delete(0, 'end') if self.entry_search.get() == "Search name/email..." else None)
        
        btn_search = ttk.Button(search_frame, text="🔍 Search", command=self.search_users, style="TButton")
        btn_search.pack(side="left")
        
        btn_refresh = ttk.Button(search_frame, text="🔄 Refresh", command=self.load_data, style="TButton")
        btn_refresh.pack(side="left", padx=5)
        
        # Grid containing Treeview and controls
        body_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
        body_frame.pack(fill="both", expand=True)
        
        tree_container = tk.Frame(body_frame, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1)
        tree_container.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        self.tree = ttk.Treeview(tree_container, columns=("id", "name", "email", "role"), show="headings")
        self.tree.heading("id", text="User ID")
        self.tree.heading("name", text="Full Name")
        self.tree.heading("email", text="Email Address")
        self.tree.heading("role", text="System Role")
        
        self.tree.column("id", width=80, anchor="center")
        self.tree.column("name", width=200, anchor="w")
        self.tree.column("email", width=250, anchor="w")
        self.tree.column("role", width=120, anchor="center")
        
        sb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        
        self.tree.bind("<<TreeviewSelect>>", self.on_select_user)
        
        # Controls Form
        form_frame = tk.LabelFrame(body_frame, text="User Management Controls", font=FONT_BOLD, fg=COLOR_SECONDARY, bg=COLOR_CARD_BG, padx=15, pady=10, borderwidth=1, relief="solid", width=280)
        form_frame.pack(side="right", fill="y")
        form_frame.pack_propagate(False)
        
        lbl_sec_details = tk.Label(form_frame, text="Modify User Account Details", font=FONT_BOLD, fg=COLOR_SECONDARY, bg=COLOR_CARD_BG)
        lbl_sec_details.pack(anchor="w", pady=(5, 5))
        
        lbl_name = tk.Label(form_frame, text="Full Name *", font=FONT_BOLD, fg=COLOR_TEXT, bg=COLOR_CARD_BG)
        lbl_name.pack(anchor="w", pady=(2, 1))
        self.entry_name = tk.Entry(form_frame, font=FONT_NORMAL, highlightthickness=1, highlightbackground=COLOR_BORDER, bd=0)
        self.entry_name.pack(fill="x", ipady=4, pady=(0, 8))
        
        lbl_email = tk.Label(form_frame, text="Email Address *", font=FONT_BOLD, fg=COLOR_TEXT, bg=COLOR_CARD_BG)
        lbl_email.pack(anchor="w", pady=(2, 1))
        self.entry_email = tk.Entry(form_frame, font=FONT_NORMAL, highlightthickness=1, highlightbackground=COLOR_BORDER, bd=0)
        self.entry_email.pack(fill="x", ipady=4, pady=(0, 8))
        
        lbl_pass = tk.Label(form_frame, text="New Password (blank to keep)", font=FONT_BOLD, fg=COLOR_TEXT, bg=COLOR_CARD_BG)
        lbl_pass.pack(anchor="w", pady=(2, 1))
        self.entry_password = tk.Entry(form_frame, font=FONT_NORMAL, show="*", highlightthickness=1, highlightbackground=COLOR_BORDER, bd=0)
        self.entry_password.pack(fill="x", ipady=4, pady=(0, 10))
        
        btn_update_details = ttk.Button(form_frame, text="📝 Update User Details", command=self.update_user_details, style="TButton")
        btn_update_details.pack(fill="x", ipady=4, pady=(0, 15))
        
        # Horizontal Divider Line
        divider = tk.Frame(form_frame, height=1, bg=COLOR_BORDER)
        divider.pack(fill="x", pady=(0, 15))
        
        # Role Modification Area
        lbl_role = tk.Label(form_frame, text="Modify System Role *", font=FONT_BOLD, fg=COLOR_TEXT, bg=COLOR_CARD_BG)
        lbl_role.pack(anchor="w", pady=(0, 2))
        
        self.combobox_role = ttk.Combobox(form_frame, values=["admin", "customer"], state="readonly", font=FONT_NORMAL)
        self.combobox_role.pack(fill="x", pady=(0, 10))
        self.combobox_role.set("customer")
        
        btn_update_role = ttk.Button(form_frame, text="🛡️ Update System Role", command=self.update_user_role, style="TButton")
        btn_update_role.pack(fill="x", ipady=4, pady=(0, 15))
        
        btn_delete = ttk.Button(form_frame, text="🗑️ Delete User Account", command=self.delete_user, style="Danger.TButton")
        btn_delete.pack(fill="x", ipady=4)
        
        self.selected_user_id = None
        self.load_data()

    def on_select_user(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        vals = self.tree.item(selected[0], "values")
        self.selected_user_id = int(vals[0])
        
        # Load values into details inputs
        self.entry_name.delete(0, "end")
        self.entry_name.insert(0, vals[1])
        
        self.entry_email.delete(0, "end")
        self.entry_email.insert(0, vals[2])
        
        self.entry_password.delete(0, "end")
        self.combobox_role.set(vals[3])

    def update_user_details(self):
        if not self.selected_user_id:
            messagebox.showwarning("Selection Required", "Please select a user account to modify.")
            return
            
        name = self.entry_name.get().strip()
        email = self.entry_email.get().strip()
        password = self.entry_password.get().strip()
        
        if not name or not email:
            messagebox.showerror("Validation Error", "Full Name and Email Address cannot be empty.")
            return
            
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            messagebox.showerror("Validation Error", "Please enter a valid email format.")
            return
            
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                # Check for duplicate email under other users
                cursor.execute("SELECT COUNT(*) FROM users WHERE email = :p_email AND user_id != :p_uid", {"p_email": email, "p_uid": self.selected_user_id})
                if cursor.fetchone()[0] > 0:
                    messagebox.showerror("Validation Error", "A user account with this email address already exists.")
                    conn.close()
                    return
                
                if password:
                    hashed_pwd = generate_password_hash(password)
                    cursor.execute("""
                        UPDATE users 
                        SET name = :p_name, email = :p_email, password = :p_password 
                        WHERE user_id = :p_uid
                    """, {"p_name": name, "p_email": email, "p_password": hashed_pwd, "p_uid": self.selected_user_id})
                else:
                    cursor.execute("""
                        UPDATE users 
                        SET name = :p_name, email = :p_email 
                        WHERE user_id = :p_uid
                    """, {"p_name": name, "p_email": email, "p_uid": self.selected_user_id})
                
                conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"Account details for '{name}' successfully updated!")
            
            # If current logged in user updated their own name/email, update local session
            if self.selected_user_id == self.controller.app.current_user["user_id"]:
                self.controller.app.current_user["name"] = name
                self.controller.app.current_user["email"] = email
                self.controller.app.title(f"CARFOON online shopping - Admin Console ({name})")
            
            self.load_data()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update user details:\n{e}")

    def update_user_role(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a user account to modify.")
            return
            
        vals = self.tree.item(selected[0], "values")
        user_id, name, email, current_role = vals[0], vals[1], vals[2], vals[3]
        new_role = self.combobox_role.get()
        
        # Enforce Rule: Only admin@gmail.com can edit roles
        logged_in_email = self.controller.app.current_user["email"]
        if logged_in_email != "admin@gmail.com":
            messagebox.showerror("Access Denied", "Only the primary administrator ('admin@gmail.com') is authorized to update system roles.")
            return
            
        # Enforce Rule: admin@gmail.com role is not editable
        if email == "admin@gmail.com":
            messagebox.showerror("Access Denied", "The primary administrator account 'admin@gmail.com' cannot have its system role modified.")
            return
            
        if current_role == new_role:
            messagebox.showinfo("No Change", f"User '{name}' is already assigned the '{new_role}' role.")
            return
            
        is_self = int(user_id) == self.controller.app.current_user["user_id"]
        if is_self and new_role == "customer":
            if not messagebox.askyesno("Confirm Self-Demotion", 
                "Changing your own role to 'customer' will log you out of the Admin Console.\nAre you sure you want to demote yourself?"):
                return
                
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE users 
                    SET role = :role 
                    WHERE user_id = :user_id
                """, {"role": new_role, "user_id": int(user_id)})
                conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"System role for '{name}' successfully updated to '{new_role}'!")
            
            if is_self and new_role == "customer":
                self.controller.app.logout_user()
            else:
                self.load_data()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update user role:\n{e}")

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT user_id, name, email, role FROM users ORDER BY user_id")
                for row in cursor.fetchall():
                    self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3]))
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve users: {e}")

    def delete_user(self):
        # Enforce Rule: Only the primary admin@gmail.com is allowed to delete users
        logged_in_email = self.controller.app.current_user["email"]
        if logged_in_email != "admin@gmail.com":
            messagebox.showerror("Access Denied", "Only the primary administrator ('admin@gmail.com') is authorized to delete user accounts.")
            return

        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a user account to delete.")
            return
            
        vals = self.tree.item(selected[0], "values")
        user_id, name, email = vals[0], vals[1], vals[2]
        
        if int(user_id) == self.controller.app.current_user["user_id"]:
            messagebox.showerror("Action Denied", "You cannot delete your own active administrative session.")
            return
            
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to permanently delete user account '{name}'?"):
            return
            
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                # 1. Fetch all orders belonging to this user
                cursor.execute("SELECT order_id FROM orders WHERE user_id = :p_uid", {"p_uid": int(user_id)})
                order_ids = [row[0] for row in cursor.fetchall()]
                
                # 2. Delete child records for each order
                for oid in order_ids:
                    cursor.execute("DELETE FROM order_audit_logs WHERE order_id = :p_oid", {"p_oid": oid})
                    cursor.execute("DELETE FROM payments WHERE order_id = :p_oid", {"p_oid": oid})
                    cursor.execute("DELETE FROM order_items WHERE order_id = :p_oid", {"p_oid": oid})
                
                # 3. Delete parent orders
                if order_ids:
                    cursor.execute("DELETE FROM orders WHERE user_id = :p_uid", {"p_uid": int(user_id)})
                
                # 4. Fetch and delete cart and cart items
                cursor.execute("SELECT cart_id FROM cart WHERE user_id = :p_uid", {"p_uid": int(user_id)})
                cart_row = cursor.fetchone()
                if cart_row:
                    cart_id = cart_row[0]
                    cursor.execute("DELETE FROM cart_items WHERE cart_id = :p_cid", {"p_cid": cart_id})
                    cursor.execute("DELETE FROM cart WHERE user_id = :p_uid", {"p_uid": int(user_id)})
                
                # 5. Finally delete the user record itself
                cursor.execute("DELETE FROM users WHERE user_id = :p_uid", {"p_uid": int(user_id)})
                conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"User account '{name}' and all associated transactions successfully deleted.")
            self.load_data()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not delete user account:\n{e}")

    def search_users(self):
        term = self.entry_search.get().strip().lower()
        if not term or term == "search name/email...":
            self.load_data()
            return
            
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT user_id, name, email, role FROM users 
                    WHERE LOWER(name) LIKE :term OR LOWER(email) LIKE :term
                    ORDER BY user_id
                """, {"term": f"%{term}%"})
                for row in cursor.fetchall():
                    self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3]))
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not search users:\n{e}")

# --- 7. ADMIN AUDIT LOGS VIEW ---
class AdminAuditLogsView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BACKGROUND)
        self.controller = controller
        
        top_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
        top_frame.pack(fill="x", pady=(0, 15))
        
        lbl_title = tk.Label(top_frame, text="Oracle Trigger Audit Logs", font=FONT_HEADER, fg=COLOR_SECONDARY, bg=COLOR_BACKGROUND)
        lbl_title.pack(side="left")
        
        btn_refresh = ttk.Button(top_frame, text="🔄 Refresh Logs", command=self.load_data, style="TButton")
        btn_refresh.pack(side="right")
        
        # Table Frame
        tree_container = tk.Frame(self, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1)
        tree_container.pack(fill="both", expand=True)
        
        self.tree = ttk.Treeview(tree_container, columns=("id", "oid", "old", "new", "time"), show="headings")
        self.tree.heading("id", text="Log ID")
        self.tree.heading("oid", text="Order Reference ID")
        self.tree.heading("old", text="Previous Status")
        self.tree.heading("new", text="Updated Status")
        self.tree.heading("time", text="Timestamp (Changed At)")
        
        self.tree.column("id", width=100, anchor="center")
        self.tree.column("oid", width=150, anchor="center")
        self.tree.column("old", width=180, anchor="w")
        self.tree.column("new", width=180, anchor="w")
        self.tree.column("time", width=220, anchor="center")
        
        sb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        
        self.load_data()

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT log_id, order_id, old_status, new_status, 
                           TO_CHAR(changed_at, 'YYYY-MM-DD HH24:MI:SS') 
                    FROM order_audit_logs 
                    ORDER BY log_id DESC
                """)
                for row in cursor.fetchall():
                    self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4]))
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve audit log details: {e}")

# ==============================================================================
# CUSTOMER DASHBOARD COMPONENT
# ==============================================================================
class CustomerDashboard(BaseDashboard):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Cart ID for currently active user
        self.cart_id = None
        self.load_or_create_cart()
        
        # Customer menu items
        self.add_menu_item("Shop Catalog", "🛍️", CustomerCatalogView)
        self.add_menu_item("My Shopping Cart", "🛒", CustomerCartView)
        self.add_menu_item("My Orders & Payments", "📦", CustomerOrdersView)
        
        # Default view
        self.switch_view("Shop Catalog", CustomerCatalogView)

    def load_or_create_cart(self):
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                user_id = self.app.current_user["user_id"]
                # Query cart ID
                cursor.execute("SELECT cart_id FROM cart WHERE user_id = :user_id", {"user_id": user_id})
                row = cursor.fetchone()
                if row:
                    self.cart_id = row[0]
                else:
                    # Create cart
                    cart_id_var = cursor.var(oracledb.NUMBER)
                    cursor.execute(
                        "INSERT INTO cart (user_id) VALUES (:user_id) RETURNING cart_id INTO :cart_id",
                        {"user_id": user_id, "cart_id": cart_id_var}
                    )
                    self.cart_id = int(cart_id_var.getvalue()[0])
                    conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error loading client cart: {e}")

# --- 1. CUSTOMER CATALOG VIEW ---
class CustomerCatalogView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BACKGROUND)
        self.controller = controller
        
        # Top Bar
        top_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
        top_frame.pack(fill="x", pady=(0, 15))
        
        lbl_title = tk.Label(top_frame, text="Product Catalog Storefront", font=FONT_HEADER, fg=COLOR_SECONDARY, bg=COLOR_BACKGROUND)
        lbl_title.pack(side="left")
        
        # Filtering controls
        filters_frame = tk.Frame(top_frame, bg=COLOR_BACKGROUND)
        filters_frame.pack(side="right")
        
        lbl_filter = tk.Label(filters_frame, text="Filter Category:", font=FONT_BOLD, fg=COLOR_TEXT, bg=COLOR_BACKGROUND)
        lbl_filter.pack(side="left", padx=5)
        
        self.combobox_cat = ttk.Combobox(filters_frame, font=FONT_NORMAL, state="readonly", width=18)
        self.combobox_cat.pack(side="left", padx=5)
        self.combobox_cat.bind("<<ComboboxSelected>>", self.filter_products)
        
        self.entry_search = tk.Entry(filters_frame, font=FONT_NORMAL, width=20, highlightthickness=1, highlightbackground=COLOR_BORDER, bd=0)
        self.entry_search.pack(side="left", ipady=5, padx=5)
        self.entry_search.insert(0, "Search products...")
        self.entry_search.bind("<FocusIn>", lambda e: self.entry_search.delete(0, 'end') if self.entry_search.get() == "Search products..." else None)
        
        btn_search = ttk.Button(filters_frame, text="🔍", command=self.search_products, style="TButton")
        btn_search.pack(side="left")
        
        btn_clear = ttk.Button(filters_frame, text="Reset", command=self.reset_filters, style="TButton")
        btn_clear.pack(side="left", padx=5)
        
        # Layout: Treeview left, details add cart frame on right
        body_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
        body_frame.pack(fill="both", expand=True)
        
        tree_container = tk.Frame(body_frame, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1)
        tree_container.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        # Configure Storefront Treeview style for taller rows
        style = ttk.Style()
        style.configure("Storefront.Treeview", 
                        background=COLOR_CARD_BG, 
                        foreground=COLOR_TEXT,
                        fieldbackground=COLOR_CARD_BG, 
                        rowheight=48,
                        font=FONT_NORMAL)
        style.map("Storefront.Treeview", background=[('selected', COLOR_PRIMARY)])
        
        self.tree = ttk.Treeview(tree_container, columns=("id", "name", "price", "cat", "image_url"), show="tree headings", style="Storefront.Treeview")
        self.tree.heading("#0", text="Image", anchor="center")
        self.tree.heading("id", text="Product ID")
        self.tree.heading("name", text="Product Name")
        self.tree.heading("price", text="Price")
        self.tree.heading("cat", text="Category")
        self.tree.heading("image_url", text="Image URL")
        
        self.tree.column("#0", width=60, anchor="center")
        self.tree.column("id", width=80, anchor="center")
        self.tree.column("name", width=230, anchor="w")
        self.tree.column("price", width=100, anchor="e")
        self.tree.column("cat", width=130, anchor="w")
        self.tree.column("image_url", width=50, stretch=False)
        
        # Hide image_url column from view visually
        self.tree["displaycolumns"] = ("id", "name", "price", "cat")
        
        sb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        
        self.tree.bind("<<TreeviewSelect>>", self.on_select_item)
        
        self.placeholder_img = tk.PhotoImage(width=40, height=40)
        self.placeholder_img.put("#f1f5f9", to=(0, 0, 40, 40))
        self.product_images_cache = {}
        
        # Side Order Add Form
        order_frame = tk.LabelFrame(body_frame, text="Add to Cart Panel", font=FONT_BOLD, fg=COLOR_SECONDARY, bg=COLOR_CARD_BG, padx=15, pady=15, borderwidth=1, relief="solid", width=280)
        order_frame.pack(side="right", fill="y")
        order_frame.pack_propagate(False)
        
        lbl_pname = tk.Label(order_frame, text="Selected Product:", font=FONT_NORMAL, fg=COLOR_TEXT_LIGHT, bg=COLOR_CARD_BG)
        lbl_pname.pack(anchor="w", pady=(5, 2))
        self.lbl_selected_p = tk.Label(order_frame, text="None Selected", font=FONT_TITLE, fg=COLOR_PRIMARY, bg=COLOR_CARD_BG, wraplength=230, justify="left")
        self.lbl_selected_p.pack(anchor="w", pady=(0, 15))
        
        # Image Preview Container Frame to ensure a fixed layout box
        self.preview_container = tk.Frame(order_frame, bg=COLOR_CARD_BG, width=240, height=160, highlightbackground=COLOR_BORDER, highlightthickness=1)
        self.preview_container.pack(pady=(0, 15))
        self.preview_container.pack_propagate(False)
        
        self.lbl_preview = tk.Label(self.preview_container, bg=COLOR_CARD_BG, text="[ Image Preview ]", font=FONT_SMALL, fg=COLOR_TEXT_LIGHT)
        self.lbl_preview.pack(fill="both", expand=True)
        self.lbl_preview.bind("<Button-1>", self.open_full_image)
        self.current_preview_filename = None
        
        lbl_qty = tk.Label(order_frame, text="Purchase Quantity *", font=FONT_BOLD, fg=COLOR_TEXT, bg=COLOR_CARD_BG)
        lbl_qty.pack(anchor="w", pady=(5, 2))
        self.spinbox_qty = tk.Spinbox(order_frame, from_=1, to=99, font=FONT_NORMAL, width=10, bd=1, relief="solid")
        self.spinbox_qty.pack(anchor="w", ipady=4, pady=(0, 25))
        
        btn_add = ttk.Button(order_frame, text="🛒 Add Item to Cart", command=self.add_item_to_cart, style="Success.TButton")
        btn_add.pack(fill="x", ipady=5)
        
        lbl_pkg_note = tk.Label(order_frame, text="🔌 Package Integration: Item inserts invoke 'pkg_order_management.add_item_to_cart' PL/SQL procedure natively inside Oracle.", font=FONT_SMALL, fg=COLOR_TEXT_LIGHT, bg=COLOR_CARD_BG, justify="left", wraplength=230)
        lbl_pkg_note.pack(side="bottom", pady=10)
        
        # Setup data mappings
        self.categories_map = {}
        self.selected_product_id = None
        
        self.load_categories()
        self.load_products()

    def load_categories(self):
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT category_id, category_name FROM categories ORDER BY category_name")
                rows = cursor.fetchall()
                self.categories_map = {row[1]: row[0] for row in rows}
                self.combobox_cat["values"] = ["All Categories"] + list(self.categories_map.keys())
                self.combobox_cat.set("All Categories")
            conn.close()
        except Exception as e:
            print(f"Error loading categories: {e}")

    def get_thumbnail(self, filename):
        if not filename:
            return self.placeholder_img
            
        if filename in self.product_images_cache:
            return self.product_images_cache[filename]
            
        upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
        full_path = os.path.join(upload_dir, filename)
        
        if os.path.exists(full_path):
            try:
                from PIL import Image, ImageTk
                img = Image.open(full_path)
                img = img.resize((40, 40), Image.Resampling.LANCZOS)
                tk_img = ImageTk.PhotoImage(img)
                self.product_images_cache[filename] = tk_img
                return tk_img
            except Exception:
                try:
                    tk_img = tk.PhotoImage(file=full_path)
                    w = tk_img.width()
                    h = tk_img.height()
                    factor = max(1, w // 40, h // 40)
                    if factor > 1:
                        tk_img = tk_img.subsample(factor, factor)
                    self.product_images_cache[filename] = tk_img
                    return tk_img
                except Exception:
                    return self.placeholder_img
        else:
            return self.placeholder_img

    def load_products(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT p.product_id, p.name, p.price, c.category_name, p.image_url 
                    FROM products p 
                    LEFT JOIN categories c ON p.category_id = c.category_id
                    ORDER BY p.product_id
                """)
                for row in cursor.fetchall():
                    tk_img = self.get_thumbnail(row[4])
                    self.tree.insert("", "end", image=tk_img, values=(row[0], row[1], f"${row[2]:.2f}", row[3] or "", row[4] or ""))
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve catalog: {e}")

    def on_select_item(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        vals = self.tree.item(selected[0], "values")
        self.selected_product_id = vals[0]
        self.lbl_selected_p.config(text=f"{vals[1]}\n(Price: {vals[2]})")
        
        # Display image preview
        img_url = vals[4] if len(vals) > 4 else None
        self.update_image_preview(img_url)

    def update_image_preview(self, filename):
        self.current_preview_filename = filename
        if not filename:
            self.lbl_preview.config(image="", text="[ Image Preview ]", cursor="")
            return
            
        upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
        full_path = os.path.join(upload_dir, filename)
        
        if os.path.exists(full_path):
            try:
                from PIL import Image, ImageTk
                img = Image.open(full_path)
                img.thumbnail((240, 160))
                self.tk_img = ImageTk.PhotoImage(img)
                self.lbl_preview.config(image=self.tk_img, text="", cursor="hand2")
            except Exception:
                try:
                    self.tk_img = tk.PhotoImage(file=full_path)
                    if self.tk_img.width() > 240 or self.tk_img.height() > 160:
                        self.tk_img = self.tk_img.subsample(2, 2)
                    self.lbl_preview.config(image=self.tk_img, text="", cursor="hand2")
                except Exception:
                    self.lbl_preview.config(image="", text="[ Preview Unavailable ]", cursor="")
        else:
            self.lbl_preview.config(image="", text="[ No Image File ]", cursor="")

    def open_full_image(self, event):
        if not self.current_preview_filename:
            return
            
        upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
        full_path = os.path.join(upload_dir, self.current_preview_filename)
        
        if os.path.exists(full_path):
            try:
                img_win = tk.Toplevel(self)
                img_win.title("Full Size Product Image")
                img_win.configure(bg=COLOR_CARD_BG)
                
                from PIL import Image, ImageTk
                img = Image.open(full_path)
                img.thumbnail((600, 600))
                self.full_tk_img = ImageTk.PhotoImage(img)
                
                lbl_full = tk.Label(img_win, image=self.full_tk_img, bg=COLOR_CARD_BG)
                lbl_full.pack(padx=20, pady=20)
                
                lbl_dims = tk.Label(img_win, text=f"Resolution: {img.width}x{img.height} pixels", font=FONT_SMALL, fg=COLOR_TEXT_LIGHT, bg=COLOR_CARD_BG)
                lbl_dims.pack(pady=(0, 15))
                
                img_win.update_idletasks()
                w = img_win.winfo_width()
                h = img_win.winfo_height()
                x = (img_win.winfo_screenwidth() // 2) - (w // 2)
                y = (img_win.winfo_screenheight() // 2) - (h // 2)
                img_win.geometry(f"+{x}+{y}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not load full size image: {e}")

    def add_item_to_cart(self):
        if not self.selected_product_id:
            messagebox.showwarning("Selection Required", "Please select a product from the catalog.")
            return
            
        qty_str = self.spinbox_qty.get()
        try:
            qty = int(qty_str)
            if qty <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Validation Error", "Quantity must be a valid integer greater than 0.")
            return
            
        cart_id = self.controller.cart_id
        
        # Invoke PL/SQL package procedure pkg_order_management.add_item_to_cart(p_cart_id, p_product_id, p_quantity)
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                # Call stored procedure
                cursor.callproc("pkg_order_management.add_item_to_cart", [cart_id, int(self.selected_product_id), qty])
                conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Item successfully added to cart via PL/SQL package!")
        except oracledb.DatabaseError as db_err:
            error_obj, = db_err.args
            messagebox.showerror("Database Error", f"PL/SQL Package raised an exception:\n{error_obj.message}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not add item to cart:\n{e}")

    def filter_products(self, event):
        cat_name = self.combobox_cat.get()
        if cat_name == "All Categories" or not cat_name:
            self.load_products()
            return
            
        cat_id = self.categories_map.get(cat_name)
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT p.product_id, p.name, p.price, c.category_name, p.image_url 
                    FROM products p 
                    LEFT JOIN categories c ON p.category_id = c.category_id
                    WHERE p.category_id = :cat_id
                    ORDER BY p.product_id
                """, {"cat_id": cat_id})
                for row in cursor.fetchall():
                    tk_img = self.get_thumbnail(row[4])
                    self.tree.insert("", "end", image=tk_img, values=(row[0], row[1], f"${row[2]:.2f}", row[3] or "", row[4] or ""))
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not filter products:\n{e}")

    def search_products(self):
        term = self.entry_search.get().strip().lower()
        if not term or term == "search products...":
            self.load_products()
            return
            
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT p.product_id, p.name, p.price, c.category_name, p.image_url 
                    FROM products p 
                    LEFT JOIN categories c ON p.category_id = c.category_id
                    WHERE LOWER(p.name) LIKE :term
                    ORDER BY p.product_id
                """, {"term": f"%{term}%"})
                for row in cursor.fetchall():
                    tk_img = self.get_thumbnail(row[4])
                    self.tree.insert("", "end", image=tk_img, values=(row[0], row[1], f"${row[2]:.2f}", row[3] or "", row[4] or ""))
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not search products:\n{e}")

    def reset_filters(self):
        self.combobox_cat.set("All Categories")
        self.entry_search.delete(0, "end")
        self.entry_search.insert(0, "Search products...")
        self.update_image_preview(None)
        self.load_products()

def show_receipt_window(parent, order_id, total_amount, items):
    receipt_win = tk.Toplevel(parent)
    receipt_win.title("Payment Receipt")
    receipt_win.geometry("380x560")
    receipt_win.resizable(False, False)
    receipt_win.configure(bg="#ffffff")
    receipt_win.grab_set() # Block interaction with parent window until closed
    
    # Outer border frame
    outer_frame = tk.Frame(receipt_win, bg="#ffffff", bd=2, relief="solid")
    outer_frame.pack(fill="both", expand=True, padx=15, pady=15)
    
    # Store Header
    lbl_store = tk.Label(outer_frame, text="CARFOON SHOPPING", font=("Courier New", 13, "bold"), fg="#000000", bg="#ffffff")
    lbl_store.pack(pady=(15, 2))
    
    lbl_loc = tk.Label(outer_frame, text="Mogadishu, Somalia\nTell:636279489", font=("Courier New", 8), fg="#000000", bg="#ffffff")
    lbl_loc.pack(pady=2)
    
    lbl_sep1 = tk.Label(outer_frame, text="----------------------------------", font=("Courier New", 9), fg="#000000", bg="#ffffff")
    lbl_sep1.pack()
    
    lbl_title = tk.Label(outer_frame, text="PAYMENT RECEIPT", font=("Courier New", 10, "bold"), fg="#000000", bg="#ffffff")
    lbl_title.pack(pady=2)
    
    lbl_sep2 = tk.Label(outer_frame, text="----------------------------------", font=("Courier New", 9), fg="#000000", bg="#ffffff")
    lbl_sep2.pack()
    
    # Transaction Info
    info_frame = tk.Frame(outer_frame, bg="#ffffff")
    info_frame.pack(fill="x", padx=15, pady=5)
    
    import datetime
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    customer_name = parent.controller.app.current_user['name'] if parent.controller.app.current_user else 'Guest'
    
    tk.Label(info_frame, text=f"ORDER ID: #{order_id}", font=("Courier New", 9, "bold"), fg="#000000", bg="#ffffff").pack(anchor="w")
    tk.Label(info_frame, text=f"DATE:     {now_str}", font=("Courier New", 8), fg="#000000", bg="#ffffff").pack(anchor="w")
    tk.Label(info_frame, text=f"CUSTOMER: {customer_name}", font=("Courier New", 8), fg="#000000", bg="#ffffff").pack(anchor="w")
    tk.Label(info_frame, text="STATUS:   PAID", font=("Courier New", 8, "bold"), fg="#047857", bg="#ffffff").pack(anchor="w")
    
    tk.Label(outer_frame, text="----------------------------------", font=("Courier New", 9), fg="#000000", bg="#ffffff").pack()
    
    # Items Section
    items_frame = tk.Frame(outer_frame, bg="#ffffff")
    items_frame.pack(fill="both", expand=True, padx=15, pady=5)
    
    # Make header inside items
    hdr_row = tk.Frame(items_frame, bg="#ffffff")
    hdr_row.pack(fill="x", pady=2)
    tk.Label(hdr_row, text="ITEM NAME & QTY", font=("Courier New", 8, "bold"), fg="#000000", bg="#ffffff").pack(side="left")
    tk.Label(hdr_row, text="PRICE", font=("Courier New", 8, "bold"), fg="#000000", bg="#ffffff").pack(side="right")
    
    for item in items:
        item_row = tk.Frame(items_frame, bg="#ffffff")
        item_row.pack(fill="x", pady=1)
        
        name_text = f"{item['name'][:18].upper()} x{item['qty']}"
        lbl_item_name = tk.Label(item_row, text=name_text, font=("Courier New", 8), fg="#000000", bg="#ffffff")
        lbl_item_name.pack(side="left")
        
        lbl_item_price = tk.Label(item_row, text=f"${item['price']*item['qty']:.2f}", font=("Courier New", 8), fg="#000000", bg="#ffffff")
        lbl_item_price.pack(side="right")
        
    tk.Label(outer_frame, text="----------------------------------", font=("Courier New", 9), fg="#000000", bg="#ffffff").pack()
    
    # Cost Summary
    summary_frame = tk.Frame(outer_frame, bg="#ffffff")
    summary_frame.pack(fill="x", padx=15, pady=5)
    
    row_sub = tk.Frame(summary_frame, bg="#ffffff")
    row_sub.pack(fill="x")
    tk.Label(row_sub, text="SUBTOTAL:", font=("Courier New", 8), fg="#000000", bg="#ffffff").pack(side="left")
    tk.Label(row_sub, text=f"${total_amount:.2f}", font=("Courier New", 8), fg="#000000", bg="#ffffff").pack(side="right")
    
    row_tax = tk.Frame(summary_frame, bg="#ffffff")
    row_tax.pack(fill="x")
    tk.Label(row_tax, text="TAX (0%):", font=("Courier New", 8), fg="#000000", bg="#ffffff").pack(side="left")
    tk.Label(row_tax, text="$0.00", font=("Courier New", 8), fg="#000000", bg="#ffffff").pack(side="right")
    
    row_total = tk.Frame(summary_frame, bg="#ffffff")
    row_total.pack(fill="x", pady=(3, 0))
    tk.Label(row_total, text="TOTAL CHARGED:", font=("Courier New", 9, "bold"), fg="#000000", bg="#ffffff").pack(side="left")
    tk.Label(row_total, text=f"${total_amount:.2f}", font=("Courier New", 9, "bold"), fg="#000000", bg="#ffffff").pack(side="right")
    
    # Simulated Barcode on Canvas
    barcode_canvas = tk.Canvas(outer_frame, width=200, height=35, bg="#ffffff", bd=0, highlightthickness=0)
    barcode_canvas.pack(pady=5)
    
    import random
    random.seed(order_id)
    x = 15
    while x < 185:
        width = random.choice([1, 2, 3, 4])
        space = random.choice([2, 3, 4])
        barcode_canvas.create_rectangle(x, 2, x + width, 32, fill="#000000", outline="")
        x += width + space
        
    barcode_num = f"{order_id:012d}"
    lbl_barcode = tk.Label(outer_frame, text=" ".join(barcode_num), font=("Courier New", 7), fg="#000000", bg="#ffffff")
    lbl_barcode.pack()
    
    # Somali/English footer
    tk.Label(outer_frame, text="Mahadsanid! Waad ku mahadsantahay\nbooqashadaada.", font=("Courier New", 8, "italic"), fg="#000000", bg="#ffffff").pack(pady=(10, 5))
    
    # Button
    btn_close = tk.Button(outer_frame, text="Print & Close", font=("Courier New", 9, "bold"), bg="#000000", fg="#ffffff",
                          activebackground="#333333", activeforeground="#ffffff", borderwidth=0, cursor="hand2", command=receipt_win.destroy)
    btn_close.pack(side="bottom", fill="x", padx=15, pady=(0, 10), ipady=4)


# --- 2. CUSTOMER CART VIEW ---
class CustomerCartView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BACKGROUND)
        self.controller = controller
        
        # Top Bar
        top_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
        top_frame.pack(fill="x", pady=(0, 15))
        
        lbl_title = tk.Label(top_frame, text="My Shopping Cart", font=FONT_HEADER, fg=COLOR_SECONDARY, bg=COLOR_BACKGROUND)
        lbl_title.pack(side="left")
        
        btn_refresh = ttk.Button(top_frame, text="🔄 Refresh Cart", command=self.load_data, style="TButton")
        btn_refresh.pack(side="right")
        
        # Grid containing table left and checkout summaries right
        body_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
        body_frame.pack(fill="both", expand=True)
        
        # Table of items
        tree_container = tk.Frame(body_frame, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1)
        tree_container.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        self.tree = ttk.Treeview(tree_container, columns=("id", "pid", "name", "price", "qty", "total"), show="headings")
        self.tree.heading("id", text="Item ID")
        self.tree.heading("pid", text="Product ID")
        self.tree.heading("name", text="Product Name")
        self.tree.heading("price", text="Price")
        self.tree.heading("qty", text="Quantity")
        self.tree.heading("total", text="Total Price")
        
        self.tree.column("id", width=80, anchor="center")
        self.tree.column("pid", width=80, anchor="center")
        self.tree.column("name", width=220, anchor="w")
        self.tree.column("price", width=100, anchor="e")
        self.tree.column("qty", width=90, anchor="center")
        self.tree.column("total", width=120, anchor="e")
        
        self.tree["displaycolumns"] = ("pid", "name", "price", "qty", "total")
        
        sb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        
        self.tree.bind("<<TreeviewSelect>>", self.on_select_item)
        
        # Right checkout panel
        checkout_frame = tk.LabelFrame(body_frame, text="Order Summary", font=FONT_BOLD, fg=COLOR_SECONDARY, bg=COLOR_CARD_BG, padx=15, pady=15, borderwidth=1, relief="solid", width=280)
        checkout_frame.pack(side="right", fill="y")
        checkout_frame.pack_propagate(False)
        
        # Selected cart item control
        lbl_ctrl = tk.Label(checkout_frame, text="Selected Item Controls:", font=FONT_BOLD, fg=COLOR_TEXT, bg=COLOR_CARD_BG)
        lbl_ctrl.pack(anchor="w", pady=(5, 5))
        
        self.lbl_selected_item = tk.Label(checkout_frame, text="None Selected", font=FONT_SMALL, fg=COLOR_TEXT_LIGHT, bg=COLOR_CARD_BG, wraplength=230, justify="left")
        self.lbl_selected_item.pack(anchor="w", pady=(0, 10))
        
        # Quantity spinbox
        qty_frame = tk.Frame(checkout_frame, bg=COLOR_CARD_BG)
        qty_frame.pack(fill="x", pady=5)
        lbl_qty = tk.Label(qty_frame, text="Quantity:", font=FONT_SMALL, fg=COLOR_TEXT, bg=COLOR_CARD_BG)
        lbl_qty.pack(side="left", padx=(0, 10))
        self.spinbox_qty = tk.Spinbox(qty_frame, from_=1, to=99, font=FONT_NORMAL, width=8, bd=1, relief="solid")
        self.spinbox_qty.pack(side="left")
        
        btn_update = ttk.Button(checkout_frame, text="✏️ Update Qty", command=self.update_quantity, style="TButton")
        btn_update.pack(fill="x", ipady=3, pady=5)
        
        btn_remove = ttk.Button(checkout_frame, text="🗑️ Remove Item", command=self.remove_item, style="Danger.TButton")
        btn_remove.pack(fill="x", ipady=3, pady=5)
        
        sep = tk.Frame(checkout_frame, bg=COLOR_BORDER, height=1)
        sep.pack(fill="x", pady=15)
        
        # Cart Total Summary
        lbl_tot = tk.Label(checkout_frame, text="Checkout Summary", font=FONT_BOLD, fg=COLOR_SECONDARY, bg=COLOR_CARD_BG)
        lbl_tot.pack(anchor="w")
        
        totals_frame = tk.Frame(checkout_frame, bg=COLOR_CARD_BG)
        totals_frame.pack(fill="x", pady=10)
        
        lbl_subtotal_lbl = tk.Label(totals_frame, text="Subtotal Amount:", font=FONT_NORMAL, fg=COLOR_TEXT_LIGHT, bg=COLOR_CARD_BG)
        lbl_subtotal_lbl.grid(row=0, column=0, sticky="w")
        self.lbl_subtotal = tk.Label(totals_frame, text="$0.00", font=FONT_BOLD, fg=COLOR_TEXT, bg=COLOR_CARD_BG)
        self.lbl_subtotal.grid(row=0, column=1, sticky="e")
        
        lbl_shipping_lbl = tk.Label(totals_frame, text="Shipping Fee:", font=FONT_NORMAL, fg=COLOR_TEXT_LIGHT, bg=COLOR_CARD_BG)
        lbl_shipping_lbl.grid(row=1, column=0, sticky="w", pady=5)
        lbl_shipping = tk.Label(totals_frame, text="FREE", font=FONT_BOLD, fg=COLOR_SUCCESS, bg=COLOR_CARD_BG)
        lbl_shipping.grid(row=1, column=1, sticky="e", pady=5)
        
        totals_frame.grid_columnconfigure(0, weight=1)
        totals_frame.grid_columnconfigure(1, weight=1)
        
        # Delivery Location Entry
        lbl_loc = tk.Label(checkout_frame, text="Delivery Location / Address *", font=FONT_BOLD, fg=COLOR_TEXT, bg=COLOR_CARD_BG)
        lbl_loc.pack(anchor="w", pady=(10, 2))
        self.entry_location = tk.Entry(checkout_frame, font=FONT_NORMAL, highlightthickness=1, highlightbackground=COLOR_BORDER, bd=0)
        self.entry_location.pack(fill="x", ipady=4, pady=(0, 10))
        
        self.lbl_total = tk.Label(checkout_frame, text="Total: $0.00", font=("Segoe UI", 16, "bold"), fg=COLOR_PRIMARY, bg=COLOR_CARD_BG)
        self.lbl_total.pack(pady=5)
        
        btn_checkout = ttk.Button(checkout_frame, text="🚀 Checkout Now", command=self.checkout_cart, style="Success.TButton")
        btn_checkout.pack(fill="x", ipady=6, pady=5)
        
        self.selected_item_id = None
        self.selected_item_price = 0.0
        self.load_data()

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        cart_id = self.controller.cart_id
        cart_total = 0.0
        
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT ci.cart_item_id, ci.product_id, p.name, p.price, ci.quantity 
                    FROM cart_items ci
                    JOIN products p ON ci.product_id = p.product_id
                    WHERE ci.cart_id = :cart_id
                    ORDER BY ci.cart_item_id
                """, {"cart_id": cart_id})
                for row in cursor.fetchall():
                    item_id, prod_id, name, price, qty = row[0], row[1], row[2], row[3], row[4]
                    row_total = price * qty
                    cart_total += row_total
                    self.tree.insert("", "end", values=(item_id, prod_id, name, f"${price:.2f}", qty, f"${row_total:.2f}"))
            conn.close()
            
            # Update labels
            self.lbl_subtotal.config(text=f"${cart_total:.2f}")
            self.lbl_total.config(text=f"Total: ${cart_total:.2f}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve cart: {e}")

    def on_select_item(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        vals = self.tree.item(selected[0], "values")
        self.selected_item_id = vals[0]
        self.lbl_selected_item.config(text=f"{vals[2]}\nPrice: {vals[3]}")
        
        # Set quantity in spinbox
        self.spinbox_qty.delete(0, "end")
        self.spinbox_qty.insert(0, vals[4])

    def update_quantity(self):
        if not self.selected_item_id:
            messagebox.showwarning("Selection Required", "Please select an item from your cart first.")
            return
            
        qty_str = self.spinbox_qty.get()
        try:
            qty = int(qty_str)
            if qty <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Validation Error", "Quantity must be a valid integer greater than 0.")
            return
            
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE cart_items 
                    SET quantity = :qty 
                    WHERE cart_item_id = :id
                """, {"qty": qty, "id": self.selected_item_id})
                conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Shopping cart quantity updated.")
            self.load_data()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not update quantity:\n{e}")

    def remove_item(self):
        if not self.selected_item_id:
            messagebox.showwarning("Selection Required", "Please select an item from your cart first.")
            return
            
        if not messagebox.askyesno("Confirm Remove", "Are you sure you want to delete this product from your cart?"):
            return
            
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM cart_items WHERE cart_item_id = :id", {"id": self.selected_item_id})
                conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Item removed from shopping cart.")
            self.lbl_selected_item.config(text="None Selected")
            self.selected_item_id = None
            self.load_data()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not delete item:\n{e}")

    def checkout_cart(self):
        cart_id = self.controller.cart_id
        user_id = self.controller.app.current_user["user_id"]
        
        # Verify cart has items first
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM cart_items WHERE cart_id = :cart_id", {"cart_id": cart_id})
                cnt = cursor.fetchone()[0]
                if cnt == 0:
                    messagebox.showwarning("Cart Empty", "Your shopping cart is empty. Browse products and add items first.")
                    conn.close()
                    return
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to inspect cart:\n{e}")
            return
            
        if not messagebox.askyesno("Confirm Checkout", "Proceed to check out and finalize your order?"):
            return
            
        # Extract items from Treeview for printing on the receipt
        receipt_items = []
        for child in self.tree.get_children():
            val = self.tree.item(child, 'values')
            try:
                # Columns: ("id", "pid", "name", "price", "qty", "total")
                name = val[2]
                price = float(val[3].replace('$', '').strip())
                qty = int(val[4])
                receipt_items.append({"name": name, "price": price, "qty": qty})
            except Exception:
                pass
            
        shipping_addr = self.entry_location.get().strip()
        if not shipping_addr:
            messagebox.showwarning("Location Required", "Please enter your shipping/delivery location address in the input field before checking out.")
            return

        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                # 1. Invoke Oracle package procedure process_bulk_checkout
                # pkg_order_management.process_bulk_checkout(p_cart_id, p_user_id, p_new_order_id OUT)
                new_order_id_var = cursor.var(oracledb.NUMBER)
                cursor.callproc("pkg_order_management.process_bulk_checkout", [cart_id, user_id, new_order_id_var])
                new_order_id = int(new_order_id_var.getvalue())
                
                # 2. Invoke Oracle package function calculate_order_total to double check total
                # pkg_order_management.calculate_order_total(p_order_id)
                # Wait, process_bulk_checkout already updates the orders table's total_amount.
                # So we can query total_amount directly or call the package function:
                cursor.execute("SELECT total_amount FROM orders WHERE order_id = :order_id", {"order_id": new_order_id})
                total_amount = cursor.fetchone()[0]
                
                # 3. Create simulated payment settlements matching server.py checkout logic
                cursor.execute("INSERT INTO payments (order_id, amount) VALUES (:order_id, :amount)", 
                               {"order_id": new_order_id, "amount": total_amount})
                
                # 4. Save the customer's delivery location address to the orders table
                cursor.execute("UPDATE orders SET shipping_address = :addr WHERE order_id = :order_id", 
                               {"addr": shipping_addr, "order_id": new_order_id})
                
                conn.commit()
            conn.close()
            
            # Show the beautiful paper receipt window instead of standard messagebox
            show_receipt_window(self, new_order_id, total_amount, receipt_items)
            
            # Clear selected tracking states, clear location entry, and reload cart
            self.entry_location.delete(0, tk.END)
            self.selected_item_id = None
            self.lbl_selected_item.config(text="None Selected")
            self.load_data()
        except oracledb.DatabaseError as db_err:
            error_obj, = db_err.args
            messagebox.showerror("PL/SQL Error", f"Oracle transaction aborted:\n{error_obj.message}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not checkout cart:\n{e}")

# --- 3. CUSTOMER ORDERS VIEW ---
class CustomerOrdersView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BACKGROUND)
        self.controller = controller
        
        # Top Bar
        top_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
        top_frame.pack(fill="x", pady=(0, 15))
        
        lbl_title = tk.Label(top_frame, text="My Purchasing History", font=FONT_HEADER, fg=COLOR_SECONDARY, bg=COLOR_BACKGROUND)
        lbl_title.pack(side="left")
        
        btn_refresh = ttk.Button(top_frame, text="🔄 Refresh History", command=self.load_data, style="TButton")
        btn_refresh.pack(side="right")
        
        # Outer Notebook tabs: Tab 1 Orders, Tab 2 Payments
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True)
        
        # Tab 1: Orders
        self.tab_orders = tk.Frame(self.tabs, bg=COLOR_BACKGROUND)
        self.tabs.add(self.tab_orders, text=" My Orders ")
        
        # Layout inside Tab 1: Split into Master (orders) and Detail (order items)
        paned = tk.PanedWindow(self.tab_orders, orient="vertical", bg=COLOR_BACKGROUND, sashwidth=4, bd=0)
        paned.pack(fill="both", expand=True, pady=10)
        
        # Master Order List Frame
        master_frame = tk.LabelFrame(paned, text="Orders History", font=FONT_BOLD, fg=COLOR_SECONDARY, bg=COLOR_CARD_BG, borderwidth=1, relief="solid")
        paned.add(master_frame, height=200)
        
        self.tree_orders = ttk.Treeview(master_frame, columns=("id", "amt", "status"), show="headings")
        self.tree_orders.heading("id", text="Order ID")
        self.tree_orders.heading("amt", text="Total Price Charged")
        self.tree_orders.heading("status", text="Order Status")
        
        self.tree_orders.column("id", width=100, anchor="center")
        self.tree_orders.column("amt", width=180, anchor="e")
        self.tree_orders.column("status", width=180, anchor="center")
        
        self.tree_orders.tag_configure('Pending', foreground=COLOR_WARNING, font=FONT_BOLD)
        self.tree_orders.tag_configure('Completed', foreground=COLOR_SUCCESS, font=FONT_BOLD)
        self.tree_orders.tag_configure('Cancelled', foreground=COLOR_DANGER, font=FONT_BOLD)
        self.tree_orders.tag_configure('Shipped', foreground=COLOR_PRIMARY, font=FONT_BOLD)
        self.tree_orders.tag_configure('Delivered', foreground="#a855f7", font=FONT_BOLD)
        
        sb_mo = ttk.Scrollbar(master_frame, orient="vertical", command=self.tree_orders.yview)
        self.tree_orders.configure(yscrollcommand=sb_mo.set)
        
        self.tree_orders.pack(side="left", fill="both", expand=True)
        sb_mo.pack(side="right", fill="y")
        
        self.tree_orders.bind("<<TreeviewSelect>>", self.on_select_order)
        
        # Detail Order Items Frame
        detail_frame = tk.LabelFrame(paned, text="Order Product Line Details", font=FONT_BOLD, fg=COLOR_SECONDARY, bg=COLOR_CARD_BG, borderwidth=1, relief="solid")
        paned.add(detail_frame, height=180)
        
        self.tree_details = ttk.Treeview(detail_frame, columns=("pid", "pname", "price", "qty", "line_total"), show="headings")
        self.tree_details.heading("pid", text="Product ID")
        self.tree_details.heading("pname", text="Product Name")
        self.tree_details.heading("price", text="Unit Price")
        self.tree_details.heading("qty", text="Quantity")
        self.tree_details.heading("line_total", text="Line Total")
        
        self.tree_details.column("pid", width=100, anchor="center")
        self.tree_details.column("pname", width=250, anchor="w")
        self.tree_details.column("price", width=120, anchor="e")
        self.tree_details.column("qty", width=100, anchor="center")
        self.tree_details.column("line_total", width=150, anchor="e")
        
        sb_od = ttk.Scrollbar(detail_frame, orient="vertical", command=self.tree_details.yview)
        self.tree_details.configure(yscrollcommand=sb_od.set)
        
        self.tree_details.pack(side="left", fill="both", expand=True)
        sb_od.pack(side="right", fill="y")
        
        # Tab 2: Payments
        self.tab_payments = tk.Frame(self.tabs, bg=COLOR_BACKGROUND)
        self.tabs.add(self.tab_payments, text=" My Receipts & Payments ")
        
        tree_container_pay = tk.Frame(self.tab_payments, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1)
        tree_container_pay.pack(fill="both", expand=True, pady=10)
        
        self.tree_payments = ttk.Treeview(tree_container_pay, columns=("pay_id", "order_id", "amount"), show="headings")
        self.tree_payments.heading("pay_id", text="Receipt Payment ID")
        self.tree_payments.heading("order_id", text="Order Reference ID")
        self.tree_payments.heading("amount", text="Paid Amount")
        
        self.tree_payments.column("pay_id", width=150, anchor="center")
        self.tree_payments.column("order_id", width=150, anchor="center")
        self.tree_payments.column("amount", width=200, anchor="e")
        
        sb_pay = ttk.Scrollbar(tree_container_pay, orient="vertical", command=self.tree_payments.yview)
        self.tree_payments.configure(yscrollcommand=sb_pay.set)
        
        self.tree_payments.pack(side="left", fill="both", expand=True)
        sb_pay.pack(side="right", fill="y")
        
        self.load_data()

    def load_data(self):
        # Clear
        for item in self.tree_orders.get_children():
            self.tree_orders.delete(item)
        for item in self.tree_details.get_children():
            self.tree_details.delete(item)
        for item in self.tree_payments.get_children():
            self.tree_payments.delete(item)
            
        user_id = self.controller.app.current_user["user_id"]
        
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                # Retrieve client orders
                cursor.execute("""
                    SELECT order_id, total_amount, status 
                    FROM orders 
                    WHERE user_id = :user_id 
                    ORDER BY order_id DESC
                """, {"user_id": user_id})
                for row in cursor.fetchall():
                    self.tree_orders.insert("", "end", values=(row[0], f"${row[1]:.2f}", row[2]), tags=(row[2],))
                    
                # Retrieve client payments
                cursor.execute("""
                    SELECT p.payment_id, p.order_id, p.amount 
                    FROM payments p 
                    JOIN orders o ON p.order_id = o.order_id 
                    WHERE o.user_id = :user_id
                    ORDER BY p.payment_id DESC
                """, {"user_id": user_id})
                for row in cursor.fetchall():
                    self.tree_payments.insert("", "end", values=(row[0], row[1], f"${row[2]:.2f}"))
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve purchase history: {e}")

    def on_select_order(self, event):
        selected = self.tree_orders.selection()
        if not selected:
            return
            
        order_id = self.tree_orders.item(selected[0], "values")[0]
        
        # Clear previous detail items
        for item in self.tree_details.get_children():
            self.tree_details.delete(item)
            
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT oi.product_id, p.name, p.price, oi.quantity 
                    FROM order_items oi
                    JOIN products p ON oi.product_id = p.product_id
                    WHERE oi.order_id = :order_id
                    ORDER BY oi.order_item_id
                """, {"order_id": order_id})
                for row in cursor.fetchall():
                    prod_id, name, price, qty = row[0], row[1], row[2], row[3]
                    line_total = price * qty
                    self.tree_details.insert("", "end", values=(prod_id, name, f"${price:.2f}", qty, f"${line_total:.2f}"))
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve details of order #{order_id}: {e}")

# ==============================================================================
# SCRIPT EXECUTION
# ==============================================================================
if __name__ == "__main__":
    app = OnlineShoppingApp()
    app.mainloop()
