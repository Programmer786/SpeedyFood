from app import app
from sqlalchemy.exc import IntegrityError
from sqlalchemy import asc
from database_model import *
from flask import render_template, flash, session, request, redirect, url_for, jsonify


@app.route("/pos_table_booking")
def pos_table_booking():
    try:
        all_tables_retrieve = RestaurantTables.query.all()
        tables_count = RestaurantTables.query.count()

        base_static_url = url_for('static', filename='')

        return render_template('Customer/pos_table_booking.html',
                               base_static_url=base_static_url,
                               tables_count=tables_count,
                               all_tables_retrieve=all_tables_retrieve)
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "danger")
        return render_template('Customer/pos_customer_order.html')


@app.route('/add_table', methods=['POST', 'GET'])
def add_table():
    if 'cnic' and 'user_name' and 'rol_name' in session:
        try:
            # this is for table data retrieve Ascending order
            table_data_retrieve = RestaurantTables.query.order_by(asc(RestaurantTables.table_name)).all()

            if request.method == 'POST':
                get_table_name = request.form['table_name'].upper()
                get_table_pax = request.form['table_pax']
                if not get_table_name:
                    flash("Error. Please fill the table name", "danger")
                    return redirect('/add_table')
                try:
                    new_entry_table = RestaurantTables(
                        table_name=get_table_name,
                        table_pax=get_table_pax
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
                get_table_pax = request.form['table_pax']

                if not get_table_name:
                    flash("Error. Please fill the table name", "danger")
                    return redirect('/add_table')

                try:
                    table_to_update.table_name = get_table_name
                    table_to_update.table_pax = get_table_pax
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


@app.route('/api/time_slots')
def get_time_slots():
    table_id = request.args.get('table_id')
    reservation_date = request.args.get('reservation_date')

    # Fetch all time slots
    time_slots = TimeSlots.query.all()

    # Fetch reservations for the given table and date
    reservations = TableReservations.query.filter_by(table_id=table_id, reservation_date=reservation_date).all()

    # Mark the time slots with their reservation status
    available_slots = []
    for slot in time_slots:
        status = 'Available'
        for reservation in reservations:
            if reservation.time_slot_id == slot.time_slot_id:
                status = f'Reserved by {reservation.customers.cust_full_name}'
                break
        available_slots.append({
            'time_slot_id': slot.time_slot_id,
            'time': slot.slot_time.strftime('%I:%M %p'),
            'status': status
        })

    return jsonify({'time_slots': available_slots})


@app.route('/api/book_reservation', methods=['POST'])
def book_reservation():
    data = request.get_json()

    new_reservation = TableReservations(
        customer_id=data['customer_id'],
        table_id=data['table_id'],
        reservation_date=data['reservation_date'],
        number_of_guests=data['number_of_guests'],
        special_requests=data.get('special_requests', '')
    )

    try:
        db.session.add(new_reservation)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

