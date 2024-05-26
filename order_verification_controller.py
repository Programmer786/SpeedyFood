from sqlalchemy.orm import joinedload

from app import app
from sqlalchemy.exc import IntegrityError
from sqlalchemy import asc, and_
from database_model import *
from flask import render_template, flash, session, request, redirect, url_for, jsonify


@app.route('/verify_payment', methods=['POST', 'GET'])
def verify_payment():
    if 'cnic' and 'user_name' and 'rol_name' in session:
        all_order_retrieve = (
            Order.query
            .options(
                joinedload(Order.order_items).joinedload(OrderItem.products),
                joinedload(Order.customers)
            )
            .all()
        )
        return render_template('Administrator/verify_payment.html',
                               all_order_retrieve=all_order_retrieve)
    else:
        return render_template('Administrator/login.html')


@app.route('/payment_verification_success/<int:O_Id>')
def payment_verification_success(O_Id):
    if 'cnic' and 'user_name' and 'rol_name' in session:
        try:
            sel_one_order_verify = Order.query.filter_by(id=O_Id).first()
            sel_one_order_verify.is_verified = 'Approved'
            sel_one_order_verify.isActive = True
            db.session.commit()
            flash("Record Successfully Verified", "success")
            return redirect('/verify_payment')
        except Exception as e:
            # If an error occurs during database connection, display an error message
            db.session.rollback()
            flash(f"Failed to connect to the database. -> Error: {str(e)}" "", "danger")
            return render_template('Administrator/login.html')
    else:
        return render_template('Administrator/login.html')


@app.route('/ready_for_delivery/<int:O_Id>')
def ready_for_delivery(O_Id):
    if 'cnic' and 'user_name' and 'rol_name' in session:
        try:
            sel_one_order_verify = Order.query.filter_by(id=O_Id).first()
            sel_one_order_verify.delivery_status = 'OnTheWay'
            db.session.commit()
            flash("Ready For Delivery, Now Your Order is On The Way", "success")
            return redirect('/verify_payment')
        except Exception as e:
            # If an error occurs during database connection, display an error message
            db.session.rollback()
            flash(f"Failed to connect to the database. -> Error: {str(e)}" "", "danger")
            return render_template('Administrator/login.html')
    else:
        return render_template('Administrator/login.html')
