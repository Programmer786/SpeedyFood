from app import app
from sqlalchemy.exc import IntegrityError
from sqlalchemy import asc
from database_model import *
from flask import render_template, flash, session, request, redirect


@app.route('/add_table', methods=['POST', 'GET'])
def add_table():
    if 'cnic' and 'user_name' and 'rol_name' in session:
        try:
            # this is for table data retrieve Ascending order
            table_data_retrieve = RestaurantTables.query.order_by(asc(RestaurantTables.table_name)).all()

            if request.method == 'POST':
                get_table_name = request.form['table_name'].upper()
                if not get_table_name:
                    flash("Error. Please fill the table name", "danger")
                    return redirect('/add_table')
                try:
                    new_entry_table = RestaurantTables(
                        table_name=get_table_name
                    )
                    db.session.add(new_entry_table)
                    db.session.commit()
                    flash("Record Successfully Save", "success")
                    return redirect('/add_table')
                except IntegrityError:
                    db.session.rollback()
                    flash("Error. Duplicate data detected. Please do not proceed and try again.", "danger")
                    return redirect('/add_table')  # Add a return statement here
            else:
                return render_template('Administrator/add_table.html', table_data_retrieve=table_data_retrieve)
        except Exception as e:
            # If an error occurs during database connection, display an error message
            db.session.rollback()
            flash(f"Error: {str(e)}", "danger")
            return redirect('/')  # Add a return Dashboard here
    else:
        return render_template('Administrator/login.html')


@app.route('/delete_table/<int:Table_Id>')
def delete_table(Table_Id):
    if 'cnic' and 'user_name' and 'rol_name' in session:
        try:
            sel_one_table = RestaurantTables.query.filter_by(table_id=Table_Id).first()
            db.session.delete(sel_one_table)
            db.session.commit()
            flash("Record Successfully Deleted", "success")
            return redirect('/add_table')
        except IntegrityError:
            db.session.rollback()
            flash("Error. Please try again", "danger")
            return redirect('/add_table')
    else:
        return render_template('Administrator/login.html')


@app.route('/update_table/<int:Table_Id>', methods=['GET', 'POST'])
def update_table(Table_Id):
    if 'cnic' and 'user_name' and 'rol_name' in session:
        try:
            table_to_update = RestaurantTables.query.filter_by(table_id=Table_Id).first()

            if request.method == 'POST':
                get_table_name = request.form['table_name'].upper()

                if not get_table_name:
                    flash("Error. Please fill the table name", "danger")
                    return redirect('/add_table')

                try:
                    table_to_update.table_name = get_table_name
                    db.session.commit()
                    flash("Record Successfully Updated", "success")
                    return redirect('/add_table')
                except IntegrityError:
                    db.session.rollback()
                    flash("Error. Duplicate data detected. Please do not proceed and try again.", "danger")
                    return redirect('/add_table')
            else:
                return redirect('/add_table')
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "danger")
            return redirect('/add_table')
    else:
        return render_template('Administrator/login.html')
