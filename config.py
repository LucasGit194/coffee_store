SECRET_KEY = 'coffee'

SQLALCHEMY_DATABASE_URI = \
    '{SGBD}://{user}:{password}@{host}/{database}'.format(
        SGBD='mysql+mysqlconnector',
        user='root',
        password='mYsql;2901',
        host='localhost',
        database='coffee_shop'
    )
