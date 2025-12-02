from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-me'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nava_organics.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)  # demo only, not hashed
    is_admin = db.Column(db.Boolean, default=False)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # soap, shampoo, serum, haircare
    description = db.Column(db.Text, default='Placeholder description for this herbal product.')
    image_url = db.Column(db.String(255), default='/static/img/placeholder.png')
    base_price = db.Column(db.Integer, nullable=False)
    secondary_price = db.Column(db.Integer)  # for serums 30 ml
    base_volume = db.Column(db.String(50))   # e.g. '15 ml', '100 ml', 'Bar'
    secondary_volume = db.Column(db.String(50))


class Offer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    discount_percent = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    customer_name = db.Column(db.String(120), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(50), nullable=False)
    customer_address = db.Column(db.Text, nullable=False)
    total_amount = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='Order Placed')
    payment_status = db.Column(db.String(50), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # simulated payment fields (demo only)
    account_number = db.Column(db.String(20))
    card_type = db.Column(db.String(20))

    items = db.relationship('OrderItem', backref='order', lazy=True)


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product_name = db.Column(db.String(120), nullable=False)
    variant_label = db.Column(db.String(50))
    unit_price = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    line_total = db.Column(db.Integer, nullable=False)


class Favourite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))


# Utility functions

def get_cart():
    return session.get('cart', [])


def save_cart(cart):
    session['cart'] = cart


def calculate_cart_total(cart):
    return sum(item['line_total'] for item in cart)


# Auth helpers
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = session.get('user')
        if not user:
            flash('Please login to continue.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated


# Seed initial data
@app.cli.command('init-db')
def init_db_command():
    """Initialize the database and seed default data."""
    db.drop_all()
    db.create_all()

    # Create default admin
    if not User.query.filter_by(email='admin@navaorganics.test').first():
        admin = User(name='Admin', email='admin@navaorganics.test', password='admin123', is_admin=True)
        db.session.add(admin)

    # Products
    products = [
        # Soaps – ₹200 each
        dict(name='Goat Milk Soap', category='soap', base_price=200, base_volume='Bar'),
        dict(name='Manjistha Soap', category='soap', base_price=200, base_volume='Bar'),
        dict(name='Kuppameni Soap', category='soap', base_price=200, base_volume='Bar'),
        dict(name='Carrot Soap', category='soap', base_price=200, base_volume='Bar'),
        dict(name='Coconut Milk Soap', category='soap', base_price=200, base_volume='Bar'),
        dict(name='Papaya Soap', category='soap', base_price=200, base_volume='Bar'),
        dict(name='Charcoal Soap', category='soap', base_price=200, base_volume='Bar'),
        dict(name='Sandal Soap', category='soap', base_price=200, base_volume='Bar'),
        dict(name='Red Sandal Soap', category='soap', base_price=200, base_volume='Bar'),
        dict(name='Gram Flour Soap', category='soap', base_price=200, base_volume='Bar'),
        # Shampoos – ₹300, 100 ml
        dict(name='Onion Shampoo', category='shampoo', base_price=300, base_volume='100 ml'),
        dict(name='Hibiscus Shampoo', category='shampoo', base_price=300, base_volume='100 ml'),
        dict(name='Keratin Shampoo', category='shampoo', base_price=300, base_volume='100 ml'),
        dict(name='Fenugreek Shampoo', category='shampoo', base_price=300, base_volume='100 ml'),
        dict(name='Herbal Shampoo', category='shampoo', base_price=300, base_volume='100 ml'),
        dict(name='Dandruff Shampoo', category='shampoo', base_price=300, base_volume='100 ml'),
        # Face Serums
        dict(name='Kumkumadi Serum', category='serum', base_price=500, secondary_price=1000, base_volume='15 ml', secondary_volume='30 ml'),
        dict(name='Water-Based Serum', category='serum', base_price=500, secondary_price=1000, base_volume='15 ml', secondary_volume='30 ml'),
        # Hair Care
        dict(name='Rosemary Hydrosol Spray', category='haircare', base_price=200, base_volume='100 ml'),
    ]

    for p in products:
        prod = Product(**p)
        db.session.add(prod)

    # Sample offer
    offer = Offer(
        title='Festive Herbal Glow Offer',
        description='Enjoy special savings on selected Nava Organics essentials. Placeholder text – edit in admin.',
        discount_percent=10,
        is_active=True,
    )
    db.session.add(offer)

    db.session.commit()
    print('Initialized the database and seeded data.')


# Context processor
@app.context_processor
def inject_globals():
    return dict(current_user=session.get('user'), cart_count=len(get_cart()))


# Routes – User side
@app.route('/')
def home():
    offers = Offer.query.filter_by(is_active=True).all()
    categories = {
        'soap': Product.query.filter_by(category='soap').limit(4).all(),
        'shampoo': Product.query.filter_by(category='shampoo').limit(4).all(),
        'serum': Product.query.filter_by(category='serum').limit(4).all(),
        'haircare': Product.query.filter_by(category='haircare').limit(4).all(),
    }
    return render_template('index.html', offers=offers, categories=categories)


@app.route('/products')
def products():
    category = request.args.get('category', 'all')
    search = request.args.get('q', '').strip()

    query = Product.query
    if category != 'all':
        query = query.filter_by(category=category)
    if search:
        like = f"%{search}%"
        query = query.filter(Product.name.ilike(like))

    all_products = query.all()
    return render_template('products.html', products=all_products, active_category=category, search=search)


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)


@app.route('/cart')
@login_required
def cart():
    cart_items = get_cart()
    total = calculate_cart_total(cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)


@app.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    user = session.get('user')
    if user and user.get('is_admin'):
        flash('Admins cannot add to cart.')
        return redirect(url_for('products'))
    product_id = int(request.form['product_id'])
    quantity = int(request.form.get('quantity', 1))
    variant = request.form.get('variant', '')  # for serums 15 ml / 30 ml

    product = Product.query.get_or_404(product_id)

    if product.category == 'serum' and variant == '30ml':
        unit_price = product.secondary_price or product.base_price
        variant_label = product.secondary_volume or '30 ml'
    else:
        unit_price = product.base_price
        variant_label = product.base_volume

    line_total = unit_price * quantity

    cart_items = get_cart()
    cart_items.append({
        'product_id': product.id,
        'product_name': product.name,
        'variant_label': variant_label,
        'unit_price': unit_price,
        'quantity': quantity,
        'line_total': line_total,
    })
    save_cart(cart_items)
    flash('Added to cart.')

    return redirect(request.referrer or url_for('products'))


@app.route('/cart/remove/<int:index>')
@login_required
def remove_from_cart(index):
    cart_items = get_cart()
    if 0 <= index < len(cart_items):
        cart_items.pop(index)
        save_cart(cart_items)
    return redirect(url_for('cart'))


@app.route('/cart/update/<int:index>', methods=['POST'])
@login_required
def update_cart_item(index):
    cart_items = get_cart()
    if 0 <= index < len(cart_items):
        item = cart_items[index]
        data = request.get_json(silent=True) or {}
        action = (data.get('action') or request.form.get('action') or '').strip()
        qty = int(data.get('quantity') or item['quantity'])
        if action == 'inc':
            qty += 1
        elif action == 'dec':
            qty = max(1, qty - 1)
        item['quantity'] = qty
        item['line_total'] = item['unit_price'] * qty
        save_cart(cart_items)
        total = calculate_cart_total(cart_items)
        if data:
            return {'ok': True, 'item': item, 'total': total}
    return redirect(url_for('cart'))


@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    user = session.get('user')
    if user and user.get('is_admin'):
        flash('Admins cannot checkout.')
        return redirect(url_for('products'))
    cart_items = get_cart()
    if not cart_items:
        flash('Your cart is empty.')
        return redirect(url_for('products'))

    total = calculate_cart_total(cart_items)

    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        # collect extended address fields, fallback to plain address
        base_address = request.form.get('address', '').strip()
        location = request.form.get('location', '').strip()
        landmark = request.form.get('landmark', '').strip()
        district = request.form.get('district', '').strip()
        state = request.form.get('state', '').strip()
        pincode = request.form.get('pincode', '').strip()
        parts = [base_address]
        if location:
            parts.append(location)
        if landmark:
            parts.append(f"Landmark: {landmark}")
        if district:
            parts.append(district)
        if state:
            parts.append(state)
        if pincode:
            parts.append(f"PIN {pincode}")
        address = ", ".join([p for p in parts if p])

        user = session.get('user')
        user_id = user['id'] if user else None

        order = Order(
            user_id=user_id,
            customer_name=name,
            customer_email=email,
            customer_phone=phone,
            customer_address=address,
            total_amount=total,
            status='Order Placed',
            payment_status='Pending',
        )
        db.session.add(order)
        db.session.flush()

        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item['product_id'],
                product_name=item['product_name'],
                variant_label=item['variant_label'],
                unit_price=item['unit_price'],
                quantity=item['quantity'],
                line_total=item['line_total'],
            )
            db.session.add(order_item)

        db.session.commit()

        # clear cart
        save_cart([])

        return redirect(url_for('payment', order_id=order.id))

    return render_template('checkout.html', cart_items=cart_items, total=total)


@app.route('/payment/<int:order_id>', methods=['GET', 'POST'])
@login_required
def payment(order_id):
    order = Order.query.get_or_404(order_id)

    if request.method == 'POST':
        account_number = request.form.get('account_number', '').strip()
        card_type = request.form.get('card_type', '').strip()
        pin = request.form.get('pin', '').strip()

        # basic server-side validation
        if not (account_number.isdigit() and len(account_number) == 12):
            flash('Account number must be exactly 12 digits.')
            return redirect(url_for('payment', order_id=order.id))
        if not (pin.isdigit() and len(pin) == 4):
            flash('PIN must be exactly 4 digits.')
            return redirect(url_for('payment', order_id=order.id))

        # store only non-sensitive fields; do NOT store PIN in real apps
        order.account_number = account_number
        order.card_type = card_type or 'Card'
        # mark payment as successful immediately for both user and admin views
        order.payment_status = 'Payment Successful'
        db.session.commit()

        return redirect(url_for('receipt', order_id=order.id))

    success = request.args.get('success') == '1'
    return render_template('payment.html', order=order, success=success)


@app.route('/receipt/<int:order_id>')
@login_required
def receipt(order_id):
    order = Order.query.get_or_404(order_id)
    steps = ['Order Placed', 'Order Confirmed', 'Order Dispatched', 'Order Reached']
    try:
        current_index = steps.index(order.status)
    except ValueError:
        current_index = 0
    return render_template('receipt.html', order=order, steps=steps, current_index=current_index)


@app.route('/order/<int:order_id>')
def order_status(order_id):
    order = Order.query.get_or_404(order_id)
    steps = ['Order Placed', 'Order Confirmed', 'Order Dispatched', 'Order Reached']

    # determine current index based on status
    try:
        current_index = steps.index(order.status)
    except ValueError:
        current_index = 0

    delivered_message = 'Order Delivered' if order.status == 'Order Reached' else ''

    return render_template(
        'order_status.html', order=order, steps=steps, current_index=current_index, delivered_message=delivered_message
    )


@app.route('/order/<int:order_id>/reached', methods=['POST'])
@login_required
def user_order_reached(order_id):
    user = session.get('user')
    if not user or user.get('is_admin'):
        return redirect(url_for('order_status', order_id=order_id))
    order = Order.query.get_or_404(order_id)
    if order.user_id != user['id']:
        return redirect(url_for('order_status', order_id=order_id))
    if order.status == 'Order Dispatched':
        order.status = 'Order Reached'
        db.session.commit()
    return redirect(url_for('order_status', order_id=order_id))


# Favourites (requires login)
@app.route('/favourites')
def favourites():
    user = session.get('user')
    if not user:
        flash('Please login to view favourites.')
        return redirect(url_for('login'))

    favs = Favourite.query.filter_by(user_id=user['id']).all()
    products = [Product.query.get(f.product_id) for f in favs]
    return render_template('favourites.html', products=products)


@app.route('/favourites/toggle/<int:product_id>')
def toggle_favourite(product_id):
    user = session.get('user')
    if not user:
        flash('Please login to manage favourites.')
        return redirect(url_for('login'))

    fav = Favourite.query.filter_by(user_id=user['id'], product_id=product_id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
    else:
        new_fav = Favourite(user_id=user['id'], product_id=product_id)
        db.session.add(new_fav)
        db.session.commit()

    return redirect(request.referrer or url_for('products'))


# Auth
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            flash('Email already registered.')
            return redirect(url_for('register'))

        user = User(name=name, email=email, password=password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful. Please login.')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password).first()
        if not user:
            flash('Invalid credentials.')
            return redirect(url_for('login'))

        session['user'] = {'id': user.id, 'name': user.name, 'email': user.email, 'is_admin': user.is_admin}
        flash('Logged in successfully.')
        return redirect(url_for('home'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out.')
    return redirect(url_for('home'))


# Admin routes


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = session.get('user')
        if not user or not user.get('is_admin'):
            flash('Admin access required.')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)

    return decorated


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password, is_admin=True).first()
        if not user:
            flash('Invalid admin credentials.')
            return redirect(url_for('admin_login'))
        session['user'] = {'id': user.id, 'name': user.name, 'email': user.email, 'is_admin': user.is_admin}
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_login.html')


@app.route('/admin')
@admin_required
def admin_dashboard():
    product_count = Product.query.count()
    order_count = Order.query.count()
    offer_count = Offer.query.count()
    return render_template('admin_dashboard.html', product_count=product_count, order_count=order_count, offer_count=offer_count)


@app.route('/admin/products')
@admin_required
def admin_products():
    products = Product.query.all()
    return render_template('admin_products.html', products=products)


@app.route('/admin/products/new', methods=['GET', 'POST'])
@admin_required
def admin_product_new():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        base_price = int(request.form['base_price'])
        description = request.form.get('description') or 'Placeholder description.'
        base_volume = request.form.get('base_volume')
        secondary_price = request.form.get('secondary_price') or None
        secondary_volume = request.form.get('secondary_volume') or None

        product = Product(
            name=name,
            category=category,
            base_price=base_price,
            description=description,
            base_volume=base_volume,
            secondary_price=int(secondary_price) if secondary_price else None,
            secondary_volume=secondary_volume,
        )
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('admin_products'))

    return render_template('admin_product_form.html', product=None)


@app.route('/admin/products/<int:product_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_product_edit(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.category = request.form['category']
        product.base_price = int(request.form['base_price'])
        product.description = request.form.get('description') or product.description
        product.base_volume = request.form.get('base_volume')
        secondary_price = request.form.get('secondary_price') or None
        product.secondary_price = int(secondary_price) if secondary_price else None
        product.secondary_volume = request.form.get('secondary_volume') or None
        db.session.commit()
        return redirect(url_for('admin_products'))
    return render_template('admin_product_form.html', product=product)


@app.route('/admin/products/<int:product_id>/delete', methods=['POST'])
@admin_required
def admin_product_delete(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('admin_products'))


@app.route('/admin/offers', methods=['GET', 'POST'])
@admin_required
def admin_offers():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        discount_percent = request.form.get('discount_percent') or None
        offer = Offer(
            title=title,
            description=description,
            discount_percent=int(discount_percent) if discount_percent else None,
            is_active='is_active' in request.form,
        )
        db.session.add(offer)
        db.session.commit()
        return redirect(url_for('admin_offers'))

    offers = Offer.query.order_by(Offer.id.desc()).all()
    return render_template('admin_offers.html', offers=offers)


@app.route('/admin/offers/<int:offer_id>/toggle', methods=['POST'])
@admin_required
def admin_offer_toggle(offer_id):
    offer = Offer.query.get_or_404(offer_id)
    offer.is_active = not offer.is_active
    db.session.commit()
    return redirect(url_for('admin_offers'))


@app.route('/admin/orders')
@admin_required
def admin_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin_orders.html', orders=orders)


@app.route('/admin/orders/<int:order_id>/status', methods=['POST'])
@admin_required
def admin_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    action = request.form['action']

    if action == 'got':
        order.status = 'Order Placed'
    elif action == 'payment_received':
        if order.status == 'Order Placed':
            order.status = 'Order Confirmed'
    elif action == 'dispatched':
        if order.status == 'Order Confirmed':
            order.status = 'Order Dispatched'
    elif action == 'reached':
        if order.status == 'Order Dispatched':
            order.status = 'Order Reached'

    db.session.commit()
    return redirect(url_for('admin_orders'))


@app.route('/my-orders')
@login_required
def my_orders():
    user = session.get('user')
    orders = Order.query.filter_by(user_id=user['id']).order_by(Order.created_at.desc()).all()
    return render_template('my_orders.html', orders=orders)


if __name__ == '__main__':
    # for local development
    app.run(debug=True)
