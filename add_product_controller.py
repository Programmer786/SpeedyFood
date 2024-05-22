from sqlalchemy.orm import joinedload
from app import app
from sqlalchemy.exc import IntegrityError
from sqlalchemy import asc, desc
from database_model import *
# from database_model import db, Users,Rol
from flask import render_template, flash, session, request, redirect, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import os
import random


@app.route('/add_product', methods=['POST', 'GET'])
def add_product():
    if 'cnic' and 'user_name' and 'rol_name' in session:
        # try:
        # this is for get province
        all_product_category_name = ProductCategory.query.all()
        # this is for table data retrieve Ascending order
        all_restaurant__name = RestaurantNames.query.all()

        all_products_data_retrieve = (
            Products.query
            .join(RestaurantNames)
            .options(joinedload(Products.restaurant_names))  # Eager load the associated project
            .join(ProductCategory)
            .options(joinedload(Products.product_category))  # Eager load the associated project
            .all()
        )

        get_restaurant_id_of_user = ""

        if request.method == 'POST':
            get_p_name = request.form['p_name']
            get_p_description = request.form['p_description']
            get_p_price = request.form['p_price']
            get_category_id = request.form['get_category_id']
            get_uploaded_p_image = request.files['p_image']  # Assuming the image is a file upload, handle it accordingly

            if session['rol_name'] == "Administrator":
                get_restaurant_id = request.form['get_restaurant_id']  # if Admin Then POST Request
            else:  # else Manager direct get from session['restaurant_id']
                get_restaurant_id = session['restaurant_id']

            # Check if required fields are not empty
            if not (get_p_name and get_p_price and get_category_id):
                flash("Error. Please fill all the required fields", "danger")
                return redirect('/add_product')

            try:
                new_entry_save_by_products = Products(
                    p_name=get_p_name,
                    p_description=get_p_description,
                    p_price=get_p_price,
                    pc_id=get_category_id,
                    restaurant_id=get_restaurant_id
                )

                if get_uploaded_p_image:
                    # Get the original file extension
                    _, file_extension = os.path.splitext(get_uploaded_p_image.filename)
                    # Generate a random 4-digit number
                    random_number = random.randint(1000000, 9999999)
                    # UserId Get from Session
                    get_user_id = session['UserId']
                    # Combine random_number, employee ID, and file extension to create a custom filename
                    custom_filename = f"{random_number}_{get_user_id}{file_extension}"
                    # Save the file and update the database record with the file path
                    file_path_system = os.path.join(app.config['UPLOAD_FOLDER'], custom_filename)  # Set your upload folder path
                    file_full_name = os.path.join("", custom_filename)  # Set your No path for database column
                    get_uploaded_p_image.save(file_path_system)
                    new_entry_save_by_products.p_image = file_full_name

                db.session.add(new_entry_save_by_products)
                db.session.commit()
                flash(f"Record Successfully Saved", "success")
                return redirect('/add_product')
            except IntegrityError:
                db.session.rollback()
                flash("Error. Duplicate data detected. Please do not proceed and try again.", "danger")
                return redirect('/add_product')  # Add return statement here
        else:
            return render_template('Administrator/add_product.html', all_restaurant__name=all_restaurant__name,
                                   all_product_category_name=all_product_category_name, all_products_data_retrieve=all_products_data_retrieve)
        # except Exception as e:
        #     # If an error occurs during database connection, display error message
        #     db.session.rollback()
        #     flash(f"Failed to connect to the database. -> Error: {str(e)}" "", "danger")
        #     return render_template('Administrator/login.html')
    else:
        return render_template('Administrator/login.html')


@app.route('/delete_product/<int:Product_Id>')
def delete_product(Product_Id):
    if 'cnic' and 'user_name' and 'rol_name' in session:
        try:
            # First delete the file
            product = Products.query.get_or_404(Product_Id)
            file_path = None  # Initialize file_path with a default value
            if product.p_image is not None:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], product.p_image)  # Construct the full path to the file
            # Delete the file from the directory
            if file_path is not None and os.path.exists(file_path):
                os.remove(file_path)

            # get specific Product_Id from clerk Table and then check date with Product_Id related
            select_one_products = Products.query.filter_by(p_id=Product_Id).first()
            db.session.delete(select_one_products)
            db.session.commit()
            flash("Record Successfully Deleted", "success")
            return redirect('/add_product')
        except IntegrityError:
            db.session.rollback()
            flash("Error. Please try again", "danger")
            return redirect('/add_product')  # Add return statement here
    else:
        return render_template('Administrator/login.html')


@app.route('/update_product/<int:Product_Id>', methods=['GET', 'POST'])
def update_product(Product_Id):
    if 'cnic' and 'user_name' and 'rol_name' in session:
        try:
            # this is for table data retrieve of the Specific product
            one_product = Products.query.get_or_404(Product_Id)

            if request.method == 'POST':
                get_p_name = request.form['p_name']
                get_p_description = request.form['p_description']
                get_p_price = request.form['p_price']
                get_category_id = request.form['get_category_id']
                if session['rol_name'] == "Administrator":
                    get_restaurant_id = request.form['get_restaurant_id']  # if Admin Then POST Request
                else:  # else Manager direct get from session['restaurant_id']
                    get_restaurant_id = session['restaurant_id']

                # Check if required fields are not empty
                if not (get_p_name and get_p_description and get_p_price and get_category_id and get_restaurant_id):
                    flash("Error. Please fill all the required fields", "danger")
                    return redirect('/add_product')

                try:
                    one_product.p_name = get_p_name
                    one_product.p_description = get_p_description
                    one_product.p_price = get_p_price
                    one_product.pc_id = get_category_id
                    one_product.restaurant_id = get_restaurant_id

                    db.session.commit()
                    flash("Record Successfully Updated", "success")
                    return redirect('/add_product')
                except IntegrityError:
                    db.session.rollback()
                    flash("Error. Duplicate data detected. Please do not proceed and try again.", "danger")
                    return redirect('/add_product')
            else:
                return redirect('/add_product')
        except Exception as e:
            # If an error occurs during database connection, display error message
            db.session.rollback()
            flash(f"Failed to connect to the database. -> Error: {str(e)}" "", "danger")
            return render_template('Administrator/login.html')
    else:
        return render_template('Administrator/login.html')


@app.route('/update_product_image/<int:Product_Id>', methods=['GET', 'POST'])
def update_product_image(Product_Id):
    if 'cnic' and 'user_name' and 'rol_name' in session:
        try:
            if request.method == 'POST':
                # First delete the file
                product = Products.query.get_or_404(Product_Id)
                file_path = None  # Initialize file_path with a default value
                if product.p_image is not None:
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], product.p_image)  # Construct the full path to the file
                # Delete the file from the directory
                if file_path is not None and os.path.exists(file_path):
                    os.remove(file_path)

                # Get New Image Path
                get_uploaded_p_image = request.files['p_image']

                if get_uploaded_p_image:
                    # Get the original file extension
                    _, file_extension = os.path.splitext(get_uploaded_p_image.filename)
                    # Generate a random 4-digit number
                    random_number = random.randint(1000000, 9999999)
                    # UserId Get from Session
                    get_user_id = session['UserId']
                    # Combine random_number, employee ID, and file extension to create a custom filename
                    custom_filename = f"{random_number}_{get_user_id}{file_extension}"
                    # Save the file and update the database record with the file path
                    file_path_system = os.path.join(app.config['UPLOAD_FOLDER'], custom_filename)  # Set your upload folder path
                    file_full_name = os.path.join("", custom_filename)  # Set your No path for database column
                    get_uploaded_p_image.save(file_path_system)
                    product.p_image = file_full_name

                db.session.commit()
                flash("Product Image Successfully Updated", "success")
                return redirect('/add_product')
            else:
                return redirect('/add_product')
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "danger")
            return redirect('/add_product')
    else:
        return render_template('Administrator/login.html')


@app.route('/update_stock', methods=['POST', 'GET'])
def update_stock():
    if 'cnic' and 'user_name' and 'rol_name' in session:
        try:
            # this is for get province
            all_product_category_name = ProductCategory.query.all()
            # this is for table data retrieve Ascending order
            all_restaurant__name = RestaurantNames.query.all()

            all_products_data_retrieve = (
                Products.query
                .join(RestaurantNames)
                .options(joinedload(Products.restaurant_names))  # Eager load the associated project
                .join(ProductCategory)
                .options(joinedload(Products.product_category))  # Eager load the associated project
                .all()
            )

            get_restaurant_id_of_user = ""

            if request.method == 'POST':
                get_p_name = request.form['p_name']
                get_p_description = request.form['p_description']
                get_p_price = request.form['p_price']
                get_category_id = request.form['get_category_id']
                get_uploaded_p_image = request.files['p_image']  # Assuming the image is a file upload, handle it accordingly

                if session['rol_name'] == "Administrator":
                    get_restaurant_id = request.form['get_restaurant_id']  # if Admin Then POST Request
                else:  # else Manager direct get from session['restaurant_id']
                    get_restaurant_id = session['restaurant_id']

                # Check if required fields are not empty
                if not (get_p_name and get_p_price and get_category_id):
                    flash("Error. Please fill all the required fields", "danger")
                    return redirect('/update_stock')

                try:
                    new_entry_save_by_products = Products(
                        p_name=get_p_name,
                        p_description=get_p_description,
                        p_price=get_p_price,
                        pc_id=get_category_id,
                        restaurant_id=get_restaurant_id
                    )

                    if get_uploaded_p_image:
                        # Get the original file extension
                        _, file_extension = os.path.splitext(get_uploaded_p_image.filename)
                        # Generate a random 4-digit number
                        random_number = random.randint(1000000, 9999999)
                        # UserId Get from Session
                        get_user_id = session['UserId']
                        # Combine random_number, employee ID, and file extension to create a custom filename
                        custom_filename = f"{random_number}_{get_user_id}{file_extension}"
                        # Save the file and update the database record with the file path
                        file_path_system = os.path.join(app.config['UPLOAD_FOLDER'], custom_filename)  # Set your upload folder path
                        file_full_name = os.path.join("", custom_filename)  # Set your No path for database column
                        get_uploaded_p_image.save(file_path_system)
                        new_entry_save_by_products.p_image = file_full_name

                    db.session.add(new_entry_save_by_products)
                    db.session.commit()
                    flash(f"Record Successfully Saved", "success")
                    return redirect('/update_stock')
                except IntegrityError:
                    db.session.rollback()
                    flash("Error. Duplicate data detected. Please do not proceed and try again.", "danger")
                    return redirect('/update_stock')  # Add return statement here
            else:
                return render_template('Administrator/update_stock.html', all_restaurant__name=all_restaurant__name,
                                       all_product_category_name=all_product_category_name, all_products_data_retrieve=all_products_data_retrieve)
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "danger")
            return redirect('/update_stock')  # Add return statement here
    else:
        return render_template('Administrator/login.html')


@app.route('/update_product_stock_active/<int:Product_Id>', methods=['GET', 'POST'])
def update_product_stock_active(Product_Id):
    if 'cnic' and 'user_name' and 'rol_name' in session:
        try:
            one_product = Products.query.get_or_404(Product_Id)
            if request.method == 'POST':
                get_p_stock = request.form.get('p_stock')

                # Check if p_isActive key exists in form data and if get_p_stock is not equal to 0
                if 'p_isActive' in request.form and get_p_stock != '0':
                    # Checkbox is checked and stock is not 0
                    get_p_is_active = True
                    stock = get_p_stock
                else:
                    # Checkbox is unchecked or stock is 0
                    get_p_is_active = False
                    stock = 0

                # Check if required fields are not empty
                if not get_p_stock:
                    flash("Error. Please fill all the required fields", "danger")
                    return redirect('/update_stock')

                one_product.p_stock = stock
                one_product.p_isActive = get_p_is_active

                db.session.commit()
                flash(f"{one_product.p_name} Record Successfully Updated", "success")
                return redirect('/update_stock')
            else:
                return redirect('/update_stock')
        except Exception as e:
            db.session.rollback()
            flash(f"Failed to connect to the database. -> Error: {str(e)}", "danger")
            return render_template('Administrator/login.html')
    else:
        return render_template('Administrator/login.html')
