from app import app
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta, datetime
from sqlalchemy import create_engine, Numeric
import os
from flask_migrate import Migrate

# Session configuration
app.permanent_session_lifetime = timedelta(hours=1)

# Database configuration for the online MySQL database on cPanel
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://cmsfarca_app:Pakistan007!!!@cp6.mywebsitebox.com/cmsfarca_cms_application'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/rmsfood_rms_application'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/cms_application'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
# Set the upload folder
UPLOAD_FOLDER = 'static/uploaded_files'
# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
# Configure the Flask app with the upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)
# Model Migrate into database tables Automatically
# First initialize only one time command (flask db init)
# apply those command Step:1(flask db migrate)Step:2 (flask db upgrade)
migrate = Migrate(app, db)


class Users(db.Model):
    __tablename__ = 'users'
    idUsers = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50), unique=True, nullable=True)
    full_name = db.Column(db.String(50), unique=False, nullable=True)
    email = db.Column(db.String(50), unique=True, nullable=True)
    phone = db.Column(db.String(50), unique=True, nullable=True)
    cnic = db.Column(db.String(20), unique=True, nullable=True)
    gender = db.Column(db.String(20), unique=False, nullable=True)
    rol_name = db.Column(db.String(20), unique=False, nullable=True)
    password = db.Column(db.String(256))
    photo = db.Column(db.String(256))  # e.g., db.Column(db.LargeBinary) for LONGBLOB).
    isActive = db.Column(db.Boolean, nullable=False)
    registrationDate = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant_names.restaurant_id'), nullable=True)
    # Define the relationships
    restaurant_names = db.relationship('RestaurantNames', backref=db.backref('users', lazy=True))


# Create a province model. The table name "province" will automatically be assigned to the model’s table.
class Province(db.Model):
    __tablename__ = 'province'
    province_sno = db.Column(db.Integer, primary_key=True)
    province_name = db.Column(db.String(50), unique=True, nullable=False)


# Create a District model. The table name "district" will automatically be assigned to the model’s table.
class District(db.Model):
    __tablename__ = 'district'
    district_sno = db.Column(db.Integer, primary_key=True)
    district_province_sno = db.Column(db.Integer, db.ForeignKey('province.province_sno'), nullable=False)
    district_name = db.Column(db.String(100), unique=True, nullable=False)
    # Define the relationships
    province = db.relationship('Province', backref=db.backref('districts', lazy=True))


# Assuming you have a Bank model defined in your code
class RestaurantNames(db.Model):
    __tablename__ = 'restaurant_names'
    restaurant_id = db.Column(db.Integer, primary_key=True)
    restaurant_name = db.Column(db.String(50), nullable=False)
    restaurant_district_sno = db.Column(db.Integer, db.ForeignKey('district.district_sno'), nullable=False)
    # Define the relationships
    district = db.relationship('District', backref=db.backref('restaurant_names', lazy=True))


class ProductCategory(db.Model):
    __tablename__ = 'product_category'
    pc_id = db.Column(db.Integer, primary_key=True)
    pc_name = db.Column(db.String(50), unique=True, nullable=False)


class Products(db.Model):
    __tablename__ = 'products'
    p_id = db.Column(db.Integer, primary_key=True)
    p_name = db.Column(db.String(100), nullable=False)
    p_description = db.Column(db.Text, nullable=True)
    p_price = db.Column(Numeric(precision=20, scale=1), nullable=False)
    p_image = db.Column(db.String(255), nullable=True)
    p_isActive = db.Column(db.Boolean, nullable=False, default=True)
    p_registrationDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    pc_id = db.Column(db.Integer, db.ForeignKey('product_category.pc_id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant_names.restaurant_id'), nullable=True)
    p_stock = db.Column(db.Integer, nullable=True, default=0)
    # Define the relationships
    restaurant_names = db.relationship('RestaurantNames', backref=db.backref('products', lazy=True))
    product_category = db.relationship('ProductCategory', backref=db.backref('products', lazy=True))


class Customers(db.Model):
    __tablename__ = 'customers'
    cust_id = db.Column(db.Integer, primary_key=True)
    cust_user_name = db.Column(db.String(50), unique=True, nullable=False)
    cust_full_name = db.Column(db.String(50), unique=False, nullable=False)
    cust_phone = db.Column(db.String(50), unique=True, nullable=False)
    cust_gender = db.Column(db.String(20), unique=False, nullable=False)
    cust_rol_name = db.Column(db.String(20), unique=False, nullable=False)
    cust_password = db.Column(db.String(256), nullable=False)
    cust_photo = db.Column(db.String(256))  # e.g., db.Column(db.LargeBinary) for LONGBLOB).
    cust_registrationDate = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    isActive = db.Column(db.Boolean, nullable=False)


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.cust_id'), nullable=False)
    total_price = db.Column(db.Numeric(precision=20, scale=1), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_verified = db.Column(db.String(50), default='Waiting', nullable=True)  # e.g., 'Waiting', 'Verification', 'Approved', 'Reject'
    transaction_no = db.Column(db.String(50), unique=True, nullable=True)
    cust_drop_address = db.Column(db.String(255), nullable=True)
    delivery_status = db.Column(db.String(50), nullable=True)  # e.g. 'Want Delivery', 'OnTheWay', 'Deliver'
    isActive = db.Column(db.Boolean, default=False, nullable=True)
    # Define the relationships
    order_items = db.relationship('OrderItem', backref=db.backref('order', lazy=True))
    customers = db.relationship('Customers', backref=db.backref('order', lazy=True))


class OrderItem(db.Model):
    __tablename__ = 'order_item'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.p_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(precision=20, scale=1), nullable=False)
    # Define the relationships
    products = db.relationship('Products', backref=db.backref('order_item', lazy=True))


class RestaurantTables(db.Model):
    __tablename__ = 'restaurant_tables'
    table_id = db.Column(db.Integer, primary_key=True)
    table_name = db.Column(db.String(4), unique=True, nullable=False)
    table_pax = db.Column(db.Integer, default=4, nullable=False)


class TableReservations(db.Model):
    __tablename__ = 'table_reservations'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.cust_id'), nullable=False)
    table_id = db.Column(db.Integer, db.ForeignKey('restaurant_tables.table_id'), nullable=False)
    number_of_chairs = db.Column(db.Integer, nullable=False)
    reservation_date = db.Column(db.Date, nullable=False)
    time_from = db.Column(db.Time, nullable=False)
    time_to = db.Column(db.Time, nullable=False)
    status = db.Column(db.Enum('Reserved', 'Completed', 'Cancelled', name='reservation_status'), default='Reserved')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Relationships
    customers = db.relationship('Customers', backref=db.backref('table_reservations', lazy=True))
    restaurant_tables = db.relationship('RestaurantTables', backref=db.backref('table_reservations', lazy=True))
