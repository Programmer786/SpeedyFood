from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.functions import now

from app import app
from database_model import *
from flask import render_template, session, request, redirect, jsonify, url_for, flash


@app.route("/")
def customer_dashboard():
    try:
        # Get all product categories and restaurant names
        all_product_category_name = ProductCategory.query.all()
        all_restaurant__name = RestaurantNames.query.all()
        all_tables_retrieve = RestaurantTables.query.all()
        if 'Cust_Id' in session:
            all_order_retrieve = (
                Order.query
                .filter(Order.customer_id == session['Cust_Id'])
                .options(
                    joinedload(Order.order_items).joinedload(OrderItem.products),
                    joinedload(Order.customers)
                )
                .all()
            )

            # Get the current datetime
            now_date = datetime.now()
            # Separate the date and time
            current_date = now_date.date()
            current_time = now_date.time()

            # Query to retrieve reservations based on conditions
            all_tables_reservation_retrieve = (
                TableReservations.query
                .filter(
                    TableReservations.customer_id == session['Cust_Id'],
                    or_(
                        TableReservations.reservation_date > current_date,
                        and_(
                            TableReservations.reservation_date == current_date,
                            TableReservations.time_to > current_time
                        )
                    )
                )
                .options(
                    joinedload(TableReservations.restaurant_tables),
                    joinedload(TableReservations.customers)
                )
                .all()
            )


        else:
            all_order_retrieve = (
                Order.query
                .options(
                    joinedload(Order.order_items).joinedload(OrderItem.products),
                    joinedload(Order.customers)
                )
                .all()
            )
            all_tables_reservation_retrieve = (
                TableReservations.query
                .options(
                    joinedload(TableReservations.restaurant_tables),
                    joinedload(TableReservations.customers)
                )
                .all()
            )

        # Retrieve all products with eager loading of related data
        all_products_data_retrieve = (
            Products.query
            .join(RestaurantNames)
            .options(joinedload(Products.restaurant_names))
            .join(ProductCategory)
            .options(joinedload(Products.product_category))
            .all()
        )
        base_static_url = url_for('static', filename='')

        # Initialize cart items and totals
        cart_items = []
        SubTotal = 0.0
        Taxes = 0.0
        item_count = 0

        if 'Cust_Id' in session:
            cust_id = str(session['Cust_Id'])
            all_cart_items = session.get('cart_items', {})
            cart_items = all_cart_items.get(cust_id, [])

            for item in cart_items:
                price = item['productPrice']
                quantity = item['quantity']
                SubTotal += price * quantity
                item_count += quantity

        Total = SubTotal + Taxes

        print("My Cart:", cart_items)

        return render_template('Customer/pos_customer_order.html',
                               all_restaurant__name=all_restaurant__name,
                               all_product_category_name=all_product_category_name,
                               all_products_data_retrieve=all_products_data_retrieve,
                               base_static_url=base_static_url,
                               cart_items=cart_items,
                               SubTotal=SubTotal,
                               Taxes=Taxes,
                               Total=Total,
                               item_count=item_count,
                               all_tables_retrieve=all_tables_retrieve,
                               all_order_retrieve=all_order_retrieve,
                               all_tables_reservation_retrieve=all_tables_reservation_retrieve)
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "danger")
        return render_template('Customer/pos_customer_order.html')


@app.route('/add_to_cart_in_session/<int:Product_Id>', methods=['GET', 'POST'])
def add_to_cart_in_session(Product_Id):
    if 'Cust_Id' in session:
        cust_id = str(session['Cust_Id'])  # Ensure Cust_Id is treated as a string for session keys
        # Simulate retrieving product data from a database using Product_Id
        product = Products.query.get(Product_Id)

        if product:
            # Construct the product data dictionary
            cartItemData = {
                "productId": int(product.p_id),
                "productName": product.p_name,
                "productPrice": float(product.p_price),
                "quantity": 1,
                "productImageUrl": product.p_image
            }

            # Retrieve existing cart items from session for the specific user
            all_cart_items = session.get('cart_items', {})
            user_cart_items = all_cart_items.get(cust_id, [])

            # Check if the product already exists in the user's cart
            product_exists = False
            for item in user_cart_items:
                if item['productId'] == cartItemData['productId']:
                    # Product already exists, update quantity
                    item['quantity'] += cartItemData['quantity']
                    product_exists = True
                    break

            if not product_exists:
                # Product doesn't exist, append it to the user's cart items
                user_cart_items.append(cartItemData)

            # Update the all_cart_items dictionary with the user's updated cart
            all_cart_items[cust_id] = user_cart_items
            # Update session variable with updated all_cart_items
            session['cart_items'] = all_cart_items

        return redirect('/')
    else:
        return render_template('Customer/customer_login.html')


@app.route('/inc_quantity_in_session/<int:Product_Id>', methods=['GET', 'POST'])
def inc_quantity_in_session(Product_Id):
    if 'Cust_Id' in session:
        cust_id = str(session['Cust_Id'])  # Ensure Cust_Id is treated as a string for session keys
        all_cart_items = session.get('cart_items', {})
        user_cart_items = all_cart_items.get(cust_id, [])

        for item in user_cart_items:
            if item['productId'] == Product_Id:
                item['quantity'] += 1
                break

        all_cart_items[cust_id] = user_cart_items
        session['cart_items'] = all_cart_items
        return redirect('/')
    else:
        return render_template('Customer/customer_login.html')


@app.route('/dec_quantity_in_session/<int:Product_Id>', methods=['GET', 'POST'])
def dec_quantity_in_session(Product_Id):
    if 'Cust_Id' in session:
        cust_id = str(session['Cust_Id'])  # Ensure Cust_Id is treated as a string for session keys
        all_cart_items = session.get('cart_items', {})
        user_cart_items = all_cart_items.get(cust_id, [])

        for item in user_cart_items:
            if item['productId'] == Product_Id:
                if item['quantity'] > 1:
                    item['quantity'] -= 1
                break

        all_cart_items[cust_id] = user_cart_items
        session['cart_items'] = all_cart_items
        return redirect('/')
    else:
        return render_template('Customer/customer_login.html')


@app.route('/remove_from_session_data/<int:Product_Id>', methods=['GET', 'POST'])
def remove_from_session_data(Product_Id):
    if 'Cust_Id' in session:
        cust_id = str(session['Cust_Id'])  # Ensure Cust_Id is treated as a string for session keys
        all_cart_items = session.get('cart_items', {})
        user_cart_items = all_cart_items.get(cust_id, [])

        user_cart_items = [item for item in user_cart_items if item['productId'] != Product_Id]

        all_cart_items[cust_id] = user_cart_items
        session['cart_items'] = all_cart_items
        return redirect('/')
    else:
        return render_template('Customer/customer_login.html')


@app.route('/submit_order', methods=['POST'])
def submit_order():
    if 'Cust_Id' in session and 'Cust_Phone' in session and 'Cust_UserName' in session:
        try:
            # Parse the JSON data
            order_data = request.get_json()
            session_Cust_Id = session['Cust_Id']
            total_price = sum(item['price'] * item['quantity'] for item in order_data)

            # Create a new Order object with the calculated total price
            order = Order(
                customer_id=session_Cust_Id,
                total_price=total_price
            )
            db.session.add(order)
            db.session.commit()

            # Create new OrderItem objects for each item in the order data
            for item in order_data:
                product = Products.query.filter_by(p_id=item['productId']).first()
                if product and product.p_price:
                    order_item = OrderItem(
                        order_id=order.id,
                        product_id=item['productId'],
                        quantity=item['quantity'],
                        price=product.p_price
                    )
                    db.session.add(order_item)

            # Save the order data in the database
            db.session.commit()

            # Clear the cart for the specific user
            cust_id = str(session['Cust_Id'])
            all_cart_items = session.get('cart_items', {})
            if cust_id in all_cart_items:
                del all_cart_items[cust_id]
            session['cart_items'] = all_cart_items

            return jsonify({'success': True})
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500  # Return error message with status code
    else:
        return render_template('Customer/customer_login.html')


# Define a function to generate bot responses based on user input
def generate_response(user_message):
    # Convert the user message to lowercase for case-insensitive matching
    user_message = user_message.lower()

    # Define some simple rules to match user input and generate responses
    if 'menu' in user_message:
        # Fetch all product categories from the database
        all_product_category_name = ProductCategory.query.all()
        # Extract the category names
        categories = [category.pc_name for category in all_product_category_name]
        # Create an HTML ordered list
        categories_list = "<ol>" + "".join(f"<li>{category}</li>" for category in categories) + "</ol>"
        return f"Sure! Here's our menu: {categories_list}"
    elif 'specials' in user_message:
        return "Our specials today are: [insert specials here]"
    elif 'hours' in user_message:
        return "We are open from 11:00 AM to 10:00 PM every day."
    elif 'burger' in user_message:
        return "Our delicious burger is made with 100% Angus beef, served with lettuce, tomato, and fries."
    elif 'pizza' in user_message:
        return "Our pizzas are handcrafted with fresh ingredients and baked to perfection in our wood-fired oven."
    elif 'reservation' in user_message:
        return "Sure! How many people will be dining, and for what time?"
    elif 'order' in user_message:
        return "What would you like to order? Please specify the item and quantity."
    elif 'discount' in user_message:
        return "We currently have a special promotion: Buy one, get one free on all appetizers!"
    elif 'feedback' in user_message:
        return "We appreciate your feedback! Please let us know how we can improve our service."
    else:
        return "I'm sorry, I didn't understand that. How can I assist you?"


@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_message = request.json['message']
    bot_response = generate_response(user_message)
    return jsonify({'response': bot_response})


@app.route('/table_reserve_with_time', methods=['POST'])
def table_reserve_with_time():
    if 'Cust_Id' in session:
        try:
            table_id = request.form['table_id']
            reservation_date = request.form['table_date']
            number_of_chair = request.form['table_chair']
            time_from = request.form['Time_from']
            time_to = request.form['Time_to']

            # Convert the date and time from string to datetime objects
            convert_reservation_date = datetime.strptime(reservation_date, '%Y-%m-%d').date()
            convert_time_from = datetime.strptime(time_from, '%H:%M').time()
            convert_time_to = datetime.strptime(time_to, '%H:%M').time()

            # Check if a reservation with the same table_id and date exists
            existing_reservation = TableReservations.query.filter_by(
                customer_id=session['Cust_Id'],
                table_id=table_id,
                reservation_date=convert_reservation_date,
                status='Reserved'
            ).first()

            if existing_reservation:
                # Update existing reservation
                existing_reservation.number_of_chairs = number_of_chair
                existing_reservation.time_from = convert_time_from
                existing_reservation.time_to = convert_time_to
                existing_reservation.status = 'Reserved'
                db.session.commit()
                flash("Reservation Timing Update Successfully", "success")
            else:
                # Create a new reservation
                new_reservation = TableReservations(
                    customer_id=session['Cust_Id'],
                    table_id=table_id,
                    reservation_date=convert_reservation_date,
                    number_of_chairs=number_of_chair,
                    time_from=convert_time_from,
                    time_to=convert_time_to,
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


@app.route('/submit_transaction/<int:OrderId>', methods=['GET', 'POST'])
def submit_transaction(OrderId):
    if 'Cust_Id' in session:
        try:
            one_Order = Order.query.get_or_404(OrderId)
            if request.method == 'POST':
                get_transaction_no = request.form.get('transaction_no')
                # Check if required fields are not empty
                if not get_transaction_no:
                    flash("Error. Please fill all the required fields", "danger")
                    return redirect('/')

                one_Order.transaction_no = get_transaction_no
                one_Order.is_verified = 'Verification'
                db.session.commit()
                flash(f"Total Price:{one_Order.total_price} :- Transaction Number Successfully Submitted, Now Waiting For Conformation. Thank You!", "success")
                return redirect('/')
            else:
                return redirect('/')
        except Exception as e:
            db.session.rollback()
            flash(f"Failed to connect to the database. -> Error: {str(e)}", "danger")
            return redirect('/')
    else:
        return render_template('Customer/customer_login.html')


@app.route('/submit_delivery_address', methods=['POST'])
def submit_delivery_address():
    if 'Cust_Id' in session:
        try:
            # Get the order ID from the form data
            order_id = request.form.get('order_id')
            if not order_id:
                flash("Error: Order ID not found", "danger")
                return redirect('/')

            one_Order = Order.query.get_or_404(order_id)

            if request.method == 'POST':
                get_cust_drop_address = request.form.get('cust_drop_address')
                if not get_cust_drop_address:
                    flash("Error. Please fill all the required fields", "danger")
                    return redirect('/')

                one_Order.cust_drop_address = get_cust_drop_address
                db.session.commit()
                flash("Address Successfully Submitted. Now Waiting For Delivery. Thank You!", "success")
                return redirect('/')
            else:
                return redirect('/')
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "danger")
            return redirect('/')
    else:
        return render_template('Customer/customer_login.html')


@app.route('/delivery_received/<int:OrderId>')
def delivery_received(OrderId):
    if 'Cust_Id' in session:
        try:
            sel_one_delivery = Order.query.get_or_404(OrderId)
            sel_one_delivery.delivery_status = 'Deliver'
            db.session.commit()
            flash("Record Successfully Received", "success")
            return redirect('/')
        except Exception as e:
            # If an error occurs during database connection, display an error message
            db.session.rollback()
            flash(f"Error: {str(e)}" "", "danger")
            return render_template('Customer/customer_login.html')
    else:
        return render_template('Customer/customer_login.html')
