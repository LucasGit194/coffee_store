from helpers import *
from flask import render_template, request, redirect, session, flash, url_for
from store import app, db
from models import *
from decimal import Decimal
from cryptography.fernet import Fernet
import json
from sqlalchemy import text

key = Fernet.generate_key()

@app.route('/', methods=['GET'])
def index():
    session['cart_items'] = list()
    # print(session)
    if 'logged' in session:
        username = session['user']
        user = db.session.scalars(db.select(Users).filter_by(username=username)).first()
    else:
        session['user'] = None
        user = session['user']

    if 'cart_items' not in session or session['cart_items'] is None:
        session['cart_items'] = list()

    print(session)
    drinks = db.session.scalars(db.select(Drinks).order_by(Drinks.units_sold.desc())).all()
    top_seller_drink = drinks[0]

    images = db.session.scalars(db.select(Images).order_by(Images.id)).all()

    carousel_payload = carousel()
    c_image_to_message_map = carousel_payload['image_to_message_map']

    main = is_main_page()

    return render_template('list.html', title='DRINKS', drinks=drinks, images=images,
                           carousel=carousel_payload, image_to_message_map=c_image_to_message_map, main=main,
                           top_seller_drink=top_seller_drink, user=user)


@app.route('/login')
def login():
    next = request.args.get('next')
    main = is_main_page()
    return render_template('login.html', next=next, main=main)


@app.route('/user')
def user():
    next = request.args.get('next')
    main = is_main_page()
    return render_template('user.html', next=next, main=main)

@app.route('/create', methods=['POST',])
def create():
    first_name = request.form['first']
    last_name = request.form['last']
    admin = bool(request.form['admin'])
    password = request.form['password']
    username = request.form['user']

    user = Users(username=username, password=password, first_name=first_name, last_name=last_name, admin=admin)
    db.session.add(user)
    db.session.commit()

    return redirect('/')


@app.route('/authenticate', methods=['POST',])
def authenticate():
    password = request.form['password']
    username = request.form['user']

    user = db.session.scalars(db.select(Users).filter_by(password=password)).first()

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
    session.clear()
    flash('Logout was successful!')

    return redirect('/')


@app.route('/cart', methods=['POST'])
def cart():
    print(session['cart_items'])

    if len(session['cart_items']) > 0:
        session['cart_items'].clear()

    drinks = list()
    item_ids = request.form.getlist('item_id')
    item_prices = request.form.getlist('item_price')
    quantities = request.form.getlist('quantity')

    quantities = [int(i) for i in quantities]
    item_ids = [int(i) for i in item_ids]
    item_prices = [Decimal(i) for i in item_prices]

    drinks_query = db.session.scalars(db.select(Drinks).order_by(Drinks.id.desc())).all()
    images = db.session.scalars(db.select(Images).order_by(Images.id.desc())).all()
    users = db.session.scalars(db.select(Users).order_by(Users.id.desc())).all()

    amount_per_drink_type = list()
    total_amount = 0


    for user in users:
        if 'logged' in session:
            if session['user_id'] == user.id:
                user_id = user.id
                order = Orders(users_id=user_id)
                points = user.points
                db.session.add(order)
                db.session.commit()
                break;
        else:
            order = Orders(users_id=None)
            db.session.add(order)
            db.session.commit()
            points = None

    order = db.session.scalars(db.select(Orders).order_by(Orders.id.desc())).first()
    order_id = order.id

    for item_id, item_price, quantity in zip(item_ids, item_prices, quantities):
        if quantity > 0:
            order_item = OrderItems(drinks_id=item_id, drinks_price=item_price, quantity=quantity, order_id=order_id)
            amount_per_drink_type.append(item_price * quantity)

            cart_item = {
                'order_id': order_item.order_id,
                'drinks_id': order_item.drinks_id,
                'drinks_price': order_item.drinks_price,
                'quantity': order_item.quantity
            }

            session['cart_items'].append(cart_item)
    cart_items = session['cart_items']


    for value in amount_per_drink_type:
        total_amount += value

    session['total_amount'] = total_amount

    for drink in drinks_query:
        for item in session['cart_items']:
            if drink.id == item['drinks_id']:
                drinks.append(drink)

    data_bytes = cart_item_to_json(cart_items)
    encription_data = json_encrypt(data_bytes)
    main = is_main_page()

    if 'encription_data' not in session or session['encription_data'] is None:
        session['encription_data'] = encription_data

    return render_template('cart.html', title='YOUR CART', cart_items=cart_items,
                           drinks=drinks, images=images, main=main, total_amount=total_amount, points=points)


@app.route('/checkout', methods=['POST'])
def checkout():

    key = session['encription_data']['key']
    token = session['encription_data']['token']

    order = db.session.scalars(db.select(Orders).order_by(Orders.id.desc())).first()

    forms = request.form.to_dict()

    city = forms['city']
    district = forms['district']
    address = forms['address']
    credit_card = forms['credit']
    cvc = forms['cvc']
    total_amount = session['total_amount']
    total_amount = total_amount.split(".")[0]

    total_amount =  round(int(total_amount))
    cashback = 10 * (total_amount / 100)

    try:
        points_spent = int(forms['discount'])
    except (ValueError, KeyError):
        points_spent = 0

    order_id = order.id


    order_details = OrderDetails(order_id=order_id, city=city, district=district, address=address,
                                 credit_card=credit_card, cvc=cvc, points_spent=points_spent)
    print(order_details)
    if 'logged' in session:
        user_id = session['user_id']
        user = db.session.scalars(db.select(Users).filter_by(id=user_id)).first()
        user.points -= points_spent
        user.points += cashback
        order_details.points_spent = points_spent

    db.session.add(order_details)
    db.session.commit()

    decrypted_json = decrypt_json(key, token)
    decrypted_data = json.loads(decrypted_json.decode('utf-8'))


    for item in decrypted_data:
        print(item)
        order_id = item['order_id']
        drinks_id = item['drinks_id']
        drinks_price = Decimal(item['drinks_price'])
        quantity = item['quantity']

        ordered_item = OrderItems(order_id=order_id, drinks_id=drinks_id, drinks_price=drinks_price, quantity=quantity)
        print(ordered_item)
        db.session.add(ordered_item)
        drink = db.session.scalars(db.select(Drinks).filter_by(id=drinks_id)).first()
        drink.units_sold += quantity
        db.session.commit()

    return redirect('/thanks')


@app.route('/thanks')
def thanks():
    order_details = db.session.scalars(db.select(OrderDetails).order_by(OrderDetails.id.desc())).first()

    city = order_details.city
    district = order_details.district
    address = order_details.address
    main = is_main_page()


    return render_template('thanks.html', title='THANK FOR YOUR ORDER', city=city,
                               district=district, address=address, main=main)


@app.route('/address', methods=['POST', 'GET'])
def address():
    main = is_main_page()
    states = db.session.scalars(db.select(States).order_by(States.region_code))

    return render_template('address.html', title='MAP', main=main, states=states)


@app.route('/results', methods=['GET', 'POST'])
def results():
    if request.method == 'POST':
        city = request.form['city']
        state = request.form['state']

        data = api_city_request(city)
        main = is_main_page()

        filtered_result = filter(lambda entry: entry['regionCode'] == state, data)
        filtered_result = list(filtered_result)

        if len(filtered_result) > 0:
            nearest_store = api_distance_request(filtered_result[0])

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
        else:
            return  render_template('wrong.html', main=main)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if session['logged'] is False or session['admin'] is False:
        return redirect((url_for('/', next=url_for('edit'))))

    drink = db.session.scalars(db.select(Drinks).filter_by(id=id)).first()
    image = db.session.scalars(db.select(Images).filter_by(id=id)).first()
    main = is_main_page()

    return render_template('edit.html', title='Editing a drink', main=main, drink=drink, image=image)


@app.route('/update', methods=['POST'])
def update():
    drink = db.session.scalars(db.select(Drinks).filter_by(id=request.form['item_id'])).first()
    drink.name = request.form['name']
    drink.price = Decimal(request.form['price'])
    drink.description = request.form['description']



    db.session.execute(text("SET FOREIGN_KEY_CHECKS=0"))
    db.session.add(drink)
    db.session.commit()
    db.session.execute(text("SET FOREIGN_KEY_CHECKS=1"))

    return redirect(url_for('index'))