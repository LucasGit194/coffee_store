SECRET_KEY = 'random'

SQLALCHEMY_DATABASE_URI = \
    '{SGBD}://{user}:{password}@{host}/{database}'.format(
        SGBD='mysql+mysqlconnector',
        user='user',
        password='password',
        host='host',
        database='database'
    )
