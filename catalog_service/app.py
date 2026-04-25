import os
import time
import random
from datetime import datetime
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Cloud-native practice: Retrieve DB credentials from environment variables
database_uri = os.environ.get('DATABASE_URI', 'sqlite:///catalog.db')
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 1. Categories
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(255))
    products = db.relationship('Product', backref='category', lazy=True)

# 2. Products
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)

    def to_dict(self):
        return {
            "id": self.id, 
            "name": self.name, 
            "price": self.price, 
            "image_url": self.image_url,
            "category": self.category.name if self.category else "Uncategorized"
        }

# 3. Customers
class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship('Order', backref='customer', lazy=True)

# 4. Orders
class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='PENDING') # PENDING, SHIPPED, DELIVERED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', lazy=True)

# 5. Order Items (Many-to-Many bridge for Order and Product)
class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price_at_purchase = db.Column(db.Float, nullable=False)
    product = db.relationship('Product')

# Initialize DB on load with retry logic
with app.app_context():
    retries = 10
    while retries > 0:
        try:
            db.create_all()
            if not Category.query.first():
                # Seed Data logic
                cat_tech = Category(name="Technology", description="Tech gadgets and computers")
                cat_apparel = Category(name="Apparel", description="Clothing and accessories")
                db.session.add_all([cat_tech, cat_apparel])
                db.session.commit()

                p1 = Product(name="Cloud Architect Handbook", price=45.00, category_id=cat_tech.id, image_url="https://images.unsplash.com/photo-1544161515-4ab6ce6db874?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80")
                p2 = Product(name="Kubernetes Node Server", price=1200.00, category_id=cat_tech.id, image_url="https://images.unsplash.com/photo-1558494949-ef010cbdcc31?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80")
                p3 = Product(name="Container Ship Model", price=85.00, category_id=cat_apparel.id, image_url="https://images.unsplash.com/photo-1577708579080-60b54020c9f1?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80")
                p4 = Product(name="Mechanical Keyboard", price=150.00, category_id=cat_tech.id, image_url="https://images.unsplash.com/photo-1595225476474-87563907a212?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80")
                db.session.add_all([p1, p2, p3, p4])
                
                cust1 = Customer(first_name="Jane", last_name="Doe", email="jane@cloudnative.dev")
                db.session.add(cust1)
                db.session.commit()

                order1 = Order(customer_id=cust1.id, total_amount=1245.00, status="SHIPPED")
                db.session.add(order1)
                db.session.commit()

                oi1 = OrderItem(order_id=order1.id, product_id=p1.id, quantity=1, price_at_purchase=45.00)
                oi2 = OrderItem(order_id=order1.id, product_id=p2.id, quantity=1, price_at_purchase=1200.00)
                db.session.add_all([oi1, oi2])
                db.session.commit()

            print("Database connected and all schemas populated.")
            break
        except Exception as e:
            print(f"DB not ready, retrying... ({retries} left)")
            time.sleep(3)
            retries -= 1

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/catalog/products', methods=['GET'])
def get_products():
    # Lab 1: Artificial Tail Latency Simulation
    # Most requests are fast, but random.expovariate creates occasional long delays.
    # Lambda of 1.5 gives an average delay of 0.66 seconds, but rare requests take much longer.
    delay = random.expovariate(1.5)
    time.sleep(delay)

    products = Product.query.all()
    return jsonify({"products": [p.to_dict() for p in products]}), 200

@app.route('/api/catalog/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    # Lab 1: Tail Latency simulation for individual lookup too
    delay = random.expovariate(1.5)
    time.sleep(delay)

    product = Product.query.get(product_id)
    if product:
        return jsonify(product.to_dict()), 200
    return jsonify({"error": "Product not found"}), 404

# New Route: Get all customers
@app.route('/api/catalog/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    cust_list = [{"id": c.id, "name": f"{c.first_name} {c.last_name}", "email": c.email} for c in customers]
    return jsonify({"customers": cust_list}), 200

# New Route: Get full order details
@app.route('/api/catalog/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    res = []
    for o in orders:
        items = [{"product": i.product.name, "qty": i.quantity, "price": i.price_at_purchase} for i in o.items]
        res.append({
            "order_id": o.id,
            "customer": f"{o.customer.first_name} {o.customer.last_name}",
            "total": o.total_amount,
            "status": o.status,
            "items": items
        })
    return jsonify({"orders": res}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
