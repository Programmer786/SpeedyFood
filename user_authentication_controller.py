from sqlalchemy.orm import joinedload
from app import app
from sqlalchemy.exc import IntegrityError
from sqlalchemy import asc
from database_model import *
# from database_model import db, Users,Rol
from flask import render_template, flash, session, request, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date


@app.route("/admin_dashboard")
def admin_dashboard():
    if 'cnic' and 'user_name' and 'rol_name' in session:
        return render_template('Administrator/admin_dashboard.html')
    else:
        return render_template('Administrator/login.html')


@app.route('/admin_login', methods=['POST', 'GET'])
def admin_login():
    if 'cnic' and 'user_name' and 'rol_name' in session:
        session_rol_name = session['rol_name']
        if session_rol_name == "Administrator":
            return redirect('/admin_dashboard')
        elif session_rol_name == "Manager":
            return redirect('/admin_dashboard')
        else:
            return redirect('/logout')
    else:
        if request.method == 'POST':
            a_cnic = request.form['cnic']
            a_password = request.form['password']
            try:
                # query = "select 1 from Users where cnic=cnic"
                user = Users.query.filter_by(cnic=a_cnic, isActive=1).first()
                # If no record found by this email
                if user is not None:
                    if user.isActive == 1:
                        passwd = user.password
                        # If password decrypt and record do not match with password
                        if check_password_hash(passwd, a_password):  # if passwd == a_password: without encryption
                            session.permanent = True  # <--- makes the permanent session
                            session['user_name'] = user.user_name
                            session['full_name'] = user.full_name
                            session['cnic'] = user.cnic
                            session['email'] = user.email
                            session['ContactNo'] = user.phone
                            session['UserId'] = user.idUsers
                            session['photo'] = user.photo
                            session['rol_name'] = user.rol_name
                            session['restaurant_id'] = user.restaurant_id

                            if user.rol_name == "Administrator":
                                return redirect('/admin_dashboard')
                            elif user.rol_name == "Manager":
                                return redirect('/admin_dashboard')
                            else:
                                return redirect('/logout')
                        else:
                            flash("Error! Invalid Detail, Please try Again!", "danger")
                            return render_template('Administrator/login.html')
                    else:
                        flash("Error! Please Contact to Administrator! Your Account is Looked.", "danger")
                        return render_template('Administrator/login.html')
                else:
                    flash("Error! Invalid Details, Please Contact to Administrator!", "danger")
                    return render_template('Administrator/login.html')
            except Exception as e:
                # If an error occurs during database connection, display error message
                db.session.rollback()
                flash(f"Failed to connect to the database. -> Error: {str(e)}" "", "danger")
                return render_template('Administrator/login.html')
            # except IntegrityError:
            #     db.session.rollback()
            #     flash("Error! Please try again", "danger")
            #     return render_template('Administrator/login.html')
        return render_template('Administrator/login.html')


@app.route('/role', methods=['POST', 'GET'])
def role():
    if 'cnic' and 'user_name' and 'rol_name' in session:
        try:
            # role_with_Cnic_data_retrieve = Users.query.order_by(Users.idUsers).all()
            cell_values = ["Administrator", "Manager"]
            role_with_cnic_data_retrieve = Users.query.filter(
                Users.rol_name.in_(cell_values)
            ).all()

            all_restaurant_data_retrieve = RestaurantNames.query.all()

            if request.method == 'POST':
                try:
                    r_restaurant_sno = request.form.get('get_restaurant_id')
                    r_user_name = request.form.get('user_name')
                    r_full_name = request.form.get('full_name')
                    r_email = request.form.get('email')
                    r_phone = request.form.get('phone')
                    r_cnic = request.form.get('cnic')
                    r_gender = request.form.get('gender')
                    r_password = request.form.get('password')
                    r_conform_password = request.form.get('conform_password')
                    if (r_user_name != "") and (r_full_name != "") and (r_email != "") and (r_phone != "") and (r_cnic != "") and (r_password != "") and (
                            r_conform_password != ""):
                        register_user = Users.query.filter_by(cnic=r_cnic).count()
                        if r_password == r_conform_password:
                            if register_user < 1:
                                # change_to_hashed_password = generate_password_hash(r_password, "sha256") #old method
                                change_to_hashed_password = generate_password_hash(r_password, method='scrypt')  # new method

                                new_entry_register_user = Users(
                                    user_name=r_user_name,
                                    full_name=r_full_name,
                                    email=r_email,
                                    phone=r_phone,
                                    cnic=r_cnic,
                                    gender=r_gender,
                                    rol_name="Manager",
                                    password=change_to_hashed_password,
                                    restaurant_id=r_restaurant_sno,
                                    registrationDate=datetime.now(),
                                    isActive=1
                                )
                                db.session.add(new_entry_register_user)
                                db.session.commit()
                                flash("Successfully Register.", "success")
                                return redirect('/role')
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
                    flash(f"Error: {str(e)}" "", "danger")
                    return redirect('/role')
            else:
                return render_template('Administrator/role.html', all_restaurant_data_retrieve=all_restaurant_data_retrieve, role_with_Cnic_data=role_with_cnic_data_retrieve)
        except Exception as e:
            # If an error occurs during database connection, display error message
            db.session.rollback()
            flash(f"Failed to connect to the database. -> Error: {str(e)}" "", "danger")
            return render_template('Administrator/login.html')
    else:
        return render_template('Administrator/login.html')


@app.route('/disable_role_user/<int:UserId>')
def disable_role_user(UserId):
    if 'cnic' and 'user_name' and 'rol_name' in session:
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
            return render_template('Administrator/login.html')
    else:
        return render_template('Administrator/login.html')


@app.route('/enable_role_user/<int:UserId>')
def enable_role_user(UserId):
    if 'cnic' and 'user_name' and 'rol_name' in session:
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
            return render_template('Administrator/login.html')
    else:
        return render_template('Administrator/login.html')


@app.route('/user_for_update/<int:UserId>', methods=['POST', 'GET'])
def user_for_update(UserId):
    if 'cnic' and 'user_name' and 'rol_name' in session:
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
        return render_template('Administrator/login.html')


@app.route('/change_password/<int:UserId>', methods=['POST', 'GET'])
def change_password(UserId):
    if 'cnic' and 'user_name' and 'rol_name' in session:
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
        return render_template('Administrator/login.html')


@app.route("/error_404")
def error_404():
    if 'cnic' and 'user_name' and 'rol_name' in session:
        return render_template('Administrator/error_404.html')
    else:
        return render_template('Administrator/login.html')


@app.route("/logout")
def logout():
    session.pop('user_name', None)
    session.pop('full_name', None)
    session.pop('cnic', None)
    session.pop('email', None)
    session.pop('ContactNo', None)
    session.pop('UserId', None)
    session.pop('photo', None)
    session.pop('district', None)
    session.pop('rol_name', None)
    session.pop('restaurant_id', None)
    return redirect('/')
