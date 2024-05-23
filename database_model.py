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
    # Define the relationships
    order_items = db.relationship('OrderItem', backref=db.backref('order', lazy=True))


class OrderItem(db.Model):
    __tablename__ = 'order_item'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.p_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(precision=20, scale=1), nullable=False)


class RestaurantTables(db.Model):
    __tablename__ = 'restaurant_tables'
    table_id = db.Column(db.Integer, primary_key=True)
    table_name = db.Column(db.String(4), unique=True, nullable=False)
    table_pax = db.Column(db.Integer, default=4, nullable=False)


class TableReservations(db.Model):
    __tablename__ = 'table_reservations'
    reservation_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.cust_id'), nullable=False)
    table_id = db.Column(db.Integer, db.ForeignKey('restaurant_tables.table_id'), nullable=False)
    reservation_date = db.Column(db.Date, nullable=False)
    number_of_guests = db.Column(db.Integer, nullable=False)
    special_requests = db.Column(db.Text)
    completed = db.Column(db.Integer, default=0)
    upcoming = db.Column(db.Integer, default=0)
    in_progress = db.Column(db.Integer, default=0)
    status = db.Column(db.Enum('Reserved', 'Completed', 'Cancelled', name='reservation_status'), default='Reserved')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Relationships
    customers = db.relationship('Customers', backref=db.backref('table_reservations', lazy=True))
    restaurant_tables = db.relationship('RestaurantTables', backref=db.backref('table_reservations', lazy=True))


class TimeSlots(db.Model):
    __tablename__ = 'time_slots'
    time_slot_id = db.Column(db.Integer, primary_key=True)
    reservation_id = db.Column(db.Integer, db.ForeignKey('table_reservations.reservation_id'), nullable=False)
    slot_time_08_am = db.Column(db.String(10), default='08:00am', nullable=True)
    description_08_am = db.Column(db.String(255), nullable=True)
    slot_time_09_am = db.Column(db.String(10), default='09:00am', nullable=True)
    description_09_am = db.Column(db.String(255), nullable=True)
    slot_time_10_am = db.Column(db.String(10), default='10:00am', nullable=True)
    description_10_am = db.Column(db.String(255), nullable=True)
    slot_time_11_am = db.Column(db.String(10), default='11:00am', nullable=True)
    description_11_am = db.Column(db.String(255), nullable=True)
    slot_time_12_pm = db.Column(db.String(10), default='12:00pm', nullable=True)
    description_12_pm = db.Column(db.String(255), nullable=True)
    slot_time_01_pm = db.Column(db.String(10), default='01:00pm', nullable=True)
    description_01_pm = db.Column(db.String(255), nullable=True)
    slot_time_02_pm = db.Column(db.String(10), default='02:00pm', nullable=True)
    description_02_pm = db.Column(db.String(255), nullable=True)
    slot_time_03_pm = db.Column(db.String(10), default='03:00pm', nullable=True)
    description_03_pm = db.Column(db.String(255), nullable=True)
    slot_time_04_pm = db.Column(db.String(10), default='04:00pm', nullable=True)
    description_04_pm = db.Column(db.String(255), nullable=True)
    slot_time_05_pm = db.Column(db.String(10), default='05:00pm', nullable=True)
    description_05_pm = db.Column(db.String(255), nullable=True)
    slot_time_06_pm = db.Column(db.String(10), default='06:00pm', nullable=True)
    description_06_pm = db.Column(db.String(255), nullable=True)
    slot_time_07_pm = db.Column(db.String(10), default='07:00pm', nullable=True)
    description_07_pm = db.Column(db.String(255), nullable=True)
    slot_time_08_pm = db.Column(db.String(10), default='08:00pm', nullable=True)
    description_08_pm = db.Column(db.String(255), nullable=True)
    slot_time_09_pm = db.Column(db.String(10), default='09:00pm', nullable=True)
    description_09_pm = db.Column(db.String(255), nullable=True)
    slot_time_10_pm = db.Column(db.String(10), default='10:00pm', nullable=True)
    description_10_pm = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Relationships
    table_reservations = db.relationship('TableReservations', backref=db.backref('time_slots', lazy=True))
