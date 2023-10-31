from api_requests import *
from flask import render_template, request, redirect, session, flash, url_for
from coffee_shop import app, db
from models import *
from decimal import Decimal


def is_main_page():
    url = request.full_path
    root_url = request.root_url
    final_url = url.replace(root_url, "")

    if len(final_url) <= 2:
        return True


def carousel():
    carousel = {}
    c_images = []
    c_messages = []
    c_image_to_message_map = {}

    message1 = "<p>All kinds of coffees<br>and people. Come to us!</p>"
    message2 = "<p>The best Cappuccino in the world!<br>Come and try it!!!</p>"
    message3 = '<p>Not sure if we can serve you?<br><a href="/address">Click here</a> to discover!!!</p>'
    c_messages.append(message1)
    c_messages.append(message2)
    c_messages.append(message3)

    for i in range(1, 4):
        c_images.append("c" + str(i) + ".jpg")
        c_image_to_message_map["c" + str(i) + ".jpg"] = c_messages[i - 1]

    c_messages.append(message1)
    c_messages.append(message2)
    c_messages.append(message3)

    carousel.update({'images': c_images})
    carousel.update({'messages': c_messages})
    carousel.update({'image_to_message_map': c_image_to_message_map})

    return carousel


@app.route('/')
def index():
    session['cart_items'] = list()
    top_seller_drink = Drinks.query.order_by(Drinks.units_sold.desc()).first()
    drinks = Drinks.query.order_by(Drinks.units_sold.desc())

    images = Images.query.order_by(Images.id)
    carousel_payload = carousel()
    c_image_to_message_map = carousel_payload['image_to_message_map']

    main = is_main_page()

    return render_template('list.html', title='DRINKS', drinks=drinks, images=images,
                           carousel=carousel_payload, image_to_message_map=c_image_to_message_map, main=main,
                           top_seller_drink=top_seller_drink)


@app.route('/login')
def login():
    next = request.args.get('next')
    main = is_main_page()
    return render_template('login.html', next=next, main=main)


@app.route('/authenticate', methods=['POST',])
def authenticate():
    session['logged'] = False
    password = request.form['password']
    username = request.form['user']

    user = Users.query.filter_by(password=password).first()

    user_password = user.password
    user_username = user.username
    user_admin = user.admin
    user_id = user.id

    if user_password == password and user_username == username:
        session['user'] = user_username
        session['admin'] = user_admin
        session['logged'] = True
        session['user_id'] = user_id
        flash(session['user'] + ' has successfully logged in')
        return redirect('/')
    else:
        flash('Login failed')
        return redirect('/')


@app.route('/logout')
def logout():
    session['logged'] = False
    session['admin'] = None
    session['user'] = None
    flash('Logout was successful!')
    return redirect('/')


@app.route('/cart', methods=['POST'])
def cart():
    if 'cart_items' not in session or session['cart_items'] is None:
        session['cart_items'] = list()

    drinks = []
    item_ids = request.form.getlist('item_id')
    item_prices = request.form.getlist('item_price')
    quantities = request.form.getlist('quantity')

    quantities = [int(i) for i in quantities]
    item_ids = [int(i) for i in item_ids]
    item_prices = [Decimal(i) for i in item_prices]

    drinks_query = Drinks.query.order_by(Drinks.id)
    images = Images.query.order_by(Images.id)
    users = Users.query.order_by(Users.id)

    amount_per_drink_type = []
    total_amount = 0
    order = Orders()
    for user in users:
        if user.id in session:
            order = Orders(users_id=session['user_id'])
        else:
            order = Orders(users_id=None)

    order_id = order.id

    for item_id, item_price, quantity in zip(item_ids, item_prices, quantities):
        if quantity > 0:
            order_item = OrderItems(drinks_id=item_id, drinks_price=item_price, quantity=quantity, order_id=order_id)
            amount_per_drink_type.append(item_price * quantity)

            drink = Drinks.query.get(item_id)
            drink.units_sold += quantity
            db.session.commit()

            cart_item = {
                'drinks_id': order_item.drinks_id,
                'drinks_price': order_item.drinks_price,
                'quantity': order_item.quantity,
                'order_id': order_item.order_id
            }

            session['cart_items'].append(cart_item)
    cart_items = session['cart_items']
    print(cart_items)


    for value in amount_per_drink_type:
        total_amount += value

    for drink in drinks_query:
        for item in cart_items:
            if drink.id == item['drinks_id']:
                drinks.append(drink)

    db.session.add(order)
    db.session.commit()

    main = is_main_page()

    return render_template('cart.html', title='YOUR CART', cart_items=cart_items,
                           drinks=drinks, images=images, main=main, total_amount=total_amount)


@app.route('/checkout', methods=['POST'])
def checkout():
    if request.method == 'POST':
        city = request.form['city']
        district = request.form['district']
        address = request.form['address']

        main = is_main_page()

        return render_template('thanks.html', title='THANK FOR YOUR ORDER', city=city,
                               district=district, address=address, main=main)


@app.route('/address', methods=['POST', 'GET'])
def address():
    main = is_main_page()
    states = States.query.order_by(States.region_code)

    return render_template('address.html', title='MAP', main=main, states=states)


@app.route('/results', methods=['GET', 'POST'])
def results():
    if request.method == 'POST':
        city = request.form['city']
        state = request.form['state']
        data = api_city_request(city)

        filtered_result = filter(lambda entry: entry['regionCode'] == state, data)
        filtered_result = list(filtered_result)
        nearest_store = api_distance_request(filtered_result[0])

        main = is_main_page()

        if nearest_store:
            show_map = True
            store_data = nearest_store[0]['store_data']
            store_region = store_data['store_region']
            store_city = store_data['store_city']
            lat = store_data['lat']
            lon = store_data['lon']
            distance = store_data['distance']

            return render_template('results.html', store_city=store_city, store_region=store_region,
                                   distance=distance, lat=lat, lon=lon, show_map=show_map,
                                   main=main)
        else:
            show_map = False

            return render_template('results.html', show_map=show_map,
                                   main=main)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if session['logged'] is False or session['admin'] is False:
        return redirect((url_for('/', next=url_for('edit'))))

    drink = Drinks.query.filter_by(id=id).first()
    image = Images.query.filter_by(id=id).first()
    main = is_main_page()

    return render_template('edit.html', title='Editing a drink', main=main, drink=drink, image=image)


@app.route('/update', methods=['POST'])
def update():
    drink = Drinks.query.filter_by(id=request.form['item_id']).first()
    drink.name = request.form['name']
    drink.price = Decimal(request.form['price'])
    drink.description = request.form['description']


    db.session.add(drink)
    db.session.commit()

    return redirect(url_for('index'))