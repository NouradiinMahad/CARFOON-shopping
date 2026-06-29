const API_BASE = `http://${window.location.hostname || 'localhost'}:5000/api`;

// Application State
let state = {
    users: [],
    activeUserId: null,
    activeUserName: '',
    activeUserRole: '',
    categories: [],
    products: [],
    selectedCategory: 'all',
    cart: { items: [] },
    orders: [],
    theme: 'light',
    loggedInUser: null,
    currentAdminSubview: 'dashboard',
    adminSearchQueries: { products: '', categories: '', users: '' },
    adminOrdersStatusFilter: 'all',
    lang: 'so' // Default language
};

// Custom fetch wrapper to attach active user ID for RBAC
async function apiFetch(url, options = {}) {
    options.headers = options.headers || {};
    if (state.activeUserId) {
        options.headers['X-User-Id'] = state.activeUserId.toString();
    }
    return fetch(url, options);
}


// Complete dynamic dictionary translations
const translations = {
    en: {
        brand: "CARFOON online shopping",
        brand_admin: "ShopAdmin",
        welcome_title: "Welcome Back",
        welcome_subtitle: "Enter your email and password to log in.",
        email_label: "Email Address",
        email_placeholder: "Example: admin@gmail.com",
        email_register_placeholder: "Example: ahmed@gmail.com",
        password_label: "Password",
        password_placeholder: "••••••••",
        forgot_pwd_link: "Forgot Password?",
        create_acct_link: "Create Account (Sign Up)",
        login_btn_text: "Login",
        register_title: "Sign Up",
        register_subtitle: "Please enter your details to create a new account.",
        fullname_label: "Full Name",
        fullname_placeholder: "Example: Ahmed Ali",
        confirm_password_label: "Confirm Password",
        already_have_account: "Already have an account?",
        register_btn_text: "Sign Up",
        forgot_title: "Forgot Password",
        forgot_subtitle: "Enter your email to request a verification code.",
        back_to_login: "← Back to Login",
        send_code_btn: "Send Code",
        reset_title: "Reset Password",
        reset_subtitle: "Enter verification code and your new password.",
        verification_code_label: "Verification Code",
        code_placeholder: "6-Digit Code",
        new_password_label: "New Password",
        cancel_reset: "← Cancel",
        reset_btn_text: "Reset Password",
        
        nav_categories: "Categories",
        nav_cart: "Cart",
        nav_orders: "Orders",
        nav_payments: "Payments",
        nav_profile: "Profile",
        nav_admin_dashboard: "Admin Dashboard",
        my_payments_title: "My Payments",
        my_payments_subtitle: "View your payment history.",
        payments_empty_title: "No Payments",
        payments_empty_desc: "You have not made any payments yet.",
        
        sidebar_categories: "CATEGORIES",
        view_reports_btn: "View Reports",
        store_subtitle: "Welcome back! Find everything you need for your business operations.",
        search_placeholder: "Search products, orders, or categories...",
        trending_items_title: "Trending Items",
        trending_items_subtitle: "Recommended based on your recent activity",
        filter_btn: "Filter",
        sort_newest: "Sort by: Newest",
        sort_price_low: "Price: Low to High",
        sort_price_high: "Price: High to Low",
        
        bulk_discount_title: "Bulk Order Discount",
        bulk_discount_desc: "Save up to 15% when ordering more than 50 units of selected inventory items.",
        explore_terms_btn: "Explore Terms",
        rewards_member_title: "Rewards Member",
        rewards_member_desc: "You're only 250 points away from a $25 credit on your next order.",
        points_750: "750 Points",
        points_1000: "1000 Points",
        
        cart_large_title_text: "Your Shopping Cart",
        cart_large_subtitle: "Review your products before checking out.",
        order_summary_title: "Order Summary",
        subtotal_label: "Subtotal",
        vat_label: "VAT (15%)",
        grand_total_label: "Grand Total",
        checkout_btn_text: "Checkout",
        cart_empty_title: "Your Cart is Empty",
        cart_empty_desc: "Please browse Categories to add items to your cart.",
        
        my_orders_title: "My Orders",
        my_orders_subtitle: "Track your past orders directly from the system.",
        orders_empty_title: "No orders placed yet.",
        orders_empty_desc: "Your purchases will appear here automatically.",
        
        role_desc_title: "Role Description",
        db_engine_label: "System Engine",
        session_status_label: "Session Status",
        active_status: "Active",
        current_schema_label: "Current Schema",
        access_matrix_title: "Application Access Matrix",
        access_matrix_subtitle: "Interface behaviors customized based on your system role.",
        policy_browse_title: "Browse Products",
        policy_browse_desc: "Ability to view catalog and filter products.",
        policy_checkout_title: "Cart & Checkout",
        policy_checkout_desc: "Ability to add products to cart and complete checkout.",
        policy_add_prod_title: "Insert Products",
        policy_add_prod_desc: "Ability to add new products to the system.",
        policy_update_status_title: "Update Order Status",
        policy_update_status_desc: "Ability to update order status.",
        policy_view_tables_title: "Admin DB Tables",
        policy_view_tables_desc: "Ability to inspect system tables in live view.",
        policy_yes: "Yes",
        policy_no: "No",
        
        system_privs_title: "System Privileges",
        system_privs_subtitle: "Global system permissions allocated to the active role.",
        th_privilege: "Privilege",
        th_type: "Type",
        th_status: "Active Status",
        object_privs_title: "Object Privileges",
        object_privs_subtitle: "Access privileges configured on tables and packages.",
        th_object_name: "Table/Object Name",
        
        dbms_log_title: "DBMS_OUTPUT / SQL Developer Script Output log",
        live_session_connection: "Live Session Connection",
        
        menu_section_main: "MAIN",
        menu_dashboard: "Dashboard",
        menu_products: "Products",
        menu_categories: "Categories",
        menu_section_commerce: "COMMERCE",
        menu_orders: "Orders",
        menu_users: "Users",
        menu_payments: "Payments",
        menu_section_system: "SYSTEM",
        menu_audit: "Audit Log",
        back_to_shop: "Back to Shop",
        logout: "Logout",
        dashboard_overview: "Dashboard Overview",
        reset_db_btn: "Reset DB",
        stat_total_users: "Total Users",
        stat_total_products: "Total Products",
        stat_total_orders: "Total Orders",
        stat_total_revenue: "Total Revenue"
    },
    so: {
        brand: "CARFOON online shopping",
        brand_admin: "ShopAdmin",
        welcome_title: "Ku Soo Dhowow",
        welcome_subtitle: "Geli email-kaaga iyo fure-sirta si aad u gasho nidaamka.",
        email_label: "Email Address",
        email_placeholder: "Tusaale: admin@gmail.com",
        email_register_placeholder: "Tusaale: ahmed@gmail.com",
        password_label: "Fure-sirta (Password)",
        password_placeholder: "••••••••",
        forgot_pwd_link: "Forgot Password?",
        create_acct_link: "Create Account (Sign Up)",
        login_btn_text: "Geli Nidaamka (Login)",
        register_title: "Sign Up",
        register_subtitle: "Please enter your information to create a new account.",
        fullname_label: "Magacaaga oo Buuxa (Full Name)",
        fullname_placeholder: "Tusaale: Ahmed Ali",
        confirm_password_label: "Xaqiiji Fure-sirta (Confirm Password)",
        already_have_account: "Already have an account?",
        register_btn_text: "Sign Up",
        forgot_title: "Fure-sir Codso (Forgot Password)",
        forgot_subtitle: "Geli email-kaaga si aan kuugu soo dirno koodhka xaqiijinta.",
        back_to_login: "← Ku laabo Login-ka",
        send_code_btn: "Soo Dir Koodhka (Send Code)",
        reset_title: "Deji Fure-sir Cusub",
        reset_subtitle: "Geli koodhka xaqiijinta iyo fure-sirta cusub ee aad rabto.",
        verification_code_label: "Koodhka Xaqiijinta (Verification Code)",
        code_placeholder: "6-Digit Code",
        new_password_label: "Fure-sir Cusub (New Password)",
        cancel_reset: "← Cancel",
        reset_btn_text: "Bedel Fure-sirta (Reset Password)",
        
        nav_categories: "Categories",
        nav_cart: "Cart",
        nav_orders: "Dalabaadka",
        nav_payments: "Payments",
        nav_profile: "Koontada",
        nav_admin_dashboard: "Maamulka",
        my_payments_title: "Taariikhda Payments",
        my_payments_subtitle: "Track your payments here.",
        payments_empty_title: "No Payments Made",
        payments_empty_desc: "You have not made any payments in the system yet."
        
        sidebar_categories: "CATEGORIES",
        view_reports_btn: "View Reports",
        store_subtitle: "Welcome back! Find everything you need for your business operations.",
        search_placeholder: "Search products, orders, or categories...",
        trending_items_title: "Trending Items",
        trending_items_subtitle: "Recommended based on your recent activity",
        filter_btn: "Filter",
        sort_newest: "Sort by: Newest",
        sort_price_low: "Price: Low to High",
        sort_price_high: "Price: High to Low",
        
        bulk_discount_title: "Bulk Order Discount",
        bulk_discount_desc: "Save up to 15% when ordering more than 50 units of selected inventory items.",
        explore_terms_btn: "Explore Terms",
        rewards_member_title: "Rewards Member",
        rewards_member_desc: "You're only 250 points away from a $25 credit on your next order.",
        points_750: "750 Points",
        points_1000: "1000 Points",
        
        cart_large_title_text: "Your Shopping Cart",
        cart_large_subtitle: "Review the items you added to the cart before submitting your order.",
        order_summary_title: "Faahfaahinta Lacag-bixinta (Order Summary)",
        subtotal_label: "Subtotal (Cadadka Alaabta)",
        vat_label: "Canshuur / VAT (15%)",
        grand_total_label: "Warta Guud (Grand Total)",
        checkout_btn_text: "Submit Order",
        cart_empty_title: "Your cart is empty",
        cart_empty_desc: "Please go to the Categories section to add items to your cart.",
        
        my_orders_title: "Taariikhda Dalabaadka (My Orders)",
        my_orders_subtitle: "Halkan ka la soco dalabaadkaagii hore ee laga soo qaaday nidaamka.",
        orders_empty_title: "Ma jiraan dalabaad hore oo aad sameysay.",
        orders_empty_desc: "Dalabaadka aad iibsato halkan ayey si toos ah uga soo muuqan doonaan.",
        
        role_desc_title: "Fahfaahinta Booska (Role Description)",
        db_engine_label: "System Engine",
        session_status_label: "Session Status",
        active_status: "Active",
        current_schema_label: "Current Schema",
        access_matrix_title: "Muraayada Ogolaanshaha App-ka (Application Access Matrix)",
        access_matrix_subtitle: "Hab-dhaqanka interface-ka ee ku saleysan shaqada laguu igmaday.",
        policy_browse_title: "Aragtida Alaabta (Browse Products)",
        policy_browse_desc: "Awooda lagu arki karo catalog-ga iyo shaandhaynta alaabta.",
        policy_checkout_title: "Cart & Checkout",
        policy_checkout_desc: "Ability to add items to cart and complete checkout.",
        policy_add_prod_title: "Soo Gelinta Alaab Cusub (Insert Products)",
        policy_add_prod_desc: "Awooda lagu daro alaab ku cusub system-ka.",
        policy_update_status_title: "Bedelaada Status-ka Dalabka (Update Status)",
        policy_update_status_desc: "Awooda lagu bedelo heerka dalabka gudaha system-ka.",
        policy_view_tables_title: "Aragtida Shaxaha DB-ga (Admin Tables)",
        policy_view_tables_desc: "Awooda lagu dhex galo Live View ee shaxaha hoose ee nidaamka.",
        policy_yes: "Haa",
        policy_no: "Maya",
        
        system_privs_title: "System Privileges (Fasaxyada Nidaamka)",
        system_privs_subtitle: "Ogolaanshaha uu user-ku u leeyahay inuu sameeyo falalka guud ee nidaamka.",
        th_privilege: "Privilege (Ruqsada)",
        th_type: "Nooca (Type)",
        th_status: "Status-ka Hadda (Active Status)",
        object_privs_title: "Object Privileges (Ruqsadaha Shaxaha)",
        object_privs_subtitle: "Xuquuqda gaarka ah ee uu user-ku u leeyahay shaxaha (Tables) iyo xirmooyinka (Packages).",
        th_object_name: "Table/Object Name",
        
        dbms_log_title: "DBMS_OUTPUT / SQL Developer Script Output log",
        live_session_connection: "Live Session Connection",
        
        menu_section_main: "MAIN",
        menu_dashboard: "Dashboard",
        menu_products: "Products",
        menu_categories: "Categories",
        menu_section_commerce: "COMMERCE",
        menu_orders: "Orders",
        menu_users: "Users",
        menu_payments: "Payments",
        menu_section_system: "SYSTEM",
        menu_audit: "Audit Log",
        back_to_shop: "Dukaanka Ku Noqo",
        logout: "Ka Bax (Logout)",
        dashboard_overview: "Dashboard Overview",
        reset_db_btn: "Reset DB",
        stat_total_users: "Total Users",
        stat_total_products: "Total Products",
        stat_total_orders: "Total Orders",
        stat_total_revenue: "Total Revenue"
    }
};


function applyLanguage(lang) {
    state.lang = lang;
    document.documentElement.setAttribute('lang', lang);
    
    document.documentElement.setAttribute('dir', 'ltr');
    
    const dict = translations[lang];
    if (!dict) return;
    
    // Update all elements with data-translate attribute
    document.querySelectorAll('[data-translate]').forEach(el => {
        const key = el.getAttribute('data-translate');
        if (dict[key]) {
            el.textContent = dict[key];
        }
    });
    
    // Update all elements with data-translate-placeholder attribute
    document.querySelectorAll('[data-translate-placeholder]').forEach(el => {
        const key = el.getAttribute('data-translate-placeholder');
        if (dict[key]) {
            el.setAttribute('placeholder', dict[key]);
        }
    });
    
    // Sync dropdown values
    document.querySelectorAll('.lang-select-small, .lang-select').forEach(select => {
        select.value = lang;
    });

    // Update greeting dynamically if logged in
    if (state.loggedInUser) {
        const greetingTitle = document.getElementById('storefront-greeting-title');
        if (greetingTitle) {
            if (lang === 'ar') {
                greetingTitle.innerText = `مرحباً، ${state.activeUserName}`;
            } else {
                greetingTitle.innerText = `Hi, ${state.activeUserName}`;
            }
        }
        
        // Update user profile badge in header
        const activeUserBadgeName = document.getElementById('active-user-name');
        if (activeUserBadgeName) {
            activeUserBadgeName.innerText = `${state.activeUserName} (${state.activeUserRole.toUpperCase()})`;
        }
    }
}

function changeLanguage(lang) {
    localStorage.setItem('lang', lang);
    applyLanguage(lang);
    
    // Refresh active views to update dynamically loaded texts
    if (state.loggedInUser) {
        renderCart();
        renderOrders();
        renderPermissionsView();
    }
}

// Bind handlers to global scope
window.changeLanguage = changeLanguage;
window.applyLanguage = applyLanguage;

// Console logger helper (syncs both storefront and admin logs)
function logConsole(message, type = 'info') {
    const time = new Date().toLocaleTimeString();
    
    let prefix = '';
    if (type === 'query') prefix = '[SQL] ';
    else if (type === 'error') prefix = '[ERROR] ';
    else if (type === 'success') prefix = '[SUCCESS] ';
    else prefix = '[INFO] ';

    const content = `${time} ${prefix}${message}`;

    ['store-console-output', 'admin-console-output'].forEach(id => {
        const consoleOutput = document.getElementById(id);
        if (!consoleOutput) return;
        const line = document.createElement('div');
        line.className = `console-line ${type}`;
        line.innerText = content;
        consoleOutput.appendChild(line);
        consoleOutput.scrollTop = consoleOutput.scrollHeight;
    });
}

// Toast notification helper
function showToast(message, type = 'info') {
    const container = document.getElementById('notification-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    let icon = '';
    if (type === 'success') {
        icon = `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="toast-icon"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg>`;
    } else if (type === 'error') {
        icon = `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="toast-icon"><circle cx="12" cy="12" r="10"/><line x1="15" x2="9" y1="9" y2="15"/><line x1="9" x2="15" y1="9" y2="15"/></svg>`;
    } else {
        icon = `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="toast-icon"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg>`;
    }

    toast.innerHTML = `
        ${icon}
        <div class="toast-content">${message}</div>
    `;

    container.appendChild(toast);

    // Auto-remove after 4 seconds
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s reverse';
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Fetch Initial Data
async function initApp() {
    logConsole("Initializing E-commerce Oracle Web App...", "info");
    
    // Check language preference
    const savedLang = localStorage.getItem('lang') || 'so';
    state.lang = savedLang;
    applyLanguage(savedLang);
    
    // Check theme preference
    const savedTheme = localStorage.getItem('theme') || 'light';
    state.theme = savedTheme;
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeToggleIcon();

    try {
        await fetchUsers();
        await fetchProductsAndCategories();
        
        setupEventListeners();

        // Restore active user session if it exists
        const storedUser = localStorage.getItem('sessionUser');
        if (storedUser) {
            loginUserSession(JSON.parse(storedUser));
        } else {
            // Auto login user since they requested it
            await handleLogin('nourcade0@gmail.com', '112233');
            if (!state.loggedInUser) {
                switchPage('login');
            }
        }
        
        logConsole("App initialization completed successfully.", "success");
    } catch (err) {
        logConsole(`App initialization failed: ${err.message}`, "error");
        showToast("Backend connection failed! Is server.py running?", "error");
    }
}

// Page Toggles
function switchPage(pageName) {
    document.querySelectorAll('.page-container').forEach(page => {
        if (page.id === `${pageName}-page`) {
            page.classList.add('active');
        } else {
            page.classList.remove('active');
        }
    });
    logConsole(`Switched view to ${pageName.toUpperCase()} layout.`, "info");
}

// User login API validation
async function handleLogin(email, password) {
    logConsole(`SELECT user_id, name, email, role FROM users WHERE email = '${email}' AND password = '${password}';`, "query");
    
    try {
        const res = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const result = await res.json();
        
        if (result.success) {
            state.loggedInUser = result.user;
            localStorage.setItem('sessionUser', JSON.stringify(result.user));
            
            let welcomeMsg = `Ku soo dhowow, ${result.user.name}!`;
            if (state.lang === 'en') welcomeMsg = `Welcome back, ${result.user.name}!`;
            
            showToast(welcomeMsg, "success");
            loginUserSession(result.user);
        } else {
            let errMsg = result.error || "Gali email ama password sax ah";
            if (!result.error) {
                if (state.lang === 'en') errMsg = "Incorrect email or password.";
            }
            showToast(errMsg, "error");
            logConsole(`Failed login attempt for email: ${email}`, "error");
        }
    } catch (err) {
        logConsole(`Login connection failed: ${err.message}`, "error");
        showToast("Backend server error!", "error");
    }
}

// Trigger login directly for quick logins
async function quickLogin(email, password) {
    await handleLogin(email, password);
}

// Logout session
function logout() {
    state.loggedInUser = null;
    state.activeUserId = null;
    state.activeUserName = '';
    state.activeUserRole = '';
    localStorage.removeItem('sessionUser');
    switchPage('login');
    
    let logoutMsg = "You have been logged out.";
    if (state.lang === 'en') logoutMsg = "You have been logged out.";
    
    showToast(logoutMsg, "info");
    logConsole("User session logged out successfully.", "info");
}

// Bind logged in session variables
function loginUserSession(user) {
    state.activeUserId = user.user_id;
    state.activeUserName = user.name;
    state.activeUserRole = user.role;
    
    logConsole(`Authenticated user: ${user.name} (Role: ${user.role.toUpperCase()})`, "success");
    
    // Update top bar profile badge
    const activeUserBadgeName = document.getElementById('active-user-name');
    if (activeUserBadgeName) {
        activeUserBadgeName.innerText = `${user.name} (${user.role.toUpperCase()})`;
    }

    // Toggle admin console redirect button
    const adminBtn = document.getElementById('nav-admin-dashboard-btn');
    if (adminBtn) {
        if (user.role === 'admin') {
            adminBtn.style.display = 'flex';
        } else {
            adminBtn.style.display = 'none';
        }
    }

    // Make Profile tab visibility available to all logged-in users so they can inspect their permissions
    const profileTab = document.getElementById('tab-btn-profile');
    if (profileTab) {
        profileTab.style.display = 'flex';
    }

    // Toggle storefront live console logs for admins only
    const storeConsoleCard = document.getElementById('storefront-console-card');
    if (storeConsoleCard) {
        if (user.role === 'admin') {
            storeConsoleCard.style.display = 'block';
        } else {
            storeConsoleCard.style.display = 'none';
        }
    }

    // Fetch active user storefront data
    fetchCart();
    fetchOrders();
    renderPermissionsView();
    
    // Navigate to correct page on login
    if (user.role === 'admin') {
        switchPage('admin');
        // Activate Dashboard button in sidebar menu
        document.querySelectorAll('.admin-menu-btn').forEach(b => {
            if (b.dataset.subview === 'dashboard') b.classList.add('active');
            else b.classList.remove('active');
        });
        document.querySelectorAll('.admin-subview').forEach(view => {
            if (view.id === 'subview-dashboard') view.classList.add('active');
            else view.classList.remove('active');
        });
        
        // Load admin panel data in background/foreground
        fetchAdminStats();
        loadSubViewData('dashboard');
    } else {
        switchPage('store');
        switchView('categories');
    }

    // Update storefront greeting
    const greetingTitle = document.getElementById('storefront-greeting-title');
    if (greetingTitle) {
        greetingTitle.innerText = `Hi, ${user.name}`;
    }
}

// Fetch Users List
async function fetchUsers() {
    logConsole("SELECT user_id, name, email, role FROM users ORDER BY user_id;", "query");
    const res = await fetch(`${API_BASE}/users`);
    if (!res.ok) throw new Error("Failed to fetch users");
    state.users = await res.json();
}

// Fetch Catalog items
async function fetchProductsAndCategories() {
    logConsole("SELECT * FROM products; SELECT * FROM categories;", "query");
    const res = await fetch(`${API_BASE}/products`);
    if (!res.ok) throw new Error("Failed to fetch products/categories");
    const data = await res.json();
    state.products = data.products;
    state.categories = data.categories;
    
    renderCategoryFilters();
    renderProducts();
}

// Fetch Store Shopping Cart
async function fetchCart() {
    if (!state.activeUserId) return;
    
    logConsole(`SELECT * FROM cart_items WHERE cart_id = (SELECT cart_id FROM cart WHERE user_id = ${state.activeUserId});`, "query");
    try {
        const res = await fetch(`${API_BASE}/cart/${state.activeUserId}`);
        if (!res.ok) throw new Error("Failed to load cart");
        state.cart = await res.json();
        renderCart();
    } catch (err) {
        logConsole(`Error fetching cart: ${err.message}`, "error");
    }
}

// Render Shopping Cart (Storefront)
function renderCart() {
    const container = document.getElementById('cart-items-large-container');
    const countSpan = document.getElementById('cart-large-count');
    const subtotalSpan = document.getElementById('cart-large-subtotal');
    const vatSpan = document.getElementById('cart-large-vat');
    const totalSpan = document.getElementById('cart-large-total');
    const checkoutBtn = document.getElementById('btn-large-checkout');
    
    // Also support navbar cart count badge if any
    const cartBadge = document.getElementById('cart-total-count');
    
    if (!state.cart.items || state.cart.items.length === 0) {
        if (container) {
            const emptyTitle = translations[state.lang].cart_empty_title;
            const emptyDesc = translations[state.lang].cart_empty_desc;
            container.innerHTML = `
                <div class="empty-state">
                    <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom:1rem; color:var(--text-muted);"><circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/></svg>
                    <h3>${emptyTitle}</h3>
                    <p>${emptyDesc}</p>
                </div>
            `;
        }
        if (countSpan) countSpan.innerText = '0 items';
        if (subtotalSpan) subtotalSpan.innerText = '$0.00';
        if (vatSpan) vatSpan.innerText = '$0.00';
        if (totalSpan) totalSpan.innerText = '$0.00';
        if (checkoutBtn) checkoutBtn.disabled = true;
        if (cartBadge) {
            cartBadge.innerText = '0';
            cartBadge.style.display = 'none';
        }
        return;
    }

    let subtotal = 0;
    let totalItemsCount = 0;

    if (container) {
        container.innerHTML = state.cart.items.map(item => {
            const itemTotal = item.quantity * item.price;
            subtotal += itemTotal;
            totalItemsCount += item.quantity;
            
            let unitPriceLabel = "unit price";
            if (state.lang === 'so') unitPriceLabel = "halkii xabbo";
            
            return `
                <div class="cart-item-large-row">
                    <div class="cart-item-details">
                        <div class="cart-item-name" style="font-weight:700;">${item.name}</div>
                        <div class="cart-item-price-sub" style="font-size:0.85rem; color:var(--text-secondary);">$${item.price.toFixed(2)} ${unitPriceLabel}</div>
                    </div>
                    <div class="cart-item-actions">
                        <div class="quantity-control">
                            <button class="qty-btn" onclick="changeCartQty(${item.product_id}, -1)">-</button>
                            <span class="qty-val">${item.quantity}</span>
                            <button class="qty-btn" onclick="changeCartQty(${item.product_id}, 1)">+</button>
                        </div>
                        <div class="cart-item-total-price" style="font-weight:700;">$${itemTotal.toFixed(2)}</div>
                    </div>
                </div>
            `;
        }).join('');
    } else {
        state.cart.items.forEach(item => {
            subtotal += item.quantity * item.price;
            totalItemsCount += item.quantity;
        });
    }

    const vat = subtotal * 0.15;
    const total = subtotal + vat;

    if (countSpan) countSpan.innerText = `${totalItemsCount} item(s)`;
    if (subtotalSpan) subtotalSpan.innerText = `$${subtotal.toFixed(2)}`;
    if (vatSpan) vatSpan.innerText = `$${vat.toFixed(2)}`;
    if (totalSpan) totalSpan.innerText = `$${total.toFixed(2)}`;
    if (checkoutBtn) checkoutBtn.disabled = false;
    
    if (cartBadge) {
        cartBadge.innerText = totalItemsCount;
        cartBadge.style.display = 'inline-flex';
    }
}

// Add Item to Cart (via PL/SQL Procedure simulation)
async function addToCart(productId, quantity = 1) {
    logConsole(`EXEC pkg_order_management.add_item_to_cart(p_cart_id => ${state.cart.cart_id || 'NULL'}, p_product_id => ${productId}, p_quantity => ${quantity});`, "query");
    
    try {
        const res = await fetch(`${API_BASE}/cart/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: state.activeUserId,
                product_id: productId,
                quantity: quantity
            })
        });
        
        const result = await res.json();
        
        if (result.success) {
            logConsole(result.message, "success");
            showToast("Item added to cart!", "success");
            await fetchCart();
        } else {
            logConsole(result.message, "error");
            showToast(result.error || "Cillad ayaa dhacday", "error");
        }
    } catch (err) {
        logConsole(`Error adding to cart: ${err.message}`, "error");
        showToast("Server connection error!", "error");
    }
}

// Adjust cart qty
async function changeCartQty(productId, delta) {
    await addToCart(productId, delta);
}
// Payment Modal Functions
let currentPaymentOrderId = null;
let currentPaymentAmount = 0;

function openPaymentModal(orderId = null, amount = 0, items = []) {
    currentPaymentOrderId = orderId;
    currentPaymentAmount = amount;
    
    if (!orderId && (!state.cart.items || state.cart.items.length === 0)) return;
    
    const modal = document.getElementById('payment-modal');
    const summary = document.getElementById('payment-cart-summary');
    const totalEl = document.getElementById('payment-total-amount');
    
    let total = 0;
    
    if (orderId) {
        // Paying for an existing order
        total = amount;
        summary.innerHTML = items.map(item => `
            <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem; font-size:0.9rem;">
                <span>${item.name}</span>
                <span style="font-weight:600;">$${(item.price * item.quantity).toFixed(2)}</span>
            </div>
        `).join('');
    } else {
        // Checking out from cart
        summary.innerHTML = state.cart.items.map(item => {
            const itemTotal = item.quantity * item.price;
            total += itemTotal;
            return `
                <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem; font-size:0.9rem;">
                    <span>${item.quantity}x ${item.name}</span>
                    <span style="font-weight:600;">$${itemTotal.toFixed(2)}</span>
                </div>
            `;
        }).join('');
    }
    
    totalEl.innerText = `$${total.toFixed(2)}`;
    modal.style.display = 'flex';
}

function closePaymentModal() {
    const modal = document.getElementById('payment-modal');
    modal.style.display = 'none';
    const form = document.getElementById('payment-form');
    if (form) form.reset();
}

function confirmPayment() {
    const btn = document.getElementById('btn-confirm-payment');
    const originalText = btn.innerHTML;
    btn.innerHTML = `<svg class="spinner" viewBox="0 0 50 50" style="animation: rotate 2s linear infinite; width:20px; height:20px;"><circle class="path" cx="25" cy="25" r="20" fill="none" stroke-width="5" stroke="currentColor" stroke-linecap="round" style="animation: dash 1.5s ease-in-out infinite;"></circle></svg> Processing...`;
    btn.disabled = true;
    
    // Simulate payment gateway delay
    setTimeout(async () => {
        btn.innerHTML = originalText;
        btn.disabled = false;
        
        if (currentPaymentOrderId) {
            // Pay existing order
            try {
                const res = await fetch(`${API_BASE}/orders/pay`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ order_id: currentPaymentOrderId, amount: currentPaymentAmount })
                });
                const result = await res.json();
                if (result.success) {
                    showToast("Payment Successful!", "success");
                    await fetchOrders(); // Refresh orders
                    if (document.getElementById('payments-view') && document.getElementById('payments-view').classList.contains('active')) {
                        fetchCustomerPayments();
                    }
                } else {
                    logConsole(`Payment failed: ${result.error}`, "error");
                    showToast(`Payment failed: ${result.error}`, "error");
                }
            } catch (err) {
                logConsole(`Payment error: ${err.message}`, "error");
            }
        } else {
            // Checkout from cart
            await checkoutCart();
        }
        
        closePaymentModal();
    }, 1500);
}

// Checkout (Process bulk checkout via Oracle PL/SQL package)
async function checkoutCart() {
    if (!state.activeUserId) return;
    
    logConsole(`EXEC pkg_order_management.process_bulk_checkout(p_cart_id => ${state.cart.cart_id}, p_user_id => ${state.activeUserId}, p_new_order_id => :new_order_id);`, "query");
    
    try {
        const res = await fetch(`${API_BASE}/cart/checkout`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: state.activeUserId })
        });
        
        const result = await res.json();
        
        if (result.success) {
            logConsole(`${result.message} (Order ID: ${result.order_id}, Total: $${result.total_amount})`, "success");
            showToast(`Your order has been submitted! Order ID: #${result.order_id}`, "success");
            
            // Copy cart items before clearing the cart
            const cartItemsCopy = [...(state.cart && state.cart.items ? state.cart.items : [])];
            
            await fetchCart();
            await fetchOrders();
            
            // Display the beautiful receipt modal
            openReceiptModal(result.order_id, result.total_amount, cartItemsCopy);
        } else {
            logConsole(`Checkout failed: ${result.error}`, "error");
            showToast(result.error || "Gudbinta dalabka wuu fashilmay", "error");
        }
    } catch (err) {
        logConsole(`Checkout error: ${err.message}`, "error");
        showToast("Server connection error!", "error");
    }
}

function openReceiptModal(orderId, totalAmount, items) {
    document.getElementById('receipt-order-id').innerText = `#${orderId}`;
    document.getElementById('receipt-date').innerText = new Date().toLocaleString();
    document.getElementById('receipt-customer').innerText = state.currentUser ? state.currentUser.name : 'Customer';
    document.getElementById('receipt-subtotal').innerText = `$${totalAmount.toFixed(2)}`;
    document.getElementById('receipt-total').innerText = `$${totalAmount.toFixed(2)}`;
    
    // Barcode number (simulated using orderId + padding)
    const padding = "000000000000";
    const barcode = (padding + orderId).slice(-12);
    document.getElementById('receipt-barcode-number').innerText = barcode.split('').join(' ');

    const itemsContainer = document.getElementById('receipt-items');
    itemsContainer.innerHTML = '';
    
    items.forEach(item => {
        const itemRow = document.createElement('div');
        itemRow.style.display = 'flex';
        itemRow.style.justifyContent = 'space-between';
        
        // Product Name and quantity
        const namePart = document.createElement('span');
        namePart.innerText = `${item.PRODUCT_NAME.toUpperCase()} x${item.QUANTITY}`;
        
        // Total price
        const pricePart = document.createElement('span');
        pricePart.innerText = `$${(item.PRICE * item.QUANTITY).toFixed(2)}`;
        
        itemRow.appendChild(namePart);
        itemRow.appendChild(pricePart);
        itemsContainer.appendChild(itemRow);
    });

    document.getElementById('receipt-modal').style.display = 'flex';
}

function closeReceiptModal() {
    document.getElementById('receipt-modal').style.display = 'none';
}

// Fetch orders history (Storefront)
async function fetchOrders() {
    if (!state.activeUserId) return;
    
    logConsole(`SELECT * FROM orders WHERE user_id = ${state.activeUserId} ORDER BY order_id DESC;`, "query");
    try {
        const res = await fetch(`${API_BASE}/orders/${state.activeUserId}`);
        if (!res.ok) throw new Error("Failed to load orders");
        state.orders = await res.json();
        renderOrders();
    } catch (err) {
        logConsole(`Error fetching orders: ${err.message}`, "error");
    }
}

// Render Orders list (Storefront)
function renderOrders() {
    const container = document.getElementById('orders-large-container');
    if (!container) return;

    if (state.orders.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom:1rem; color:var(--text-muted);"><rect width="16" height="20" x="4" y="2" rx="2"/><line x1="8" x2="16" y1="6" y2="6"/><line x1="8" x2="16" y1="10" y2="10"/><line x1="8" x2="16" y1="14" y2="14"/><line x1="8" x2="12" y1="18" y2="18"/></svg>
                <h3>${translations[state.lang].orders_empty_title}</h3>
                <p>${translations[state.lang].orders_empty_desc}</p>
            </div>
        `;
        return;
    }

    container.innerHTML = state.orders.map(order => {
        const itemsList = order.items.map(item => 
            `<div class="order-large-item-row" style="display:flex; justify-content:space-between; padding:0.5rem 0; border-bottom:1px dashed var(--border-color);">
                <span>${item.name} (x${item.quantity})</span>
                <span style="font-weight: 600;">$${(item.price * item.quantity).toFixed(2)}</span>
            </div>`
        ).join('');
        
        let statusColor = 'var(--status-pending)';
        let statusBg = 'var(--status-pending-bg)';
        if (order.status === 'Completed') {
            statusColor = 'var(--status-completed)';
            statusBg = 'var(--status-completed-bg)';
        } else if (order.status === 'Shipped') {
            statusColor = 'var(--status-shipped)';
            statusBg = 'var(--status-shipped-bg)';
        } else if (order.status === 'Cancelled') {
            statusColor = 'var(--status-cancelled)';
            statusBg = 'var(--status-cancelled-bg)';
        }
        
        let statusName = order.status;
        if (state.lang === 'so') {
            if (order.status === 'Pending') statusName = 'In la sugayo';
            else if (order.status === 'Completed') statusName = 'La dhamaystiray';
            else if (order.status === 'Shipped') statusName = 'La raray';
            else if (order.status === 'Cancelled') statusName = 'La baajiyay';
        
    if (filtered.length === 0) {
        container.innerHTML = `
            <div class="empty-state" style="grid-column: 1/-1;">
                <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom:1rem; color:var(--text-muted);"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
                <h3>Alaabta lama helin</h3>
                <p>Ma jiraan alaabo ku habboon shaandhayntaada ama raadintaada.</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = filtered.map(p => {
        // Choose nice gradient backgrounds and emoji icons based on category/name
        let bgGrad = 'linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%)';
        let emoji = '📦';
        const nameLower = p.name.toLowerCase();
        const catNameLower = (p.category_name || '').toLowerCase();
        
        if (catNameLower.includes('electron') || nameLower.includes('phone') || nameLower.includes('watch') || nameLower.includes('camera') || nameLower.includes('headphone')) {
            bgGrad = 'linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%)';
            emoji = '💻';
            if (nameLower.includes('watch')) emoji = '⌚';
            if (nameLower.includes('camera')) emoji = '📷';
            if (nameLower.includes('headphone')) emoji = '🎧';
        } else if (catNameLower.includes('cloth') || nameLower.includes('shirt') || nameLower.includes('jean') || nameLower.includes('jacket')) {
            bgGrad = 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)';
            emoji = '👕';
        } else if (catNameLower.includes('footwear') || nameLower.includes('shoe') || nameLower.includes('sneaker')) {
            bgGrad = 'linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%)';
            emoji = '👟';
        } else if (catNameLower.includes('access') || nameLower.includes('bag') || nameLower.includes('belt') || nameLower.includes('wallet')) {
            bgGrad = 'linear-gradient(135deg, #f3e8ff 0%, #e9d5ff 100%)';
            emoji = '👜';
        }

        let productDesc = "Murasad tayo sare leh oo ka mid ah alaabooyinka asalka ah ee shirkadda.";
        if (state.lang === 'en') productDesc = "High-quality premium product from our official inventory.";

        let addBtnText = "+ Add";
        if (state.lang === 'so') addBtnText = "+ Ku Dar";

        let premiumBadge = "Premium";

        let displayCatName = p.category_name || 'OTHERS';

        // Add real image URL rendering:
        let bgStyle = bgGrad;
        let innerHtml = `
            <div class="product-image" style="background: ${bgStyle};">
                <span style="font-size:3rem; filter:drop-shadow(0 4px 6px rgba(0,0,0,0.1));">${emoji}</span>
            </div>
        `;
        
        if (p.image_url) {
            const firstImage = p.image_url.split(',')[0];
            innerHtml = `
                <div class="product-image" style="background: url('${API_BASE.replace('/api', '')}/uploads/${firstImage}') center/cover;">
                </div>
            `;
        }

        return `
            <div class="product-card">
                ${innerHtml}
                <div class="product-info">
                    <span class="category-pill">${displayCatName}</span>
                    <h3 class="product-title">${p.name}</h3>
                    <p class="product-price">$${parseFloat(p.price).toFixed(2)}</p>
                    <button class="btn-primary" style="width:100%; margin-top:0.5rem;" onclick="addToCart(${p.product_id}, '${p.name.replace(/'/g, "\\'")}', ${p.price})">
                        + Add to Cart
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

function renderCategories() {
    const container = document.getElementById('categories-container');
    if (!container) return;
    
    container.innerHTML = state.categories.map(c => {
        let icon = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 0.5rem;"><rect width="7" height="7" x="3" y="3" rx="1"/><rect width="7" height="7" x="14" y="3" rx="1"/><rect width="7" height="7" x="14" y="14" rx="1"/><rect width="7" height="7" x="3" y="14" rx="1"/></svg>`;
        
        const nameLower = c.category_name.toLowerCase();
        if (nameLower.includes('electron')) {
            icon = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 0.5rem;"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>`;
        } else if (nameLower.includes('cloth') || nameLower.includes('jean') || nameLower.includes('shirt')) {
            icon = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 0.5rem;"><path d="M20.38 3.46 16 7.83V5.5a1 1 0 0 0-1-1H9a1 1 0 0 0-1 1v2.33L3.62 3.46a1 1 0 0 0-1.41 0L1 4.67a1 1 0 0 0 0 1.41L5 10.09V21a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V10.09l4-4.01a1 1 0 0 0 0-1.41l-1.21-1.21a1 1 0 0 0-1.41 0Z"/></svg>`;
        } else if (nameLower.includes('footwear') || nameLower.includes('shoe')) {
            icon = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 0.5rem;"><path d="M3 12h18M3 16h18M4 4h16a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2Z"/></svg>`;
        } else if (nameLower.includes('access')) {
            icon = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 0.5rem;"><circle cx="12" cy="12" r="10"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>`;
        }
        
        let displayCatName = c.category_name;
        
        return `
            <div class="category-card" onclick="document.getElementById('search-input').value = '${c.category_name}'; filterProducts();">
                ${icon} ${displayCatName}
            </div>
        `;
    }).join('');
}

async function resetSystem() {

    if (!confirm("Ma xaqiijineysaa in aad dib u bilowdo (Reset) dhamaan shaxaha iyo xogta database-ka?")) return;
    
    logConsole("Initializing complete database rebuild schema...", "info");
    showToast("Rebuilding Oracle DB Schema...", "info");
    
    try {
        const res = await fetch(`${API_BASE}/db/reset`, { method: 'POST' });
        const result = await res.ok ? await res.json() : null;
        
        if (result && result.success) {
            logConsole(result.message, "success");
            showToast("Database-kii dib ayuu u dhashay!", "success");
            
            // Reload all
            await fetchUsers();
            await fetchProductsAndCategories();
            
            const adminUser = state.users.find(u => u.user_id === state.activeUserId);
            if (adminUser) {
                loginUserSession(adminUser);
            }
        } else {
            const errText = result ? result.error : "Unknown backend error";
            logConsole(`Database reset failed: ${errText}`, "error");
            showToast("Rebuild failed!", "error");
        }
    } catch (err) {
        logConsole(`Database reset connection failed: ${err.message}`, "error");
        showToast("Backend connection failed!", "error");
    }
}

// Render Permissions tab dashboard
function renderPermissionsView() {
    const user = state.users.find(u => u.user_id === state.activeUserId);
    if (!user) return;

    // Profile Details
    const nameEl = document.getElementById('perm-user-name');
    const emailEl = document.getElementById('perm-user-email');
    const badgeEl = document.getElementById('perm-user-role-badge');
    const roleTextEl = document.getElementById('perm-role-text');

    if (nameEl) nameEl.innerText = user.name;
    if (emailEl) emailEl.innerText = user.email;
    if (badgeEl) {
        badgeEl.innerText = user.role.toUpperCase();
        badgeEl.className = `role-badge role-${user.role}`;
    }
    if (roleTextEl) {
        if (user.role === 'admin') {
            if (state.lang === 'en') {
                roleTextEl.innerHTML = `The <strong>Admin</strong> role grants full system control. You have read/write access to all system data, can insert products, update order status, and reset the database schema.`;
            } else {
                roleTextEl.innerHTML = `Booska <strong>Admin-ka</strong> wuxuu ku siinayaa maamul buuxa oo nidaamka ah. Waxaad akhrin kartaa oo wax ka beddeli kartaa dhammaan xogta, waxaad ku dari kartaa alaab, beddeli kartaa heerka dalabka, iyo dib-u-dhiska database-ka.`;
            }
        } else {
            if (state.lang === 'en') {
                roleTextEl.innerHTML = `The <strong>Customer</strong> role allows you to browse the catalog, manage your shopping cart, checkout orders, and view your payment history.`;
            } else {
                roleTextEl.innerHTML = `Booska <strong>Customer-ka</strong> wuxuu kuu ogolaanayaa inaad dhex gasho qaybaha alaabta, maamusho gaarigaaga dukaameysiga, gudbiso dalabaadka, iyo inaad aragto taariikhdaada lacag-bixinta.`;
            }
        }
    }

    // Application Policy Matrix
    const renderStatus = (elementId, isAllowed) => {
        const el = document.getElementById(elementId);
        if (!el) return;
        const yesText = translations[state.lang].policy_yes;
        const noText = translations[state.lang].policy_no;
        if (isAllowed) {
            el.className = 'policy-status status-allowed';
            el.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg> ${yesText}`;
        } else {
            el.className = 'policy-status status-denied';
            el.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg> ${noText}`;
        }
    };

    const isAdmin = user.role === 'admin';
    renderStatus('policy-browse', true);
    renderStatus('policy-checkout', true);
    renderStatus('policy-add-product', isAdmin);
    renderStatus('policy-update-status', isAdmin);
    renderStatus('policy-view-tables', isAdmin);

    // Oracle System Privileges
    const systemPrivsBody = document.getElementById('system-privs-body');
    if (systemPrivsBody) {
        const sysPrivs = [
            { priv: 'CREATE SESSION', type: 'System Connection', allowedForCust: true, allowedForAdmin: true },
            { priv: 'CREATE TABLE', type: 'DDL Schema Creation', allowedForCust: false, allowedForAdmin: true },
            { priv: 'CREATE TRIGGER', type: 'Database Automation', allowedForCust: false, allowedForAdmin: true },
            { priv: 'CREATE PROCEDURE', type: 'PL/SQL Packages', allowedForCust: false, allowedForAdmin: true },
            { priv: 'GRANT ANY ROLE', type: 'Security Administration', allowedForCust: false, allowedForAdmin: true }
        ];

        systemPrivsBody.innerHTML = sysPrivs.map(sp => {
            const hasPriv = isAdmin ? sp.allowedForAdmin : sp.allowedForCust;
            const grantedText = state.lang === 'en' ? 'GRANTED' : (state.lang === 'ar' ? 'ممنوح' : 'GRANTED');
            const deniedText = state.lang === 'en' ? 'DENIED' : (state.lang === 'ar' ? 'مرفوض' : 'DENIED');
            
            const statusBadge = hasPriv 
                ? `<span class="policy-status status-allowed" style="font-size:0.7rem; padding:0.15rem 0.5rem;"><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg> ${grantedText}</span>`
                : `<span class="policy-status status-denied" style="font-size:0.7rem; padding:0.15rem 0.5rem;"><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg> ${deniedText}</span>`;
            return `
                <tr>
                    <td style="font-family:'Courier New', Courier, monospace; font-weight: 600;">${sp.priv}</td>
                    <td>${sp.type}</td>
                    <td>${statusBadge}</td>
                </tr>
            `;
        }).join('');
    }

    // Oracle Object Privileges
    const objectPrivsBody = document.getElementById('object-privs-body');
    if (objectPrivsBody) {
        const checkIcon = `<span style="color:#10b981; font-weight:bold; font-size:1.1rem;">✓</span>`;
        const lockIcon = `<span style="color:#ef4444; font-size:1rem;">🔒</span>`;
        
        const objPrivs = [
            { name: 'USERS', sel: true, ins: isAdmin, upd: true, exe: false },
            { name: 'CATEGORIES', sel: true, ins: isAdmin, upd: isAdmin, exe: false },
            { name: 'PRODUCTS', sel: true, ins: isAdmin, upd: isAdmin, exe: false },
            { name: 'CART & ITEMS', sel: true, ins: true, upd: true, exe: false },
            { name: 'ORDERS & ITEMS', sel: true, ins: true, upd: isAdmin, exe: false },
            { name: 'ORDER_AUDIT_LOGS', sel: isAdmin, ins: false, upd: false, exe: false },
            { name: 'PKG_ORDER_MANAGEMENT', sel: false, ins: false, upd: false, exe: true }
        ];

        objectPrivsBody.innerHTML = objPrivs.map(op => {
            return `
                <tr>
                    <td style="font-family:'Courier New', Courier, monospace; font-weight: 600;">${op.name}</td>
                    <td style="text-align: center;">${op.sel ? checkIcon : lockIcon}</td>
                    <td style="text-align: center;">${op.ins ? checkIcon : lockIcon}</td>
                    <td style="text-align: center;">${op.upd ? checkIcon : lockIcon}</td>
                    <td style="text-align: center;">${op.exe ? checkIcon : (op.sel || op.ins || op.upd ? 'N/A' : lockIcon)}</td>
                </tr>
            `;
        }).join('');
    }
}

// Theme Toggle
function toggleTheme() {
    if (state.theme === 'dark') {
        state.theme = 'light';
        document.documentElement.setAttribute('data-theme', 'light');
    } else {
        state.theme = 'dark';
        document.documentElement.setAttribute('data-theme', 'dark');
    }
    localStorage.setItem('theme', state.theme);
    updateThemeToggleIcon();
}

function updateThemeToggleIcon() {
    const btn = document.getElementById('theme-toggle');
    if (!btn) return;
    
    if (state.theme === 'light') {
        btn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>`;
    } else {
        btn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>`;
    }
}

// Views Navigation (Storefront tabs)
function switchView(viewName) {
    // Allow all logged-in users to access profile view to see their permissions

    document.querySelectorAll('.view-section').forEach(sec => {
        if (sec.id === `${viewName}-view`) sec.classList.add('active');
        else sec.classList.remove('active');
    });

    document.querySelectorAll('.nav-tab-btn').forEach(btn => {
        if (btn.dataset.view === viewName) btn.classList.add('active');
        else btn.classList.remove('active');
    });
    
    logConsole(`Switched storefront panel view to: ${viewName.toUpperCase()}`, "info");

    if (viewName === 'categories') {
        renderCategoryFilters();
        renderProducts();
    } else if (viewName === 'cart') {
        fetchCart();
    } else if (viewName === 'orders') {
        fetchOrders();
    } else if (viewName === 'payments') {
        fetchCustomerPayments();
    } else if (viewName === 'profile') {
        renderPermissionsView();
    }
}

// Fetch payments history (Storefront)
async function fetchCustomerPayments() {
    if (!state.activeUserId) return;
    
    logConsole(`SELECT * FROM payments WHERE user_id = ${state.activeUserId}`, "query");
    try {
        const res = await fetch(`${API_BASE}/payments/user/${state.activeUserId}`);
        if (!res.ok) throw new Error("Failed to load payments");
        const data = await res.json();
        state.customerPayments = data.payments || [];
        renderCustomerPayments();
    } catch (err) {
        logConsole(`Error fetching payments: ${err.message}`, "error");
    }
}

function renderCustomerPayments() {
    const tbody = document.getElementById('customer-payments-body');
    if (!tbody) return;

    if (!state.customerPayments || state.customerPayments.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; padding: 2rem;">
            <h3>${translations[state.lang].payments_empty_title}</h3>
            <p>${translations[state.lang].payments_empty_desc}</p>
        </td></tr>`;
        return;
    }

    tbody.innerHTML = state.customerPayments.map(p => `
        <tr style="border-bottom: 1px solid var(--border-color);">
            <td style="padding:0.75rem;"><strong>#${p.payment_id}</strong></td>
            <td style="padding:0.75rem;">Order #${p.order_id} (${p.status})</td>
            <td style="padding:0.75rem; font-weight:bold; color:var(--primary-color);">
                $${p.amount.toFixed(2)}
            </td>
            <td style="padding:0.75rem; color:var(--text-muted);">
                ${p.payment_date}
            </td>
        </tr>
    `).join('');
}


// ============================================================
//   ADMIN CONSOLE WORKSPACE & SUB-VIEWS LOGIC
// ============================================================

// Fetch Admin Dashboard stat counters
async function fetchAdminStats() {
    try {
        const ordersRes = await fetch(`${API_BASE}/admin/table/orders`);
        const ordersData = await ordersRes.json();
        const paymentsRes = await fetch(`${API_BASE}/admin/table/payments`);
        const paymentsData = await paymentsRes.json();

        const usersCount = state.users.length;
        const productsCount = state.products.length;
        const ordersCount = ordersData.rows ? ordersData.rows.length : 0;
        
        let revenue = 0;
        if (paymentsData.rows) {
            paymentsData.rows.forEach(p => {
                const amt = parseFloat(p.amount || 0);
                revenue += amt;
            });
        }

        document.getElementById('stat-total-users').innerText = usersCount;
        document.getElementById('stat-total-products').innerText = productsCount;
        document.getElementById('stat-total-orders').innerText = ordersCount;
        document.getElementById('stat-total-revenue').innerText = `$${revenue.toFixed(2)}`;
        
        // Fetch Analytics for Charts
        const analyticsRes = await fetch(`${API_BASE}/analytics`);
        const analyticsData = await analyticsRes.json();
        
        if (analyticsData.success) {
            renderDashboardCharts(analyticsData.sales_over_time, analyticsData.revenue_by_category);
        }

    } catch (err) {
        console.error("Error fetching admin stats:", err);
    }
}

let salesChartInstance = null;
let categoryChartInstance = null;

function renderDashboardCharts(salesData, categoryData) {
    const salesCtx = document.getElementById('salesChart');
    const catCtx = document.getElementById('categoryChart');
    
    if (!salesCtx || !catCtx) return;
    
    if (salesChartInstance) salesChartInstance.destroy();
    if (categoryChartInstance) categoryChartInstance.destroy();
    
    // Theme colors for charts
    const textColor = getComputedStyle(document.documentElement).getPropertyValue('--text-primary').trim() || '#1e293b';
    const gridColor = getComputedStyle(document.documentElement).getPropertyValue('--border-color').trim() || '#e2e8f0';
    
    // Sales Chart (Line)
    salesChartInstance = new Chart(salesCtx, {
        type: 'line',
        data: {
            labels: salesData.map(d => d.date),
            datasets: [{
                label: 'Daily Revenue ($)',
                data: salesData.map(d => d.revenue),
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                borderWidth: 3,
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: textColor }, grid: { display: false } },
                y: { ticks: { color: textColor }, grid: { color: gridColor } }
            }
        }
    });
    
    // Category Chart (Doughnut)
    const catLabels = categoryData.map(d => d.category);
    const catValues = categoryData.map(d => d.revenue);
    const colors = ['#3b82f6', '#ec4899', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444'];
    
    categoryChartInstance = new Chart(catCtx, {
        type: 'doughnut',
        data: {
            labels: catLabels,
            datasets: [{
                data: catValues,
                backgroundColor: colors.slice(0, catLabels.length),
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'right', labels: { color: textColor } }
            },
            cutout: '70%'
        }
    });
}

// Fetch and render specific sidebar views
async function loadSubViewData(subviewName) {
    logConsole(`Loading Admin subview: ${subviewName.toUpperCase()}`, "info");
    
    try {
        if (subviewName === 'dashboard') {
            await fetchAdminStats();
        } 
        else if (subviewName === 'products') {
            const res = await fetch(`${API_BASE}/admin/table/products`);
            const data = await res.json();
            state.adminProductsList = data.rows || [];
            
            // Populate category select in product creation form
            const categorySelect = document.getElementById('admin-prod-category');
            if (categorySelect) {
                categorySelect.innerHTML = state.categories.map(c => 
                    `<option value="${c.category_id}">${c.category_name} (ID: ${c.category_id})</option>`
                ).join('');
            }
            renderAdminProductsTable();
        } 
        else if (subviewName === 'categories') {
            const catRes = await fetch(`${API_BASE}/admin/table/categories`);
            const catData = await catRes.json();
            state.adminCategoriesList = catData.rows || [];
            renderAdminCategoriesTable();
        } 
        else if (subviewName === 'orders') {
            const res = await fetch(`${API_BASE}/admin/table/orders`);
            const data = await res.json();
            
            const itemsRes = await fetch(`${API_BASE}/admin/table/order_items`);
            const itemsData = await itemsRes.json();

            state.adminOrdersList = data.rows || [];
            state.adminOrderItemsList = itemsData.rows || [];
            renderAdminOrdersTable();
        } 
        else if (subviewName === 'users') {
            const res = await fetch(`${API_BASE}/admin/table/users`);
            const data = await res.json();
            
            const ordersRes = await fetch(`${API_BASE}/admin/table/orders`);
            const ordersData = await ordersRes.json();

            state.adminUsersList = data.rows || [];
            state.adminOrdersList = ordersData.rows || [];
            renderAdminUsersTable();
        } 
        else if (subviewName === 'payments') {
            const res = await fetch(`${API_BASE}/admin/table/payments`);
            const data = await res.json();
            state.adminPaymentsList = data.rows || [];
            renderAdminPaymentsTable();
        } 
        else if (subviewName === 'audit') {
            const res = await fetch(`${API_BASE}/audit-logs`);
            const data = await res.json();
            state.adminAuditList = data || [];
            renderAdminAuditTable();
        }
    } catch (err) {
        logConsole(`Error loading admin view data: ${err.message}`, "error");
    }
}

// Helpers for initials avatars
function getInitials(name) {
    if (!name) return 'U';
    const parts = name.split(' ');
    if (parts.length >= 2) {
        return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return name.slice(0, 2).toUpperCase();
}

// Helpers for category visual icons
function getProductIcon(categoryName) {
    const name = categoryName ? categoryName.toLowerCase() : '';
    if (name.includes('elect')) {
        return `<div class="avatar-circle" style="background:rgba(99,102,241,0.08); border-color:rgba(99,102,241,0.2); color:#818cf8;">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="20" x="5" y="2" rx="2"/><path d="M12 18h.01"/></svg>
        </div>`;
    } else if (name.includes('cloth') || name.includes('wear')) {
        return `<div class="avatar-circle" style="background:rgba(236,72,153,0.08); border-color:rgba(236,72,153,0.2); color:#f472b6;">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20.38 3.46 16 7.83V4a2 2 0 0 0-2-2H2a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3.83l4.38 4.37a2 2 0 0 0 3.42-1.41V4.87a2 2 0 0 0-3.42-1.41z"/></svg>
        </div>`;
    } else if (name.includes('book')) {
        return `<div class="avatar-circle" style="background:rgba(16,185,129,0.08); border-color:rgba(16,185,129,0.2); color:#34d399;">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z"/><path d="M6 6h10M6 10h10"/></svg>
        </div>`;
    } else if (name.includes('home') || name.includes('kitchen') || name.includes('appl')) {
        return `<div class="avatar-circle" style="background:rgba(245,158,11,0.08); border-color:rgba(245,158,11,0.2); color:#fbbf24;">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M17 8h1a4 4 0 1 1 0 8h-1"/><path d="M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z"/><line x1="6" x2="6" y1="2" y2="4"/><line x1="10" x2="10" y1="2" y2="4"/><line x1="14" x2="14" y1="2" y2="4"/></svg>
        </div>`;
    } else if (name.includes('sport') || name.includes('fit')) {
        return `<div class="avatar-circle" style="background:rgba(59,130,246,0.08); border-color:rgba(59,130,246,0.25); color:#60a5fa;">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
        </div>`;
    } else {
        return `<div class="avatar-circle" style="background:rgba(107,114,128,0.08); border-color:rgba(107,114,128,0.2); color:#9ca3af;">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/></svg>
        </div>`;
    }
}

function getCategoryPillClass(categoryName) {
    const name = categoryName ? categoryName.toLowerCase() : '';
    if (name.includes('elect')) return 'cat-electronics';
    if (name.includes('cloth') || name.includes('wear')) return 'cat-clothing';
    if (name.includes('book')) return 'cat-books';
    if (name.includes('home') || name.includes('kitchen')) return 'cat-home';
    if (name.includes('sport') || name.includes('fit')) return 'cat-sports';
    return 'cat-other';
}

// Toggle drawer panels
function toggleAddProductForm() {
    const panel = document.getElementById('product-form-panel');
    if (panel) panel.classList.toggle('active');
}

function toggleAddCategoryForm() {
    const panel = document.getElementById('category-form-panel');
    if (panel) panel.classList.toggle('active');
}

// CRUD: Deletion APIs
async function deleteProduct(productId) {
    if (!confirm("Ma xaqiijineysaa in aad tirtirto badeecadan?")) return;
    logConsole(`DELETE FROM products WHERE product_id = ${productId};`, "query");
    
    try {
        const res = await fetch(`${API_BASE}/products/delete/${productId}`, { method: 'POST' });
        const result = await res.json();
        if (result.success) {
            showToast("Product deleted!", "success");
            await fetchProductsAndCategories(); // Refresh local list
            await loadSubViewData('products'); // Refresh table
        } else {
            showToast("Deletion failed!", "error");
        }
    } catch (err) {
        showToast("Server connection error!", "error");
    }
}

async function deleteCategory(categoryId) {
    if (!confirm("Ma xaqiijineysaa in aad tirtirto qaybtaan? (Fiiro gaar ah: waxay saamayn kartaa alaabta ku xiran)")) return;
    logConsole(`DELETE FROM categories WHERE category_id = ${categoryId};`, "query");
    
    try {
        const res = await fetch(`${API_BASE}/categories/delete/${categoryId}`, { method: 'POST' });
        const result = await res.json();
        if (result.success) {
            showToast("Category deleted!", "success");
            await fetchProductsAndCategories();
            await loadSubViewData('categories');
        } else {
            showToast("Ma tirtiri kartid category leh alaab ku xiran!", "error");
        }
    } catch (err) {
        showToast("Server connection error!", "error");
    }
}

async function deleteUser(userId) {
    if (userId === state.activeUserId) {
        showToast("Ma tirtiri kartid naftaada!", "error");
        return;
    }
    if (!confirm("Ma xaqiijineysaa in aad tirtirto isticmaalahan?")) return;
    logConsole(`DELETE FROM users WHERE user_id = ${userId};`, "query");
    
    try {
        const res = await fetch(`${API_BASE}/users/delete/${userId}`, { method: 'POST' });
        const result = await res.json();
        if (result.success) {
            showToast("User deleted!", "success");
            await fetchUsers();
            await loadSubViewData('users');
        } else {
            showToast("Deletion failed!", "error");
        }
    } catch (err) {
        showToast("Server connection error!", "error");
    }
}

// Rendering Functions for Admin subviews
function renderAdminProductsTable() {
    const tbody = document.getElementById('admin-products-body');
    const countBadge = document.getElementById('admin-products-count');
    if (!tbody) return;

    const query = state.adminSearchQueries.products.toLowerCase();
    const filtered = state.adminProductsList.filter(p => p.name.toLowerCase().includes(query));

    countBadge.innerText = filtered.length;

    if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; padding:2rem;">Alaab laguma helin baaritaanka</td></tr>`;
        return;
    }

    tbody.innerHTML = filtered.map(p => {
        const catClass = getCategoryPillClass(p.category_name);
        let iconHtml = getProductIcon(p.category_name);
        if (p.image_url) {
            const firstImage = p.image_url.split(',')[0];
            iconHtml = `<div class="avatar-circle" style="background: url('${API_BASE.replace('/api', '')}/uploads/${firstImage}') center/cover; border: 1px solid var(--border-color);"></div>`;
        }
        return `
            <tr>
                <td>
                    <div class="name-with-avatar">
                        ${iconHtml}
                        <span>${p.name}</span>
                    </div>
                </td>
                <td><span class="category-pill ${catClass}">${p.category_name || 'Others'}</span></td>
                <td>$${parseFloat(p.price).toFixed(2)}</td>
                <td style="text-align: right;">
                    <button class="btn-action" onclick="populateProductEdit('${p.name}', ${p.price}, ${p.category_id})" title="Edit product"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg></button>
                    <button class="btn-action btn-delete" onclick="deleteProduct(${p.product_id})" title="Delete product"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg></button>
                </td>
            </tr>
        `;
    }).join('');
}

function populateProductEdit(name, price, categoryId) {
    const nameInput = document.getElementById('admin-prod-name');
    const priceInput = document.getElementById('admin-prod-price');
    const catSelect = document.getElementById('admin-prod-category');
    
    if (nameInput) nameInput.value = name.toLowerCase();
    if (priceInput) priceInput.value = price;
    if (catSelect) catSelect.value = categoryId;
    
    // Open panel
    const panel = document.getElementById('product-form-panel');
    if (panel) panel.classList.add('active');
    
    showToast("Product details filled in trigger form!", "info");
}

function renderAdminCategoriesTable() {
    const tbody = document.getElementById('admin-categories-body');
    const countBadge = document.getElementById('admin-categories-count');
    if (!tbody) return;

    // Get count of products per category
    const catCounts = {};
    state.products.forEach(p => {
        catCounts[p.category_id] = (catCounts[p.category_id] || 0) + 1;
    });

    const query = state.adminSearchQueries.categories.toLowerCase();
    const filtered = state.adminCategoriesList.filter(c => c.category_name.toLowerCase().includes(query));

    countBadge.innerText = filtered.length;

    if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; padding:2rem;">Ma jiraan categories la helay</td></tr>`;
        return;
    }

    tbody.innerHTML = filtered.map(c => {
        const pCount = catCounts[c.category_id] || 0;
        return `
            <tr>
                <td>#${c.category_id}</td>
                <td style="font-weight:600; color:var(--text-primary);">${c.category_name}</td>
                <td><strong>${pCount}</strong> products</td>
                <td style="text-align: right;">
                    <button class="btn-action btn-delete" onclick="deleteCategory(${c.category_id})" title="Delete category"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg></button>
                </td>
            </tr>
        `;
    }).join('');
}

function renderAdminOrdersTable() {
    const tbody = document.getElementById('admin-orders-body');
    const countBadge = document.getElementById('admin-orders-count');
    if (!tbody) return;

    // Map user names and order item counts
    const usersMap = {};
    state.users.forEach(u => { usersMap[u.user_id] = u.name; });

    const orderItemsCountMap = {};
    state.adminOrderItemsList.forEach(oi => {
        orderItemsCountMap[oi.order_id] = (orderItemsCountMap[oi.order_id] || 0) + parseInt(oi.quantity);
    });

    const filter = state.adminOrdersStatusFilter;
    const filtered = filter === 'all' 
        ? state.adminOrdersList 
        : state.adminOrdersList.filter(o => o.status === filter);

    countBadge.innerText = filtered.length;

    if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:2rem;">Dalabaad laguma helin status-kan</td></tr>`;
        return;
    }

    tbody.innerHTML = filtered.map(o => {
        const uName = usersMap[o.user_id] || `User #${o.user_id}`;
        const initials = getInitials(uName);
        const itemQty = orderItemsCountMap[o.order_id] || 0;
        const statusClass = `order-status-badge order-status-${o.status.toLowerCase()}`;
        
        return `
            <tr>
                <td>#${o.order_id}</td>
                <td>
                    <div class="name-with-avatar">
                        <div class="avatar-circle">${initials}</div>
                        <span>${uName}</span>
                    </div>
                </td>
                <td>$${parseFloat(o.total_amount).toFixed(2)}</td>
                <td><span class="${statusClass}">${o.status}</span></td>
                <td><strong>${itemQty}</strong> items</td>
                <td style="text-align: right;">
                    <button class="btn-action" onclick="populateOrderStatusEdit(${o.order_id}, '${o.status}')" title="Change order status"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg></button>
                </td>
            </tr>
        `;
    }).join('');
}

function populateOrderStatusEdit(orderId, status) {
    const idInput = document.getElementById('admin-status-order-id');
    const valSelect = document.getElementById('admin-status-value');
    
    if (idInput) idInput.value = orderId;
    if (valSelect) valSelect.value = status;
    
    showToast("Order ID filled in status update form!", "info");
}

function renderAdminUsersTable() {
    const tbody = document.getElementById('admin-users-body');
    const countBadge = document.getElementById('admin-users-count-badge');
    if (!tbody) return;

    // Count user orders
    const ordersCountMap = {};
    state.adminOrdersList.forEach(o => {
        ordersCountMap[o.user_id] = (ordersCountMap[o.user_id] || 0) + 1;
    });

    const query = state.adminSearchQueries.users.toLowerCase();
    const filtered = state.adminUsersList.filter(u => u.name.toLowerCase().includes(query) || u.email.toLowerCase().includes(query));

    countBadge.innerText = filtered.length;

    if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:2rem;">Isticmaalayaal laguma helin baaritaanka</td></tr>`;
        return;
    }

    tbody.innerHTML = filtered.map(u => {
        const initials = getInitials(u.name);
        const orderQty = ordersCountMap[u.user_id] || 0;
        
        return `
            <tr>
                <td>#${u.user_id}</td>
                <td>
                    <div class="name-with-avatar">
                        <div class="avatar-circle" style="background:rgba(16,185,129,0.08); color:#10b981; border-color:rgba(16,185,129,0.2);">${initials}</div>
                        <span style="font-weight:600;">${u.name} ${u.role === 'admin' ? '<span style="font-size:0.6rem; background:rgba(16,185,129,0.15); color:#10b981; padding:1px 4px; border-radius:3px; margin-left:4px;">ADMIN</span>' : ''}</span>
                    </div>
                </td>
                <td style="font-family:monospace;">${u.email}</td>
                <td>
                    <select class="form-control" style="padding:4px 8px; font-size:0.85rem;" onchange="updateUserRole(${u.user_id}, this.value)" ${u.user_id === state.activeUserId ? 'disabled' : ''}>
                        <option value="admin" ${u.role === 'admin' ? 'selected' : ''}>Admin</option>
                        <option value="manager" ${u.role === 'manager' ? 'selected' : ''}>Manager</option>
                        <option value="customer" ${u.role === 'customer' ? 'selected' : ''}>Customer</option>
                    </select>
                </td>
                <td><strong>${orderQty}</strong> orders</td>
                <td style="text-align: right;">
                    <button class="btn-action btn-delete" onclick="deleteUser(${u.user_id})" title="Delete user" ${u.user_id === state.activeUserId ? 'disabled style="opacity:0.3; cursor:not-allowed;"' : ''}><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg></button>
                </td>
            </tr>
        `;
    }).join('');
}

async function updateUserRole(userId, newRole) {
    if (!confirm(`Are you sure you want to change this user's role to ${newRole.toUpperCase()}?`)) {
        renderAdminUsersTable(); // reset dropdown
        return;
    }
    
    try {
        const res = await apiFetch(`${API_BASE}/users/role/${userId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ role: newRole })
        });
        const result = await res.json();
        
        if (result.success) {
            showToast("Role updated successfully!", "success");
            logConsole(`Updated user #${userId} role to ${newRole}`, "success");
            // Refresh table
            const userRes = await apiFetch(`${API_BASE}/admin/table/users`);
            const data = await userRes.json();
            state.adminUsersList = data.rows || [];
            renderAdminUsersTable();
        } else {
            showToast(result.error || "Failed to update role", "error");
        }
    } catch (err) {
        showToast("Network error", "error");
        console.error(err);
    }
}

function filterAdminPayments() {
    const search = document.getElementById('search-payments');
    if (search) {
        state.adminSearchQueries.payments = search.value;
        renderAdminPaymentsTable();
    }
}

function renderAdminPaymentsTable() {
    const tbody = document.getElementById('admin-payments-body');
    const grossVolumeSpan = document.getElementById('payment-gross-volume');
    const txCountSpan = document.getElementById('payment-tx-count');
    const avgTicketSpan = document.getElementById('payment-avg-ticket');
    
    if (!tbody) return;

    const searchVal = state.adminSearchQueries?.payments?.toLowerCase() || '';
    
    let filteredList = state.adminPaymentsList || [];
    if (searchVal) {
        filteredList = filteredList.filter(p => 
            p.payment_id.toString().includes(searchVal) || 
            p.order_id.toString().includes(searchVal)
        );
    }

    if (filteredList.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding:2rem; color:var(--text-secondary);">No transactions found.</td></tr>`;
        return;
    }

    let totalVolume = 0;
    filteredList.forEach(p => totalVolume += parseFloat(p.amount || 0));
    const txCount = filteredList.length;
    const avgTicket = txCount > 0 ? totalVolume / txCount : 0;

    if (grossVolumeSpan) grossVolumeSpan.innerText = `$${totalVolume.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
    if (txCountSpan) txCountSpan.innerText = txCount;
    if (avgTicketSpan) avgTicketSpan.innerText = `$${avgTicket.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;

    const getMethod = (id) => {
        const methods = [
            '<svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="4" width="22" height="16" rx="2" ry="2"></rect><line x1="1" y1="10" x2="23" y2="10"></line></svg> •••• ' + (1000 + (id * 17) % 9000),
            '<svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="4" width="22" height="16" rx="2" ry="2"></rect><line x1="1" y1="10" x2="23" y2="10"></line></svg> •••• ' + (2000 + (id * 23) % 8000)
        ];
        return methods[id % methods.length];
    };
    
    const getCustomerEmail = (id) => {
        const domains = ['gmail.com', 'yahoo.com', 'company.com'];
        return `customer_${id}@${domains[id % domains.length]}`;
    };

    const getDate = (id) => {
        const date = new Date(Date.now() - (id * 86400000 * 0.3));
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute:'2-digit' });
    };

    tbody.innerHTML = filteredList.map(p => {
        const amt = parseFloat(p.amount);
        const fee = amt * 0.029 + 0.30;
        
        return `
            <tr style="border-bottom: 1px solid var(--border-color); cursor:pointer;">
                <td style="font-family:monospace; color:var(--text-secondary); padding: 0.75rem 1rem;">pi_3${p.payment_id}QW8aX...</td>
                <td style="font-size:0.85rem; color:var(--text-secondary); padding: 0.75rem 1rem;">${getDate(p.payment_id)}</td>
                <td style="font-weight:500; padding: 0.75rem 1rem;">${getCustomerEmail(p.order_id)}</td>
                <td style="font-family:var(--font-heading); font-weight:600; padding: 0.75rem 1rem;">$${amt.toFixed(2)}</td>
                <td style="font-size:0.85rem; color:var(--text-secondary); padding: 0.75rem 1rem;">-$${fee.toFixed(2)}</td>
                <td style="display:flex; align-items:center; gap:0.5rem; color:var(--text-secondary); padding: 0.75rem 1rem;">
                    ${getMethod(p.payment_id)}
                </td>
                <td style="padding: 0.75rem 1rem;"><span class="policy-status status-allowed" style="font-size:0.7rem; padding:0.25rem 0.6rem; border-radius:9999px; display:inline-flex; align-items:center; gap:0.2rem;"><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg> Succeeded</span></td>
                <td style="text-align:right; padding: 0.75rem 1rem;">
                    <button class="btn-icon" style="width:28px; height:28px; border:none; background:transparent;"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/></svg></button>
                </td>
            </tr>
        `;
    }).join('');
}

function renderAdminAuditTable() {
    const tbody = document.getElementById('admin-audit-body');
    if (!tbody) return;

    if (state.adminAuditList.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:2rem;">Empty (Triggers log is empty)</td></tr>`;
        return;
    }

    tbody.innerHTML = state.adminAuditList.map(log => {
        return `
            <tr>
                <td>#${log.log_id}</td>
                <td>Order #${log.order_id}</td>
                <td><span class="order-status-badge order-status-${log.old_status.toLowerCase()}">${log.old_status}</span></td>
                <td><span class="order-status-badge order-status-${log.new_status.toLowerCase()}">${log.new_status}</span></td>
                <td style="font-family:monospace; font-size:0.8rem;">${log.changed_at}</td>
            </tr>
        `;
    }).join('');
}

// Input Filter triggers
function filterAdminProducts() {
    const search = document.getElementById('search-products');
    if (search) {
        state.adminSearchQueries.products = search.value;
        renderAdminProductsTable();
    }
}

function filterAdminCategories() {
    const search = document.getElementById('search-categories');
    if (search) {
        state.adminSearchQueries.categories = search.value;
        renderAdminCategoriesTable();
    }
}

// Search filter triggers
function filterAdminUsers() {
    const search = document.getElementById('search-users');
    if (search) {
        state.adminSearchQueries.users = search.value;
        renderAdminUsersTable();
    }
}

function filterAdminOrders() {
    const filter = document.getElementById('filter-order-status');
    if (filter) {
        state.adminOrdersStatusFilter = filter.value;
        renderAdminOrdersTable();
    }
}


// ============================================================
//   SUB-VIEW ACTIONS HANDLERS (TRIGGERS INSERT & UPDATE)
// ============================================================

// Submit handler to add product (BEFORE Insert Trigger check)
async function submitProductForm(e) {
    e.preventDefault();
    const nameInput = document.getElementById('admin-prod-name');
    const priceInput = document.getElementById('admin-prod-price');
    const catInput = document.getElementById('admin-prod-category');
    
    if (!nameInput || !priceInput || !catInput) return;
    
    const name = nameInput.value.trim();
    const price = parseFloat(priceInput.value);
    const category_id = catInput.value;
    const imageInput = document.getElementById('admin-prod-images');
    
    logConsole(`INSERT INTO products (name, price, category_id, image_url) ...`, "query");
    
    const formData = new FormData();
    formData.append('name', name);
    formData.append('price', price);
    formData.append('category_id', category_id);
    
    if (imageInput && imageInput.files.length > 0) {
        for (let i = 0; i < imageInput.files.length; i++) {
            formData.append('images', imageInput.files[i]);
        }
    }
    
    try {
        const res = await apiFetch(`${API_BASE}/products/add`, {
            method: 'POST',
            body: formData
        });
        const result = await res.json();
        
        if (result.success) {
            logConsole(`Product inserted successfully. Name automatically converted to uppercase: '${result.product.name}'`, "success");
            showToast(`Item added! UPPERCASE: ${result.product.name}`, "success");
            
            // Reset inputs
            nameInput.value = '';
            priceInput.value = '';
            
            // Close form card
            toggleAddProductForm();
            
            // Refresh catalog and admin view
            await fetchProductsAndCategories();
            await loadSubViewData('products');
        } else {
            logConsole(`Failed to add product: ${result.error}`, "error");
            showToast(result.error || "Ku darista wuu fashilmay", "error");
        }
    } catch (err) {
        logConsole(`Add product error: ${err.message}`, "error");
    }
}

// Add category category POST API call
async function submitCategoryForm(e) {
    e.preventDefault();
    const nameInput = document.getElementById('admin-cat-name');
    if (!nameInput) return;

    const category_name = nameInput.value.trim();
    logConsole(`INSERT INTO categories (category_name) VALUES ('${category_name}');`, "query");

    try {
        const res = await fetch(`${API_BASE}/categories/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ category_name })
        });
        const result = await res.json();

        if (result.success) {
            logConsole(`Category inserted successfully: '${category_name}'`, "success");
            showToast(`Category added!`, "success");
            nameInput.value = '';
            toggleAddCategoryForm();
            
            await fetchProductsAndCategories();
            await loadSubViewData('categories');
        } else {
            showToast(result.error || "Ku darista fashilantay!", "error");
        }
    } catch (err) {
        logConsole(`Add category error: ${err.message}`, "error");
    }
}

// Submit handler to update order status (AFTER Update Trigger check)
async function submitStatusForm(e) {
    e.preventDefault();
    const orderInput = document.getElementById('admin-status-order-id');
    const statusInput = document.getElementById('admin-status-value');
    
    if (!orderInput || !statusInput) return;
    
    const order_id = orderInput.value;
    const status = statusInput.value;
    
    logConsole(`UPDATE orders SET status = '${status}' WHERE order_id = ${order_id};`, "query");
    logConsole("Trigger executing: trg_orders_after_update (AFTER UPDATE OF status ON orders FOR EACH ROW...)", "info");
    
    try {
        const res = await fetch(`${API_BASE}/orders/update-status`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ order_id, status })
        });
        const result = await res.json();
        
        if (result.success) {
            logConsole(result.message, "success");
            logConsole(`Audit Log entry created automatically in ORDER_AUDIT_LOGS table.`, "success");
            showToast(`Status changed (Audit Log written)`, "success");
            
            // Reset input
            orderInput.value = '';
            
            // Refresh
            await fetchOrders();
            await loadSubViewData('orders');
        } else {
            logConsole(`Failed to update status: ${result.error}`, "error");
            showToast(result.error || "Fashil", "error");
        }
    } catch (err) {
        logConsole(`Status update error: ${err.message}`, "error");
    }
}


// ============================================================
//   EVENT LISTENERS CONFIGURATION
// ============================================================

function setupEventListeners() {
    // Login form submit
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const emailInput = document.getElementById('login-email');
            const passwordInput = document.getElementById('login-password');
            if (emailInput && passwordInput) {
                await handleLogin(emailInput.value.trim(), passwordInput.value);
                emailInput.value = '';
                passwordInput.value = '';
            }
        });
    }

    // Register form submit
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }

    // Forgot Request form submit
    const forgotReqForm = document.getElementById('forgot-request-form');
    if (forgotReqForm) {
        forgotReqForm.addEventListener('submit', handleForgotRequest);
    }

    // Forgot Reset form submit
    const forgotResetForm = document.getElementById('forgot-reset-form');
    if (forgotResetForm) {
        forgotResetForm.addEventListener('submit', handleForgotReset);
    }

    // Redirect button to admin dashboard
    const adminBtn = document.getElementById('nav-admin-dashboard-btn');
    if (adminBtn) {
        adminBtn.addEventListener('click', () => {
            switchPage('admin');
            loadSubViewData('dashboard');
        });
    }

    // Return back to store button in sidebar
    const backBtn = document.getElementById('btn-back-to-store');
    if (backBtn) {
        backBtn.addEventListener('click', () => {
            switchPage('store');
            switchView('categories');
        });
    }

    // Bind storefront header tabs
    document.querySelectorAll('.nav-tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            switchView(btn.dataset.view);
        });
    });

    // Theme Toggle
    const themeBtn = document.getElementById('theme-toggle');
    if (themeBtn) {
        themeBtn.addEventListener('click', toggleTheme);
    }

    // Storefront checkout
    const checkoutBtn = document.getElementById('btn-checkout');
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', openPaymentModal);
    }
    const checkoutLargeBtn = document.getElementById('btn-large-checkout');
    if (checkoutLargeBtn) {
        checkoutLargeBtn.addEventListener('click', openPaymentModal);
    }

    // Admin Sidebar view switcher
    document.querySelectorAll('.admin-menu-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.admin-menu-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const subviewName = btn.dataset.subview;
            document.querySelectorAll('.admin-subview').forEach(view => {
                if (view.id === `subview-${subviewName}`) view.classList.add('active');
                else view.classList.remove('active');
            });

            loadSubViewData(subviewName);
        });
    });

    // Reset DB on admin dashboard view
    const adminResetBtn = document.getElementById('admin-db-reset-btn');
    if (adminResetBtn) {
        adminResetBtn.addEventListener('click', resetDB);
    }

    // Admin add product trigger form submit
    const adminProdForm = document.getElementById('admin-add-product-form');
    if (adminProdForm) {
        adminProdForm.addEventListener('submit', submitProductForm);
    }

    // Admin add category form submit
    const adminCatForm = document.getElementById('admin-add-category-form');
    if (adminCatForm) {
        adminCatForm.addEventListener('submit', submitCategoryForm);
    }

    // Admin status update trigger form submit
    const adminStatusForm = document.getElementById('admin-update-status-form');
    if (adminStatusForm) {
        adminStatusForm.addEventListener('submit', submitStatusForm);
    }
}

// Auth Subview Switcher
function showAuthView(view) {
    const loginContainer = document.getElementById('login-form-container');
    const registerContainer = document.getElementById('register-form-container');
    const forgotContainer = document.getElementById('forgot-form-container');
    const forgotReqPhase = document.getElementById('forgot-request-phase');
    const forgotResetPhase = document.getElementById('forgot-reset-phase');

    if (loginContainer) loginContainer.style.display = view === 'login' ? 'block' : 'none';
    if (registerContainer) registerContainer.style.display = view === 'register' ? 'block' : 'none';
    if (forgotContainer) {
        forgotContainer.style.display = view === 'forgot' ? 'block' : 'none';
        if (view === 'forgot') {
            forgotReqPhase.style.display = 'block';
            forgotResetPhase.style.display = 'none';
        }
    }
}

function cancelResetPhase() {
    const forgotReqPhase = document.getElementById('forgot-request-phase');
    const forgotResetPhase = document.getElementById('forgot-reset-phase');
    if (forgotReqPhase && forgotResetPhase) {
        forgotReqPhase.style.display = 'block';
        forgotResetPhase.style.display = 'none';
    }
}

// Registration Submission
async function handleRegister(e) {
    e.preventDefault();
    const name = document.getElementById('register-name').value.trim();
    const email = document.getElementById('register-email').value.trim();
    const password = document.getElementById('register-password').value;
    const confirm = document.getElementById('register-confirm').value;

    if (!name || !email || !password || !confirm) {
        showToast("All information is required!", "error");
        return;
    }

    if (password !== confirm) {
        showToast("Fure-siirada isku mid ma ahan!", "error");
        return;
    }

    logConsole(`INSERT INTO users (name, email, password, role) VALUES ('${name}', '${email}', '${password}', 'customer');`, "query");

    try {
        const res = await fetch(`${API_BASE}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password })
        });
        const result = await res.json();
        if (result.success) {
            showToast("Successful! Please log in now.", "success");
            logConsole("Registration successful: " + email, "success");
            document.getElementById('register-form').reset();
            showAuthView('login');
        } else {
            showToast(result.error || "Registration failed", "error");
            logConsole("Registration failed: " + (result.error || ""), "error");
        }
    } catch (err) {
        logConsole(`Registration failed: ${err.message}`, "error");
        showToast("Server connection error!", "error");
    }
}

// Password Reset Request (Phase A)
let savedResetEmail = '';
async function handleForgotRequest(e) {
    e.preventDefault();
    const email = document.getElementById('forgot-email').value.trim();

    if (!email) {
        showToast("Please enter your email!", "error");
        return;
    }

    logConsole(`UPDATE users SET reset_code = 'XXXXXX' WHERE email = '${email}';`, "query");

    try {
        const res = await fetch(`${API_BASE}/forgot-password/request`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });
        const result = await res.json();
        if (result.success) {
            savedResetEmail = email;
            logConsole(`Reset code requested. Code generated: ${result.code}`, "success");
            alert(`CONFIRMATION: Your verification code is: ${result.code}\n\n(Displayed here for testing purposes)`);
            
            // Toggle to reset phase
            document.getElementById('forgot-request-phase').style.display = 'none';
            document.getElementById('forgot-reset-phase').style.display = 'block';
        } else {
            showToast(result.error || "Email-kaan laguma helin akoon", "error");
        }
    } catch (err) {
        logConsole(`Password reset request error: ${err.message}`, "error");
        showToast("Server connection error!", "error");
    }
}

// Password Reset (Phase B)
async function handleForgotReset(e) {
    e.preventDefault();
    const code = document.getElementById('forgot-code').value.trim();
    const password = document.getElementById('forgot-password-new').value;
    const confirm = document.getElementById('forgot-password-confirm').value;

    if (!code || !password || !confirm) {
        showToast("Please fill all fields!", "error");
        return;
    }

    if (password !== confirm) {
        showToast("Fure-siirada cusub isku mid ma ahan!", "error");
        return;
    }

    logConsole(`UPDATE users SET password = '${password}' WHERE email = '${savedResetEmail}';`, "query");

    try {
        const res = await fetch(`${API_BASE}/forgot-password/reset`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: savedResetEmail, code, password })
        });
        const result = await res.json();
        if (result.success) {
            showToast("Password reset successfully!", "success");
            logConsole("Password reset successful for " + savedResetEmail, "success");
            document.getElementById('forgot-reset-form').reset();
            showAuthView('login');
        } else {
            showToast(result.error || "Cillad ayaa ka dhacday bedelaada fure-sirta", "error");
        }
    } catch (err) {
        logConsole(`Password reset failed: ${err.message}`, "error");
        showToast("Server connection error!", "error");
    }
}

// Store helper handlers
function showReportsToast() {
    showToast("Sales and customer reports can be viewed on the Admin Dashboard.", "info");
}

function showBulkPromoDetails() {
    showToast("Dalbo wax ka badan 50 xabbo si aad u hesho 15% qiimo dhimis ah bulk order.", "success");
}

function toggleStoreFilters() {
    showToast("Ku sifee alaabta qeybta bidix ee CATEGORIES.", "info");
}

function filterStoreProducts() {
    renderProducts();
}

function sortStoreProducts() {
    const sortVal = document.getElementById('sort-products').value;
    if (sortVal === 'price-low') {
        state.products.sort((a, b) => a.price - b.price);
    } else if (sortVal === 'price-high') {
        state.products.sort((a, b) => b.price - a.price);
    } else {
        state.products.sort((a, b) => a.product_id - b.product_id);
    }
    renderProducts();
}

// Global scopes for HTML inline events
window.showAuthView = showAuthView;
window.cancelResetPhase = cancelResetPhase;
window.showReportsToast = showReportsToast;
window.showBulkPromoDetails = showBulkPromoDetails;
window.toggleStoreFilters = toggleStoreFilters;
window.filterStoreProducts = filterStoreProducts;
window.sortStoreProducts = sortStoreProducts;

// Start App on ready
document.addEventListener('DOMContentLoaded', initApp);
