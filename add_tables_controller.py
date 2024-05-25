from sqlalchemy.orm import joinedload

from app import app
from sqlalchemy.exc import IntegrityError
from sqlalchemy import asc, and_
from database_model import *
from flask import render_template, flash, session, request, redirect, url_for, jsonify


@app.route("/pos_table_booking")
def pos_table_booking():
    try:
        # all_tables_retrieve = RestaurantTables.query.all()
        # Example date for filtering
        filter_date_str = session['filter_date']
        # filter_date = datetime.strptime(filter_date_str, '%d-%m-%Y').date()
        filter_date = datetime.strptime(filter_date_str, '%d-%m-%Y').date()
        print(f"filter_date:{filter_date}")

        # Query to retrieve all tables and their reservations for the given date
        all_tables_retrieve = (
            db.session.query(RestaurantTables)
            .outerjoin(TableReservations, and_(
                RestaurantTables.table_id == TableReservations.table_id,
                TableReservations.reservation_date == filter_date
            ))
            .options(joinedload(RestaurantTables.table_reservations).joinedload(TableReservations.time_slots))
            .all()
        )
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


@app.route('/get_available_tables', methods=['GET'])
def get_available_tables():
    try:
        date_str = request.args.get('date')
        filter_date = datetime.strptime(date_str, '%d-%m-%Y').date()
        session.pop('filter_date', None)
        session['filter_date'] = date_str
        print(f" session['filter_date']:{session['filter_date']}")
        # Assuming you have a total tables
        total_tables = RestaurantTables.query.count()
        # Query to get the count of reserved tables on the given date
        reserved_tables_count = TableReservations.query.filter_by(reservation_date=filter_date).count()
        # Calculate available tables
        available_tables = total_tables - reserved_tables_count
        return jsonify({'available_tables': available_tables})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/table_reserve_with_time', methods=['POST'])
def table_reserve_with_time():
    if 'Cust_Id' in session:
        try:
            table_id = request.form['table_id']
            reservation_date = request.form['table_date']
            number_of_chair = request.form['table_chair']

            # Convert the date from DD-MM-YYYY to YYYY-MM-DD
            convert_reservation_date = datetime.strptime(reservation_date, '%d-%m-%Y').date()

            # Check if a reservation with the same table_id and convert_reservation_date exists
            existing_reservation = TableReservations.query.filter_by(
                table_id=table_id,
                reservation_date=convert_reservation_date
            ).first()

            if existing_reservation:
                existing_reservation.table_id = table_id
                existing_reservation.reservation_date = convert_reservation_date
                existing_reservation.number_of_chair = number_of_chair
                existing_reservation.status = 'Reserved'
                db.session.commit()
            else:
                # Create a new reservation
                new_reservation = TableReservations(
                    customer_id=session['Cust_Id'],
                    table_id=table_id,
                    reservation_date=convert_reservation_date,
                    number_of_chair=number_of_chair,
                    status='Reserved'
                )
                db.session.add(new_reservation)
                db.session.commit()

            flash("Reservation Successfully", "success")
            return redirect('/')
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "danger")
            return redirect('/')
    else:
        return render_template('Customer/customer_login.html')
