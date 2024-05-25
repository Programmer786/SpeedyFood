import os
from flask import Flask

app = Flask(__name__)

# Set the secret key using an environment variable
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'Pakistan786$$$')

# # Importing controllers and routes
from user_authentication_controller import *
from add_categorys_controller import *
from add_product_controller import *
from customer_authentication_controller import *
from customer_cart_controller import *

if __name__ == '__main__':
    app.run(debug=True)
