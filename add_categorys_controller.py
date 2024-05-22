from sqlalchemy.orm import joinedload
from app import app
from sqlalchemy.exc import IntegrityError
from sqlalchemy import asc, desc
from database_model import *
# from database_model import db, Users,Rol
from flask import render_template, flash, session, request, redirect, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date


@app.route('/add_district', methods=['POST', 'GET'])
def add_district():
    if 'cnic' and 'user_name' and 'rol_name' in session:
        try:
            # this is for get province
            provinces = Province.query.all()
            # this is for table data retrieve Ascending order
            # district_data_retrieve = District.query.order_by(asc(District.district_name)).all()
            district_data_retrieve = (
                District.query
                .join(Province)
                .options(joinedload(District.province))  # Eager load the associated project
                .all()
            )

            if request.method == 'POST':
                get_province_sno = request.form['get_province']
                get_district_name = request.form['district_name']
                if not get_district_name:
                    flash("Error. Please fill the district name", "danger")
                    return redirect('/add_district')
                try:
                    new_entry_save_by_district = District(
                        district_province_sno=get_province_sno,
                        district_name=get_district_name
                    )
                    db.session.add(new_entry_save_by_district)
                    db.session.commit()
                    flash("Record Successfully Save", "success")
                    return redirect('/add_district')
                except IntegrityError:
                    db.session.rollback()
                    flash("Error. Duplicate data detected. Please do not proceed and try again.", "danger")
                    return redirect('/add_district')  # Add return statement here
            else:
                return render_template('Administrator/add_district.html', provinces=provinces, district_data_retrieve=district_data_retrieve)
        except Exception as e:
            # If an error occurs during database connection, display error message
            db.session.rollback()
            flash(f"Failed to connect to the database. -> Error: {str(e)}" "", "danger")
            return render_template('Administrator/login.html')
    else:
        return render_template('Administrator/login.html')


@app.route('/delete_district/<int:District_Id>')
def delete_district(District_Id):
    if 'cnic' and 'user_name' and 'rol_name' in session:
        try:
            # get specific user district_sno from clerk Table and then check date with District_Id related
            sel_one_district = District.query.filter_by(district_sno=District_Id).first()
            db.session.delete(sel_one_district)
            db.session.commit()
            flash("Record Successfully Deleted", "success")
            return redirect('/add_district')
        except IntegrityError:
            db.session.rollback()
            flash("Error. Please try again", "danger")
            return redirect('/add_district')  # Add return statement here
    else:
        return render_template('Administrator/login.html')


@app.route('/update_district/<int:District_Id>', methods=['GET', 'POST'])
def update_district(District_Id):
    if 'cnic' and 'user_name' and 'rol_name' in session:
        try:
            # this is for get province
            provinces = Province.query.all()
            # district_to_update = District.query.get_or_404(District_Id)

            district_to_update = (
                District.query
                .filter_by(district_sno=District_Id)
                .join(Province)
                .options(joinedload(District.province))  # Eager load the associated project
                .first()  # Use first() instead of all() to get a single object
            )

            if request.method == 'POST':
                new_province_sno = request.form['province_sno']
                new_district_name = request.form['district_name']

                if not new_district_name:
                    flash("Error. Please fill the district name", "danger")
                    return redirect('/add_district')

                try:
                    district_to_update.district_province_sno = new_province_sno
                    district_to_update.district_name = new_district_name
                    db.session.commit()
                    flash("Record Successfully Updated", "success")
                    return redirect('/add_district')
                except IntegrityError:
                    db.session.rollback()
                    flash("Error. Duplicate data detected. Please do not proceed and try again.", "danger")
                    return redirect('/add_district')
            else:
                return redirect('/add_district')
        except Exception as e:
            # If an error occurs during database connection, display error message
            db.session.rollback()
            flash(f"Failed to connect to the database. -> Error: {str(e)}" "", "danger")
            return render_template('Administrator/login.html')
    else:
        return render_template('Administrator/login.html')


@app.route('/add_restaurant_name', methods=['POST', 'GET'])
def add_restaurant_name():
    if 'cnic' and 'user_name' and 'rol_name' in session:
        try:
            # this is for table data retrieve Ascending order
            restaurant_names_data_retrieve = RestaurantNames.query.order_by(asc(RestaurantNames.restaurant_name)).all()
            provinces = Province.query.order_by(asc(Province.province_name)).all()
            if request.method == 'POST':
                get_restaurant_district_sno = request.form.get('restaurant_district_sno')
                get_restaurant_name = request.form['restaurant_name']
                if not get_restaurant_name or not get_restaurant_district_sno:
                    flash("Error. Please make sure to provide both information.", "danger")
                    return redirect('/add_restaurant_name')
                try:
                    new_entry_save_by_restaurant_names = RestaurantNames(
                        restaurant_name=get_restaurant_name,
                        restaurant_district_sno=get_restaurant_district_sno
                    )
                    db.session.add(new_entry_save_by_restaurant_names)
                    db.session.commit()
                    flash("Record Successfully Save", "success")
                    return redirect('/add_restaurant_name')
                except IntegrityError:
                    db.session.rollback()
                    flash("Error. Duplicate data detected. Please do not proceed and try again.", "danger")
                    return redirect('/add_restaurant_name')  # Add return statement here
            else:
                return render_template('Administrator/add_restaurant_name.html', provinces=provinces,
                                       restaurant_names_data_retrieve=restaurant_names_data_retrieve)
        except Exception as e:
            # If an error occurs during database connection, display error message
            db.session.rollback()
            flash(f"Failed to connect to the database. -> Error: {str(e)}" "", "danger")
            return render_template('Administrator/login.html')
    else:
        return render_template('Administrator/login.html')


@app.route('/get-districts')
def get_districts():
    province_sno = request.args.get('province_name', type=str)
    districts = District.query.filter_by(district_province_sno=province_sno).all()
    district_list = []
    for district in districts:
        district_list.append({'id': district.district_sno, 'name': district.district_name})
    return jsonify(district_list)


@app.route('/update_restaurant/<int:Restaurant_Id>', methods=['GET', 'POST'])
def update_restaurant(Restaurant_Id):
    if 'cnic' and 'user_name' and 'rol_name' in session:
        try:
            # get specific user restaurant_id from clerk Table and then check data with Restaurant_Id related
            sel_one_restaurant_name = RestaurantNames.query.filter_by(restaurant_id=Restaurant_Id).first()
            # this is for table data retrieve Ascending order
            restaurant_names_data_retrieve = RestaurantNames.query.order_by(asc(RestaurantNames.restaurant_name)).all()

            if request.method == 'POST':
                get_restaurant_district_sno = request.form.get('restaurant_district_sno')
                get_restaurant_name = request.form['restaurant_name']
                if not get_restaurant_name or not get_restaurant_district_sno:
                    flash("Error. Please make sure to provide both information.", "danger")
                    return redirect('/add_restaurant_name')
                try:
                    sel_one_restaurant_name.restaurant_name = get_restaurant_name
                    sel_one_restaurant_name.restaurant_district_sno = get_restaurant_district_sno
                    db.session.commit()
                    flash("Record Successfully Updated", "success")
                    return redirect('/add_restaurant_name')
                except IntegrityError:
                    db.session.rollback()
                    flash("Error. Duplicate data detected. Please do not proceed and try again.", "danger")
                    return redirect('/add_restaurant_name')  # Add return statement here
            else:
                return render_template('Administrator/add_restaurant_name.html', restaurant_names_data_retrieve=restaurant_names_data_retrieve)
        except Exception as e:
            # If an error occurs during database connection, display error message
            db.session.rollback()
            flash(f"Failed to connect to the database. -> Error: {str(e)}" "", "danger")
            return render_template('Administrator/login.html')
    else:
        return render_template('Administrator/login.html')


@app.route('/delete_restaurant/<int:Restaurant_Id>')
def delete_restaurant(Restaurant_Id):
    if 'cnic' and 'user_name' and 'rol_name' in session:
        try:
            # get specific user restaurant_id from clerk Table and then check data with Restaurant_Id related
            sel_one_restaurant_name = RestaurantNames.query.filter_by(restaurant_id=Restaurant_Id).first()
            db.session.delete(sel_one_restaurant_name)
            db.session.commit()
            flash("Record Successfully Deleted", "success")
            return redirect('/add_restaurant_name')
        except IntegrityError:
            db.session.rollback()
            flash("Error. Please try again", "danger")
            return redirect('/add_restaurant_name')  # Add return statement here
    else:
        return render_template('Administrator/login.html')


@app.route('/add_product_category', methods=['POST', 'GET'])
def add_product_category():
    if 'cnic' and 'user_name' and 'rol_name' in session:
        try:
            product_category_data_retrieve = ProductCategory.query.all()

            if request.method == 'POST':
                get_product_category_name = request.form['product_category_name']
                if not get_product_category_name:
                    flash("Error. Please fill the product category name", "danger")
                    return redirect('/add_product_category')
                try:
                    new_entry_save_by_product_category = ProductCategory(
                        pc_name=get_product_category_name
                    )
                    db.session.add(new_entry_save_by_product_category)
                    db.session.commit()
                    flash("Record Successfully Save", "success")
                    return redirect('/add_product_category')
                except IntegrityError:
                    db.session.rollback()
                    flash("Error. Duplicate data detected. Please do not proceed and try again.", "danger")
                    return redirect('/add_product_category')  # Add return statement here
            else:
                return render_template('Administrator/add_product_category.html', product_category_data_retrieve=product_category_data_retrieve)
        except Exception as e:
            # If an error occurs during database connection, display error message
            db.session.rollback()
            flash(f"Failed to connect to the database. -> Error: {str(e)}" "", "danger")
            return render_template('Administrator/login.html')
    else:
        return render_template('Administrator/login.html')


@app.route('/delete_product_category/<int:Product_Category_Id>')
def delete_product_category(Product_Category_Id):
    if 'cnic' and 'user_name' and 'rol_name' in session:
        try:
            # get specific user district_sno from clerk Table and then check date with District_Id related
            sel_one_product_category = ProductCategory.query.filter_by(pc_id=Product_Category_Id).first()
            db.session.delete(sel_one_product_category)
            db.session.commit()
            flash("Record Successfully Deleted", "success")
            return redirect('/add_product_category')
        except IntegrityError:
            db.session.rollback()
            flash("Error. Please try again", "danger")
            return redirect('/add_product_category')  # Add return statement here
    else:
        return render_template('Administrator/login.html')


@app.route('/update_product_category/<int:Product_Category_Id>', methods=['GET', 'POST'])
def update_product_category(Product_Category_Id):
    if 'cnic' and 'user_name' and 'rol_name' in session:
        try:
            product_category_to_update = (
                ProductCategory.query
                .filter_by(pc_id=Product_Category_Id)
                .first()  # Use first() instead of all() to get a single object
            )

            if request.method == 'POST':
                new_product_category_name = request.form['product_category_name']

                if not new_product_category_name:
                    flash("Error. Please fill the product category name", "danger")
                    return redirect('/add_product_category')

                try:
                    product_category_to_update.pc_name = new_product_category_name
                    db.session.commit()
                    flash("Record Successfully Updated", "success")
                    return redirect('/add_product_category')
                except IntegrityError:
                    db.session.rollback()
                    flash("Error. Duplicate data detected. Please do not proceed and try again.", "danger")
                    return redirect('/add_product_category')
            else:
                return redirect('/add_product_category')
        except Exception as e:
            # If an error occurs during database connection, display error message
            db.session.rollback()
            flash(f"Failed to connect to the database. -> Error: {str(e)}" "", "danger")
            return render_template('Administrator/login.html')
    else:
        return render_template('Administrator/login.html')
