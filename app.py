
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import sys  # Import the sys module

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Important: Set a secret key for sessions
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Added name field
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.TEXT, nullable=False)  # Use TEXT for password
    role = db.Column(db.String(20), nullable=False)

    def __init__(self, name, email, password, role):  # Added name to constructor
        self.name = name
        self.email = email
        self.password = (password)
        self.role = role


class Product(db.Model):
    __tablename__ = 'Product'
    ProductID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    InventoryID = db.Column(db.Integer, db.ForeignKey('Inventory.InventoryID'), nullable=True)  # Corrected
    CategoryID = db.Column(db.Integer, db.ForeignKey('Category.CategoryID'), nullable=False)    # Corrected
    SupplierID = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)    # Corrected
    MRP = db.Column(db.Numeric(10, 2), nullable=False)
    StockQuantity = db.Column(db.Integer, nullable=False, default=0)

    supplier = db.relationship('User', backref='products')
    category = db.relationship('Category', backref='products')
    inventory = db.relationship('Inventory', backref='products')

    def __init__(self, Name, CategoryID, SupplierID, MRP, StockQuantity, InventoryID=None):
        self.Name = Name
        self.CategoryID = CategoryID
        self.SupplierID = SupplierID
        self.MRP = MRP
        self.StockQuantity = StockQuantity
        self.InventoryID = InventoryID



class Category(db.Model):
    __tablename__ = 'Category'
    CategoryID = db.Column(db.Integer, primary_key=True)
    CategoryName = db.Column(db.String(50), nullable=False)

    def __init__(self, CategoryName):
        self.CategoryName = CategoryName


class Warehouse(db.Model):
    __tablename__ = 'Warehouse'
    WarehouseID = db.Column(db.Integer, primary_key=True)
    Location = db.Column(db.String(100), nullable=False, unique=True)
    Capacity = db.Column(db.Integer, nullable=False)

    def __init__(self, Location, Capacity):
        self.Location = Location
        self.Capacity = Capacity



class Inventory(db.Model):
    __tablename__ = 'Inventory'
    InventoryID = db.Column(db.Integer, primary_key=True)
    WarehouseID = db.Column(db.Integer, db.ForeignKey('Warehouse.WarehouseID'), nullable=False)
    StockQuantity = db.Column(db.Integer, nullable=False, default=0)
    warehouse = db.relationship('Warehouse', backref='Inventory')

    def __init__(self, WarehouseID, StockQuantity):
        self.WarehouseID = WarehouseID
        self.StockQuantity = StockQuantity

with app.app_context():
    db.create_all()


def add_category(category_name):
    try:
        new_category = Category(CategoryName=category_name)  #  <--  We only provide CategoryName

        db.session.add(new_category)

        
        db.session.commit()
        print(f"Category '{category_name}' added successfully!")
        return True  # Indicate success
    except Exception as e:
        db.session.rollback()  # Rollback changes in case of error
        print(f"Error adding category: {e}")
        return False 


def get_status_text(stock):
    if stock > 10:
        return 'In Stock'
    elif 0 < stock <= 10:
        return 'Low Stock'
    else:
        return 'Out of Stock'

def get_status_class(stock):
    if stock > 10:
        return 'status-in-stock'
    elif 0 < stock <= 10:
        return 'status-low-stock'
    else:
        return 'status-out-of-stock'

@app.route('/product_management', methods=['GET', 'POST'])
def product_management():
    print("here")
    if request.method == 'GET':
        products = Product.query.all()
        suppliers = User.query.filter_by(role='Supplier').all()
        categories = Category.query.all()
        return render_template('product_management.html', products=products, suppliers=suppliers, categories=categories, get_status_text=get_status_text, get_status_class=get_status_class)
    elif request.method == 'POST':
        data = request.get_json()  # Get the JSON data from the request
        print("Received data:", data)  # Debugging
        try:
            name = data['name']
            category_id = int(data['category_id'])  # Convert to integer
            supplier_id = int(data['supplier_id']) # Convert to integer
            stock = int(data['stock'])
            price = float(data['price'])

            # Create a new Product object
            new_product = Product(
                Name=name,
                category_id=category_id,
                SupplierID=supplier_id,
                MRP=price,
                StockQuantity=stock
            )

            db.session.add(new_product)
            db.session.commit()
            print("Product added to database") # Debugging
            return jsonify({'message': 'Product added successfully!'}), 200  #  Send JSON response
        except Exception as e:
            db.session.rollback()
            print(f"Error adding product: {e}")
            return jsonify({'error': str(e)}), 500


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print(f"Attempting login with email: {email}")
        user = User.query.filter_by(email=email).first()
        if user:
            print(f"User found with email: {email}")
            print(f"Stored hashed password: {user.password}")  # Print the stored hash
            if check_password_hash(user.password, password):
                print("Password matches!")
                session['user_id'] = user.id
                session['user_name'] = user.name
                session['user_role'] = user.role
                if user.role == 'Customer':
                    return redirect(url_for('customer_dashboard'))
                elif user.role == 'Admin':
                    return redirect(url_for('admin_dashboard'))
                elif user.role == 'Supplier':
                    return redirect(url_for('supplier_dashboard'))
                else:
                    return "Invalid Role"
            else:
                print("Password does not match")
                return render_template('login.html', error='Invalid credentials')
        else:
            print(f"No user found with email: {email}")
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        print(f"Name: {name}, Email: {email}, Role: {role}")  # Check the values
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print("Email already exists")
            return render_template('register.html', error="Email already exists")
        hashed_password = generate_password_hash(password)
        new_user = User(name=name, email=email, password=hashed_password, role=role)
        db.session.add(new_user)
        try:
            db.session.commit()
            print("User added to database")  # See if this is printed
        except Exception as e:
            print(f"Error adding user to database: {e}")  # Print the error
            db.session.rollback()  # Rollback the transaction to prevent data corruption
            return render_template('register.html', error="Database error: Could not register user.")

        if role == 'Customer':  # Check the role and redirect
            print("Role is Customer, redirecting...")
            user = User.query.filter_by(email=email).first()  # get the new user.
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_role'] = user.role
            print(f"Session set: {session}")  # Check the session
            return redirect(url_for('customer_dashboard'))
        elif role == 'Admin':
            print("Role is Admin, redirecting...")
            user = User.query.filter_by(email=email).first()  # get the new user.
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_role'] = user.role
            print(f"Session set: {session}")  # Check the session
            return redirect(url_for('admin_dashboard'))
        elif role == 'Supplier':
            print("Role is Supplier, redirecting...")
            user = User.query.filter_by(email=email).first() 
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_role'] = user.role
            print(f"Session set: {session}")  # Check the session
            # return redirect(url_for('_dashboard'))
            print("Role is not Customer, redirecting to login")
            return redirect(url_for('login'))  # send to login if not customer
        
    print("GET request for register")
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Clear Session
    session.pop('user_name', None)
    session.pop('user_role', None)
    return redirect(url_for('index'))  # Redirect to the home page



@app.route('/customer_dashboard')
def customer_dashboard():
    if 'user_id' not in session or session['user_role'] != 'Customer':
        print("Unauthorized access to customer dashboard")
        return redirect(url_for('login'))  # Redirect non-customers
    name = session['user_name']
    print(f"Customer Dashboard accessed by: {name}")
    return render_template('customer_dashboard.html', name=name)



@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['user_role'] != 'Admin':
        return redirect(url_for('login'))  # Redirect non-admins
    name = session['user_name']
    print(f"Admin Dashboard accessed by: {name}")
    return render_template('admin_dashboard.html', name=name)


@app.route('/supplier_dashboard')
def supplier_dashboard():
    if 'user_id' not in session or session['user_role'] != 'Supplier':
        return redirect(url_for('login'))  # Redirect non-suppliers
    name = session['user_name']
    print(f"Supplier Dashboard accessed by: {name}")
    return render_template('supplier_dashboard.html', name=name)





@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/orders')
def orders():
    return render_template('orders.html')

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/reviews')
def reviews():
    return render_template('reviews.html')

@app.route('/reports')
def reports():
    return render_template('reports.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/order_management')
def order_management():
    return render_template('order_management.html')




@app.route('/user_management', methods=['GET', 'POST'])
def user_management():
    if 'user_id' not in session or session['user_role'] != 'Admin':
        return redirect(url_for('login'))

    # Get the role filter from the form
    selected_role = request.form.get('role', 'All')  # Default to 'All' if no role is selected.

    # Fetch users, filtering by role if necessary
    if selected_role == 'All':
        users = User.query.all()
    else:
        users = User.query.filter_by(role=selected_role).all()

    roles = ['All', 'Customer', 'Admin', 'Supplier']  # for dropdown

    return render_template('user_management.html', users=users, roles=roles, selected_role=selected_role)



@app.route('/admin_order_management')
def admin_order_management():
    return render_template('admin_order_management.html')

    

@app.route('/add_product')
def add_product():
    return render_template('add_product.html')

if __name__ == '__main__':
    with app.app_context():

        db.create_all()
        # category_name_to_add = "Toy"  # Replace with the category name you want to add
        # add_category(category_name_to_add)
    app.run(debug=True)
