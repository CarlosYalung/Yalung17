import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'your_drip_horizon_secret_key_12345'

DATABASE = 'shoe_store.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL 
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            product_id TEXT NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price_at_purchase REAL NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()


with app.app_context():
    init_db()

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

@app.route('/add_to_cart/<product_id>')
def add_to_cart(product_id):
    product = PRODUCTS.get(product_id)

    if product:
        flash(f'Thank you for selecting {product["name"]}! Your single item order is below.', 'success')

        session['last_added_id'] = product_id

        return redirect(url_for('cart', last_added_id=product_id))

    else:
        flash('Product not found.', 'danger')
        return redirect(url_for('shop'))


@app.route('/cart')
def cart():
    last_added_id = request.args.get('last_added_id')
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


@app.route('/finalize_purchase')
def finalize_purchase():
    product_id = session.pop('last_added_id', None)
    user_id = session.get('user_id')

    if user_id and product_id:
        product = PRODUCTS.get(product_id)

        if product:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()

            # Insert the purchase record into the orders table
            cursor.execute("""
                INSERT INTO orders (user_id, product_id, product_name, quantity, price_at_purchase)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, product_id, product['name'], 1, product['price']))

            conn.commit()
            conn.close()

            flash(f"Thank you for your purchase of {product['name']}! Your order has been placed and tracked.",
                  'success')
        else:
            flash("Error: Product details could not be found to complete the purchase.", 'danger')

    elif not user_id:
        flash("Thank you for your purchase! (Please log in next time to track your orders).", 'success')
    else:
        flash("Order could not be finalized. Please add an item to the cart first.", 'danger')

    return redirect(url_for('shop'))


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
    flash("You have been successfully logged out.", 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)