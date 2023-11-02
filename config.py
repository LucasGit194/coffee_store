SECRET_KEY = 'coffee'

SQLALCHEMY_DATABASE_URI = \
    '{SGBD}://{user}:{password}@{host}/{database}'.format(
        SGBD='mysql+mysqlconnector',
        user='lucasgit194',
        password='mYsql;2901',
        host='lucasgit194.mysql.pythonanywhere-services.com',
        database='lucasgit194$default'
    )
