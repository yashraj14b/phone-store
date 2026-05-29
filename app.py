from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "phone_store_secret"


# ---------------- DATABASE ---------------- #

def get_db_connection():
    conn = sqlite3.connect("store.db")
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- HOME ---------------- #

@app.route('/')
def home():

    search = request.args.get('search', '')

    conn = get_db_connection()

    if search:
        phones = conn.execute(
            "SELECT * FROM phones WHERE name LIKE ?",
            ('%' + search + '%',)
        ).fetchall()
    else:
        phones = conn.execute(
            "SELECT * FROM phones"
        ).fetchall()

    conn.close()

    return render_template(
        'index.html',
        phones=phones
    )


# ---------------- PRODUCT PAGE ---------------- #

@app.route('/product/<int:id>')
def product(id):

    conn = get_db_connection()

    phone = conn.execute(
        "SELECT * FROM phones WHERE id=?",
        (id,)
    ).fetchone()

    conn.close()

    return render_template(
        'product.html',
        phone=phone
    )


# ---------------- REGISTER ---------------- #

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()

        conn.execute(
            """
            INSERT INTO users
            (username,email,password)
            VALUES (?,?,?)
            """,
            (username, email, password)
        )

        conn.commit()
        conn.close()

        flash("Registration Successful")
        return redirect('/login')

    return render_template('register.html')


# ---------------- LOGIN ---------------- #

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()

        user = conn.execute(
            """
            SELECT * FROM users
            WHERE email=? AND password=?
            """,
            (email, password)
        ).fetchone()

        conn.close()

        if user:

            session['user_id'] = user['id']
            session['username'] = user['username']

            return redirect('/')

        flash("Invalid Credentials")

    return render_template('login.html')


# ---------------- LOGOUT ---------------- #

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')


# ---------------- CART ---------------- #

@app.route('/add_to_cart/<int:id>')
def add_to_cart(id):

    if 'cart' not in session:
        session['cart'] = []

    cart = session['cart']
    cart.append(id)

    session['cart'] = cart

    return redirect('/cart')


@app.route('/cart')
def cart():

    cart_items = []

    conn = get_db_connection()

    if 'cart' in session:

        for item_id in session['cart']:

            phone = conn.execute(
                "SELECT * FROM phones WHERE id=?",
                (item_id,)
            ).fetchone()

            if phone:
                cart_items.append(phone)

    conn.close()

    total = sum(item['price'] for item in cart_items)

    return render_template(
        'cart.html',
        cart_items=cart_items,
        total=total
    )


# ---------------- REMOVE FROM CART ---------------- #

@app.route('/remove_from_cart/<int:id>')
def remove_from_cart(id):

    if 'cart' in session:

        cart = session['cart']

        if id in cart:
            cart.remove(id)

        session['cart'] = cart

    return redirect('/cart')


# ---------------- CHECKOUT ---------------- #

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():

    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()

    cart_items = []

    if 'cart' in session:

        for item_id in session['cart']:

            phone = conn.execute(
                "SELECT * FROM phones WHERE id=?",
                (item_id,)
            ).fetchone()

            if phone:
                cart_items.append(phone)

    total = sum(item['price'] for item in cart_items)

    if request.method == 'POST':

        conn.execute(
            """
            INSERT INTO orders
            (user_id,total)
            VALUES (?,?)
            """,
            (session['user_id'], total)
        )

        conn.commit()

        session['cart'] = []

        flash("Order Placed Successfully")

        return redirect('/orders')

    conn.close()

    return render_template(
        'checkout.html',
        cart_items=cart_items,
        total=total
    )


# ---------------- ORDERS ---------------- #

@app.route('/orders')
def orders():

    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()

    orders = conn.execute(
        """
        SELECT * FROM orders
        WHERE user_id=?
        ORDER BY id DESC
        """,
        (session['user_id'],)
    ).fetchall()

    conn.close()

    return render_template(
        'orders.html',
        orders=orders
    )


# ---------------- ADMIN PANEL ---------------- #

@app.route('/admin')
def admin():

    conn = get_db_connection()

    phones = conn.execute(
        "SELECT * FROM phones"
    ).fetchall()

    conn.close()

    return render_template(
        'admin.html',
        phones=phones
    )


# ---------------- ADD PRODUCT ---------------- #

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():

    if request.method == 'POST':

        name = request.form['name']
        price = request.form['price']
        image = request.form['image']
        description = request.form['description']

        conn = get_db_connection()

        conn.execute(
            """
            INSERT INTO phones
            (name,price,image,description)
            VALUES (?,?,?,?)
            """,
            (name, price, image, description)
        )

        conn.commit()
        conn.close()

        return redirect('/admin')

    return render_template('add_product.html')


# ---------------- EDIT PRODUCT ---------------- #

@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):

    conn = get_db_connection()

    if request.method == 'POST':

        name = request.form['name']
        price = request.form['price']
        image = request.form['image']
        description = request.form['description']

        conn.execute(
            """
            UPDATE phones
            SET name=?,
                price=?,
                image=?,
                description=?
            WHERE id=?
            """,
            (name, price, image, description, id)
        )

        conn.commit()

        return redirect('/admin')

    phone = conn.execute(
        "SELECT * FROM phones WHERE id=?",
        (id,)
    ).fetchone()

    conn.close()

    return render_template(
        'edit_product.html',
        phone=phone
    )


# ---------------- DELETE PRODUCT ---------------- #

@app.route('/delete_product/<int:id>')
def delete_product(id):

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM phones WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/admin')


# ---------------- RUN ---------------- #

if __name__ == '__main__':
    app.run(debug=True)