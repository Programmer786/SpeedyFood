from sqlalchemy.orm import joinedload
from app import app
from sqlalchemy.exc import IntegrityError
from sqlalchemy import asc
from database_model import *
# from database_model import db, Users,Rol
from flask import render_template, flash, session, request, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date


@app.route('/cust_register', methods=['POST', 'GET'])
def customer_registration_page():
    if request.method == 'POST':
        try:
            c_full_name = request.form.get('full_name')
            c_phone = request.form.get('phone_number')
            c_gender = request.form.get('gender')
            c_user_name = request.form.get('user_name')
            c_password = request.form.get('password')
            c_conform_password = request.form.get('conform_password')

            if ' ' in c_user_name:
                flash("Error! Username cannot contain spaces.", "danger")
                return redirect('/cust_register')

            if (c_full_name != "") and (c_phone != "") and (c_user_name != "") and (c_password != "") and (
                    c_conform_password != ""):
                register_customer = Customers.query.filter_by(cust_user_name=c_user_name).count()
                if c_password == c_conform_password:
                    if register_customer < 1:
                        # change_to_hashed_password = generate_password_hash(c_password, "sha256") #old method
                        change_to_hashed_password = generate_password_hash(c_password, method='scrypt')  # new method

                        new_entry_register_customer = Customers(
                            cust_user_name=c_user_name,
                            cust_full_name=c_full_name,
                            cust_phone=c_phone,
                            cust_gender=c_gender,
                            cust_rol_name="Customer",
                            cust_password=change_to_hashed_password,
                            cust_registrationDate=datetime.now(),
                            isActive=1
                        )
                        db.session.add(new_entry_register_customer)
                        db.session.commit()
                        flash("Successfully Register.", "success")
                        return redirect('/cust_register')
                    else:
                        flash(
                            "Error! The Account is Already Registered So goto Login otherwise Contact to your Administrator. "
                            "Thank you",
                            "danger")
                else:
                    flash("Error! Your conform password is wrong please try again", "danger")
            else:
                flash("Error! Please fill out this field.", "danger")
        except Exception as e:
            # If an error occurs during database connection, display error message
            db.session.rollback()
            flash("Error: Your Contact Number is Already Attached to Another Account, So Please Try with Another Contact Number.", "danger")
            return redirect('/cust_register')
    else:
        return render_template('Customer/customer_register.html')

    # Ensure to return a valid response in all cases
    return render_template('Customer/customer_register.html')


@app.route('/cust_login', methods=['POST', 'GET'])
def customer_login_page():
    if 'Cust_Id' and 'Cust_Phone' and 'Cust_UserName' in session:
        session_cust_rol_name = session['cust_RolName']
        if session_cust_rol_name == "Customer":
            return redirect('/')
        else:
            return redirect('/cust_logout')
    else:
        if request.method == 'POST':
            c_user_name = request.form['user_name']
            c_password = request.form['login_password']
            try:
                customer = Customers.query.filter_by(cust_user_name=c_user_name, isActive=1).first()
                # If no record found by this c_user_name
                if customer is not None:
                    if customer.isActive == 1:
                        passwd = customer.cust_password
                        # If password decrypt and record do not match with password
                        if check_password_hash(passwd, c_password):  # if passwd == a_password: without encryption
                            session.permanent = True  # <--- makes the permanent session
                            session['Cust_Id'] = customer.cust_id
                            session['Cust_UserName'] = customer.cust_user_name
                            session['Cust_FullName'] = customer.cust_full_name
                            session['Cust_Phone'] = customer.cust_phone
                            session['Cust_Photo'] = customer.cust_photo
                            session['cust_RolName'] = customer.cust_rol_name

                            if customer.cust_rol_name == "Customer":
                                return redirect('/')
                            else:
                                return redirect('/cust_logout')
                        else:
                            flash("Error! Invalid Detail, Please try Again!", "danger")
                            return render_template('Customer/customer_login.html')
                    else:
                        flash("Error! Please Contact to Administrator! Your Account is Looked.", "danger")
                        return render_template('Customer/customer_login.html')
                else:
                    flash("Error! Invalid Details, Please Contact to Administrator!", "danger")
                    return render_template('Customer/customer_login.html')
            except Exception as e:
                # If an error occurs during database connection, display error message
                db.session.rollback()
                flash(f"Failed to connect to the database. -> Error: {str(e)}" "", "danger")
                return render_template('Customer/customer_login.html')
        return render_template('Customer/customer_login.html')


@app.route('/cust_disable_role_user/<int:UserId>')
def disable_role_user1(UserId):
    if 'Cust_Id' and 'Cust_Phone' and 'Cust_UserName' in session:
        try:
            # get specific user idUsers from clerk Table and then check date with UserId related
            sel_one_user = Users.query.filter_by(idUsers=UserId).first()
            sel_one_user.isActive = 0
            db.session.commit()
            flash("Record Successfully Disable", "success")
            return redirect('/role')
        except Exception as e:
            # If an error occurs during database connection, display error message
            db.session.rollback()
            flash(f"Failed to connect to the database. -> Error: {str(e)}" "", "danger")
            return render_template('Customer/customer_login.html')
    else:
        return render_template('Customer/customer_login.html')


@app.route('/cust_enable_role_user/<int:UserId>')
def enable_role_user1(UserId):
    if 'Cust_Id' and 'Cust_Phone' and 'Cust_UserName' in session:
        try:
            # get specific user idUsers from clerk Table and then check date with UserId related
            sel_one_user = Users.query.filter_by(idUsers=UserId).first()
            sel_one_user.isActive = 1
            db.session.commit()
            flash("Record Successfully Enable", "success")
            return redirect('/role')
        except Exception as e:
            # If an error occurs during database connection, display error message
            db.session.rollback()
            flash(f"Failed to connect to the database. -> Error: {str(e)}" "", "danger")
            return render_template('Customer/customer_login.html')
    else:
        return render_template('Customer/customer_login.html')


@app.route('/cust_user_for_update/<int:UserId>', methods=['POST', 'GET'])
def user_for_update1(UserId):
    if 'Cust_Id' and 'Cust_Phone' and 'Cust_UserName' in session:
        try:
            # get specific user SNo from clerk Table and then check date with SNo related
            get_restaurant_sno = request.form.get('get_restaurant_id')
            get_name = request.form['name']
            get_email = request.form['email']
            get_cnic = request.form['cnic']
            get_phone = request.form['phone']
            get_gender = request.form['gender']

            update_user = Users.query.filter_by(idUsers=UserId).first()
            update_user.name = get_name
            update_user.email = get_email
            update_user.cnic = get_cnic
            update_user.phone = get_phone
            update_user.gender = get_gender
            update_user.restaurant_id = get_restaurant_sno

            db.session.add(update_user)
            db.session.commit()
            flash("Record Successfully Updated", "success")
            return redirect('/role')
        except IntegrityError:
            db.session.rollback()
            flash("Error. Duplicate CNIC Not Acceptable", "danger")
            return redirect('/role')  # Add return statement here
    else:
        return render_template('Customer/customer_login.html')


@app.route('/cust_change_password/<int:UserId>', methods=['POST', 'GET'])
def change_password1(UserId):
    if 'Cust_Id' and 'Cust_Phone' and 'Cust_UserName' in session:
        try:
            # Retrieve form data
            r_password = request.form.get('password')
            r_conform_password = request.form.get('conform_password')

            if r_password == r_conform_password:
                # change_to_hashed_password = generate_password_hash(r_password, "sha256") #old method
                change_to_hashed_password = generate_password_hash(r_password, method='scrypt')  # new method

                update_user_password = Users.query.filter_by(idUsers=UserId).first()
                update_user_password.password = change_to_hashed_password
                db.session.add(update_user_password)
                db.session.commit()
                flash("Password changed successfully.", "success")
                return redirect('/role')
            else:
                flash("Error! Your confirm password is wrong, please try again", "danger")
                return redirect('/role')
        except IntegrityError:
            db.session.rollback()
            flash("Error. Duplicate CNIC Not Acceptable", "danger")
            return redirect('/role')  # Add return statement here
    else:
        # Render the form for GET requests
        return render_template('Customer/customer_login.html')


@app.route('/update_customer_profile/<int:CustId>', methods=['POST', 'GET'])
def update_customer_profile(CustId):
    if 'Cust_Id' and 'Cust_Phone' and 'Cust_UserName' in session:
        try:
            customer_data_retrieve = Customers.query.filter_by(cust_id=CustId).first()

            return render_template('Customer/update_customer_profile.html',
                                   customer_data_retrieve=customer_data_retrieve)
        except Exception as e:
            # If an error occurs during database connection, display an error message
            db.session.rollback()
            flash(f"Failed to connect to the database. -> Error: {str(e)}" "", "danger")
            return redirect('/')
    else:
        return render_template('Customer/customer_login.html')


@app.route('/customer_side_for_update/<int:CustId>', methods=['POST', 'GET'])
def customer_side_for_update(CustId):
    if 'Cust_Id' and 'Cust_Phone' and 'Cust_UserName' in session:
        try:
            # get specific user SNo from clerk Table and then check date with SNo related
            get_user_name = request.form['user_name']
            get_full_name = request.form['full_name']
            get_phone = request.form['phone']
            get_gender = request.form['gender']

            update_customer = Customers.query.filter_by(cust_id=CustId).first()
            update_customer.cust_user_name = get_user_name
            update_customer.cust_full_name = get_full_name
            update_customer.cust_phone = get_phone
            update_customer.cust_gender = get_gender

            db.session.add(update_customer)
            db.session.commit()
            flash("Record Successfully Updated", "success")
            return redirect(f'/update_customer_profile/{CustId}')
        except Exception as e:
            # If an error occurs during database connection, display an error message
            db.session.rollback()
            flash(f"Failed to connect to the database. -> Error: {str(e)}" "", "danger")
            return redirect('/')
    else:
        return render_template('Customer/customer_login.html')


@app.route('/customer_side_disable_role/<int:CustId>', methods=['POST', 'GET'])
def customer_side_disable_role(CustId):
    if 'Cust_Id' and 'Cust_Phone' and 'Cust_UserName' in session:
        try:
            sel_one_customer = Customers.query.filter_by(cust_id=CustId).first()
            sel_one_customer.isActive = 0
            db.session.commit()
            flash("Record Successfully Disable", "success")
            return redirect(f'/update_customer_profile/{CustId}')
        except Exception as e:
            # If an error occurs during database connection, display an error message
            db.session.rollback()
            flash(f"Failed to connect to the database. -> Error: {str(e)}" "", "danger")
            return redirect('/')
    else:
        return render_template('Customer/customer_login.html')


@app.route('/customer_side_enable_role/<int:CustId>', methods=['POST', 'GET'])
def customer_side_enable_role(CustId):
    if 'Cust_Id' and 'Cust_Phone' and 'Cust_UserName' in session:
        try:
            sel_one_customer = Customers.query.filter_by(cust_id=CustId).first()
            sel_one_customer.isActive = 1
            db.session.commit()
            flash("Record Successfully Enable", "success")
            return redirect(f'/update_customer_profile/{CustId}')
        except Exception as e:
            # If an error occurs during database connection, display an error message
            db.session.rollback()
            flash(f"Failed to connect to the database. -> Error: {str(e)}" "", "danger")
            return redirect('/')
    else:
        return render_template('Customer/customer_login.html')


@app.route('/change_password_customer_side/<int:CustId>', methods=['POST', 'GET'])
def change_password_customer_side(CustId):
    if 'Cust_Id' and 'Cust_Phone' and 'Cust_UserName' in session:
        try:
            # Retrieve form data
            r_password = request.form.get('password')
            r_conform_password = request.form.get('conform_password')

            if r_password == r_conform_password:
                # change_to_hashed_password = generate_password_hash(r_password, "sha256") #old method
                change_to_hashed_password = generate_password_hash(r_password, method='scrypt')  # new method

                update_customers_password = Customers.query.filter_by(cust_id=CustId).first()
                update_customers_password.password = change_to_hashed_password
                db.session.add(update_customers_password)
                db.session.commit()
                flash("Password changed successfully.", "success")
                return redirect(f'/update_customer_profile/{CustId}')
            else:
                flash("Error! Your confirm password is wrong, please try again", "danger")
                return redirect(f'/update_customer_profile/{CustId}')
        except Exception as e:
            # If an error occurs during database connection, display an error message
            db.session.rollback()
            flash(f"Failed to connect to the database. -> Error: {str(e)}" "", "danger")
            return redirect('/')
    else:
        return render_template('Customer/customer_login.html')


@app.route("/cust_logout")
def customer_logout():
    session.pop('Cust_Id', None)
    session.pop('Cust_UserName', None)
    session.pop('Cust_FullName', None)
    session.pop('Cust_Phone', None)
    session.pop('Cust_Photo', None)
    session.pop('cust_RolName', None)
    return redirect('/cust_login')


