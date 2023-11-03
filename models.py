from store import db


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(20), primary_key=True, nullable=False)
    password = db.Column(db.String(20), primary_key=True, nullable=False)
    admin = db.Column(db.Boolean(), nullable=False)

    def __repr__(self):
        return '<Username %r>' % self.username


class Drinks(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    units_sold = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<Name %r>' % self.name


class Images(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<Filename %r>' % self.filename


class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def __repr__(self):
        return self.id


class OrderItems(db.Model):
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    drinks_id = db.Column(db.Integer, db.ForeignKey('drinks.id'), primary_key=True)
    drinks_price = db.Column(db.Float(precision=5, asdecimal=True), db.ForeignKey('drinks.price'))
    quantity = db.Column(db.Integer)

    def __repr__(self):
        return '<Item_id %r>' % self.drinks_id


class States(db.Model):
    region_code = db.Column(db.String(2), primary_key=True)
    region_name = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return '<Name %r>' % self.name


class Stores(db.Model):
    id = db.Column(db.String(30), primary_key=True)
    store_city = db.Column(db.String(30), nullable=False)
    store_region = db.Column(db.String(2), nullable=False)
    lat = db.Column(db.DECIMAL(precision=5, scale=8), nullable=False)
    lon = db.Column(db.DECIMAL(precision=5, scale=8), nullable=False)

    def __repr__(self):
        return '<%r Store>' % self.store_city
