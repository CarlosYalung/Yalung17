import sqlite3
import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'your_drip_horizon_secret_key_12345'

DATABASE = 'shoe_store.db'
# Configuration for Photo Uploads
UPLOAD_FOLDER = 'static/profiles'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Helper function for checking allowed file extensions
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ----------------- Database Initialization (Tracking Number REMOVED) -----------------
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # 1. Users Table (No Change)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL 
        )
    ''')
    try:
        cursor.execute("SELECT profile_pic FROM users LIMIT 1")
    except sqlite3.OperationalError:
        print("Adding 'profile_pic' column to users table...")
        cursor.execute("ALTER TABLE users ADD COLUMN profile_pic TEXT DEFAULT 'default_profile.png'")

    # 2. Orders/Purchases Table (Tracking Number REMOVED from CREATE statement)
    # NOTE: SQLite makes removing columns complicated. For simplicity and to prevent
    # errors in new/existing installations, we ensure the new schema is used,
    # and existing columns (like status and reason) are checked/added.
    # The 'tracking_number' column will remain in old databases but won't be used/fetched.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            product_id TEXT NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price_at_purchase REAL NOT NULL,
            shipping_name TEXT,              
            shipping_address TEXT,           
            shipping_phone TEXT,
            status TEXT DEFAULT 'Processing',           
            cancellation_reason TEXT DEFAULT NULL,  
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # Ensure necessary columns exist for existing databases
    try:
        cursor.execute("SELECT status FROM orders LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE orders ADD COLUMN status TEXT DEFAULT 'Processing'")

    try:
        cursor.execute("SELECT cancellation_reason FROM orders LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE orders ADD COLUMN cancellation_reason TEXT DEFAULT NULL")

    conn.commit()
    conn.close()


with app.app_context():
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    init_db()

# ----------------- Product Data (Unchanged) -----------------
PRODUCTS = {
    '21': {'name': 'Womens Sneaker 1', 'price': 79.99, 'img': '21.jpg'},
    '22': {'name': 'Womens Sandal 1', 'price': 59.99, 'img': '22.jpg'},
    '23': {'name': 'Womens Heel 1', 'price': 109.99, 'img': '23.jpg'},
    '24': {'name': 'Womens Loafer 1', 'price': 89.99, 'img': '24.jpg'},
    '25': {'name': 'Womens Trainer 1', 'price': 94.99, 'img': '25.jpg'},
    '26': {'name': 'Mens Loafer 1', 'price': 89.99, 'img': '26.jpg'},
    '27': {'name': 'Mens Boot 1', 'price': 129.99, 'img': '27.jpg'},
    '28': {'name': 'Mens Sneaker 1', 'price': 79.99, 'img': '28.jpg'},
    '29': {'name': 'Mens Casual 1', 'price': 69.99, 'img': '29.jpg'},
    '30': {'name': 'Kids Trainer 1', 'price': 49.99, 'img': '30.jpg'},
    '31': {'name': 'Kids Sneaker 1', 'price': 54.99, 'img': '31.jpg'},
    '32': {'name': 'Kids Sandal 1', 'price': 39.99, 'img': '32.jpg'},
    '33': {'name': 'Kids Boot 1', 'price': 64.99, 'img': '33.jpg'},
    '34': {'name': 'Kids Loafer 1', 'price': 44.99, 'img': '34.jpg'},
    '35': {'name': 'Sport Shoe 1', 'price': 99.99, 'img': '35.jpg'},
    '36': {'name': 'Sport Shoe 2', 'price': 119.99, 'img': '36.jpg'},
    '37': {'name': 'Sport Shoe 3', 'price': 89.99, 'img': '37.jpg'},
    '38': {'name': 'Sport Accessory 1', 'price': 29.99, 'img': '38.jpg'},
}


# ----------------- Page Routes (Unchanged) -----------------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/shop')
def shop():
    return render_template('shop.html', current_category='all')


@app.route('/women')
def women():
    return render_template('women.html', current_category='women')


@app.route('/men')
def men():
    return render_template('men.html', current_category='men')


@app.route('/kid')
def kid():
    return render_template('kid.html', current_category='kid')


@app.route('/sport')
def sport():
    return render_template('sport.html', current_category='sport')


# ----------------- Profile Route (Tracking Number REMOVED) -----------------

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash("Please log in to view your profile.", 'danger')
        return redirect(url_for('index'))

    user_id = session['user_id']
    username = session['username']

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # 1. Get User Profile Information
    cursor.execute("SELECT username, profile_pic FROM users WHERE id = ?", (user_id,))
    user_data = cursor.fetchone()
    profile_pic = user_data[1] if user_data and user_data[1] else 'default_profile.png'

    # 2. Get Order History (Tracking Number REMOVED from SELECT)
    cursor.execute("""
        SELECT 
            product_name,           -- Index 0
            quantity,               -- Index 1
            price_at_purchase,      -- Index 2
            id AS order_id,         -- Index 3
            shipping_address,       -- Index 4
            shipping_phone,         -- Index 5
            status,                 -- Index 6
            cancellation_reason     -- Index 7
        FROM orders
        WHERE user_id = ?
        ORDER BY order_id DESC
    """, (user_id,))
    orders = cursor.fetchall()

    conn.close()

    return render_template('profile.html',
                           username=username,
                           orders=orders,
                           profile_pic=profile_pic)


# ----------------- Photo Upload Route (Unchanged) -----------------

@app.route('/upload_photo', methods=['POST'])
def upload_photo():
    if 'user_id' not in session:
        flash("You must be logged in to upload a photo.", 'danger')
        return redirect(url_for('index'))

    user_id = session['user_id']

    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('profile'))

    file = request.files['file']

    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('profile'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{user_id}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute("UPDATE users SET profile_pic = ? WHERE id = ?", (unique_filename, user_id))

        conn.commit()
        conn.close()

        flash('Profile picture updated successfully!', 'success')
        return redirect(url_for('profile'))
    else:
        flash('File type not allowed. Use PNG, JPG, JPEG, or GIF.', 'danger')
        return redirect(url_for('profile'))


# ----------------- Cart & Purchase Logic (Unchanged) -----------------

@app.route('/add_to_cart/<product_id>')
def add_to_cart(product_id):
    product = PRODUCTS.get(product_id)

    if product:
        session.pop('shipping_data', None)
        session['last_added_id'] = product_id

        flash(f'Thank you for selecting {product["name"]}! Review your order and enter shipping details below.',
              'success')
        return redirect(url_for('cart', last_added_id=product_id))

    else:
        flash('Product not found.', 'danger')
        return redirect(url_for('shop'))


@app.route('/cart')
def cart():
    last_added_id = request.args.get('last_added_id') or session.get('last_added_id')
    single_item = None

    if last_added_id:
        product = PRODUCTS.get(last_added_id)

        if product:
            single_item = {
                'id': last_added_id,
                'name': product['name'],
                'price': product['price'],
                'quantity': 1,
                'subtotal': product['price'],
                'img': product['img']
            }

    return render_template('cart.html', single_item=single_item)


@app.route('/submit_shipping_info', methods=['POST'])
def submit_shipping_info():
    product_id = request.form.get('product_id_to_buy')
    shipping_name = request.form.get('shipping_name')
    shipping_address = request.form.get('shipping_address')
    shipping_phone = request.form.get('shipping_phone')
    user_id = session.get('user_id')

    if not product_id or not shipping_name or not shipping_address or not shipping_phone:
        flash("Please fill in all shipping details.", 'danger')
        return redirect(url_for('cart', last_added_id=product_id))

    product = PRODUCTS.get(product_id)

    if not product:
        flash("Error: Product details could not be found.", 'danger')
        return redirect(url_for('shop'))

    session['shipping_data'] = {
        'name': shipping_name,
        'address': shipping_address,
        'phone': shipping_phone,
        'product_id': product_id
    }

    session.pop('last_added_id', None)

    if user_id:
        return redirect(url_for('finalize_purchase'))
    else:
        flash("Please log in or sign up now to track your order.", 'info')
        return redirect(url_for('index') + '#loginModal')


@app.route('/finalize_purchase')
def finalize_purchase():
    shipping_data = session.pop('shipping_data', None)
    user_id = session.get('user_id')

    if not shipping_data:
        flash("Order process interrupted. Please re-add the item and provide shipping details.", 'danger')
        return redirect(url_for('shop'))

    product_id = shipping_data['product_id']
    product = PRODUCTS.get(product_id)

    if not product:
        flash("Error: Product details could not be found to complete the purchase.", 'danger')
        return redirect(url_for('shop'))

    if user_id:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Inserts into orders table
        cursor.execute("""
            INSERT INTO orders (user_id, product_id, product_name, quantity, price_at_purchase, shipping_name, shipping_address, shipping_phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            product_id,
            product['name'],
            1,
            product['price'],
            shipping_data['name'],
            shipping_data['address'],
            shipping_data['phone']
        ))

        conn.commit()
        conn.close()

        flash(f"Thank you! Your order of {product['name']} is placed and tracked.", 'success')
        return redirect(url_for('shop'))

    else:
        flash(
            f"Thank you for your purchase of {product['name']}! Your order is confirmed and will be delivered to {shipping_data['address']}.",
            'success')
        return redirect(url_for('shop'))


# ----------------- USER ORDER CANCELLATION ROUTE (Unchanged) -----------------

@app.route('/cancel_order/<int:order_id>', methods=['POST'])
def cancel_order(order_id):
    if 'user_id' not in session:
        flash("Please log in to manage your orders.", 'danger')
        return redirect(url_for('index'))

    user_id = session['user_id']
    reason = request.form.get('reason')

    if not reason:
        flash("Cancellation reason is required.", 'danger')
        return redirect(url_for('profile'))

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        # 1. Verify the order belongs to the user and is in a cancellable state ('Processing')
        cursor.execute("SELECT status FROM orders WHERE id = ? AND user_id = ?", (order_id, user_id))
        order_status = cursor.fetchone()

        if order_status is None:
            flash(f"Order #{order_id} not found or does not belong to you.", 'danger')
        elif order_status[0] != 'Processing':
            flash(f"Order #{order_id} is already '{order_status[0]}' and cannot be cancelled.", 'danger')
        else:
            # 2. Update status AND save the cancellation reason persistently
            cursor.execute("UPDATE orders SET status = ?, cancellation_reason = ? WHERE id = ?",
                           ('Cancelled', reason, order_id))
            conn.commit()

            print(f"User {session['username']} cancelled Order #{order_id}. Reason SAVED: {reason}")

            flash(f"Order #{order_id} has been successfully cancelled. Reason: {reason}", 'success')

    except Exception as e:
        flash(f"An error occurred during cancellation: {e}", 'danger')
    finally:
        conn.close()

    return redirect(url_for('profile'))


# ----------------- Authentication Routes (Unchanged) -----------------

@app.route('/signup', methods=['GET', 'POST'])
def sign():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('shop') + '#loginModal')
        except sqlite3.IntegrityError:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('shop') + '#signInModal')
        finally:
            conn.close()

    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute("SELECT id, username FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]

            flash(f'Welcome back, {username}! You are now logged in.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('shop') + '#loginModal')

    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('shipping_data', None)
    session.pop('last_added_id', None)
    flash("You have been successfully logged out.", 'info')
    return redirect(url_for('index'))


# ----------------- Run the application -----------------
if __name__ == '__main__':
    app.run(debug=True)