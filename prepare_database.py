import mysql.connector
from mysql.connector import errorcode

print("Conecting...")
try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='mYsql;2901'
    )
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("There is something wrong with username or password")
    else:
        print(err)

cursor = conn.cursor()
cursor.execute("DROP DATABASE IF EXISTS coffee_shop;")
cursor.execute("CREATE DATABASE coffee_shop;")
cursor.execute("USE coffee_shop;")

#creating tables
TABLES = {}
TABLES['Users'] = ('''
        CREATE TABLE users (
        id INT NOT NULL AUTO_INCREMENT,
        first_name VARCHAR(20) NOT NULL,
        last_name VARCHAR(20) NOT NULL,
        username VARCHAR(20) NOT NULL,
        password VARCHAR(20) NOT NULL,
        admin TINYINT(1) NOT NULL,
        points INT NOT NULL DEFAULT 0,
        PRIMARY KEY(id, username, password)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;''')
TABLES['Drinks'] = ('''
        CREATE TABLE drinks (
        id INT NOT NULL AUTO_INCREMENT,
        name VARCHAR(20) NOT NULL,
        price DECIMAL(5,2) NOT NULL,
        units_sold INT(20) NOT NULL DEFAULT 0,
        intensity INT NOT NULL,
        description VARCHAR(255) NOT NULL,
        INDEX (id, price),
        PRIMARY KEY(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;''')
TABLES['Images'] = ('''
        CREATE TABLE images (
        id INT NOT NULL,
        filename VARCHAR(255) NOT NULL,
        PRIMARY KEY (id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;''')
TABLES['Orders'] = ('''
        CREATE TABLE orders (
        id INT NOT NULL AUTO_INCREMENT,
        users_id INT,
        PRIMARY KEY (id),
        FOREIGN KEY (users_id) REFERENCES users(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;''')
TABLES['Order_items'] = ('''
        CREATE TABLE order_items (
        id INT AUTO_INCREMENT,
        order_id INT NOT NULL,
        drinks_id INT NOT NULL,
        drinks_price DECIMAL(5, 2) NOT NULL,
        quantity INT NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY (order_id) REFERENCES orders(id),
        FOREIGN KEY (drinks_id, drinks_price) REFERENCES drinks(id, price)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;''')
TABLES['Order_details'] = ('''
        CREATE TABLE order_details (
        id INT AUTO_INCREMENT,
        order_id INT NOT NULL,
        city VARCHAR(20) NOT NULL,
        district VARCHAR (255) NOT NULL,
        address VARCHAR(255) NOT NULL,
        credit_card VARCHAR(19) NOT NULL,
        cvc INT NOT NULL,
        points_spent INT,
        PRIMARY KEY (id),
        FOREIGN KEY (order_id) REFERENCES orders(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;''')
TABLES['States'] = ('''
        CREATE TABLE states (
        region_code VARCHAR(2) NOT NULL PRIMARY KEY,
        region_name VARCHAR(30) NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;''')
TABLES['Stores'] = ('''
        CREATE TABLE stores (
        id VARCHAR(20) NOT NULL PRIMARY KEY,
        store_city VARCHAR(30) NOT NULL,
        store_region VARCHAR(30) NOT NULL,
        lat DECIMAL(8, 6) NOT NULL,
        lon DECIMAL(8, 6) NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;''')

for table_name in TABLES:
    sql_table = TABLES[table_name]
    try:
        print("Creating table {}:".format(sql_table), end='\n ')
        cursor.execute(sql_table)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print('Already exists!')
        else:
            print(err.msg)
    else:
        print("OK!")

#inserting users
sql_users = 'INSERT INTO users (first_name, last_name, username, password, admin, points) VALUES (%s, %s, %s, %s, %s, %s)'
users = [
    ("Lucas", "Souza", "lucasouza", "pass1", "1", "1000"),
    ("João", "Silva", "joaosilva", "pass2", "0", "10000")
]
cursor.executemany(sql_users, users)

cursor.execute('select * from coffee_shop.users')
print('---------------- Users: ----------------')
for user in cursor.fetchall():
    print(user[1] + " " + user[2])
print("\n")

#inserting drinks and images

sql_drinks = 'INSERT INTO drinks (name, price, units_sold, intensity, description) VALUES (%s, %s, %s, %s, %s)'
sql_images = 'INSERT INTO images (id, filename) VALUES (%s, %s)'
drinks = [
    ("EXPRESSO", "5.00", "100", "4", "1 Shot of Expresso"),
    ("AMERICANO", "5.00", "100", "3", "Hot Water + 1 Shot of Expresso"),
    ("CAPPUCCINO", "10.00", "201", "3", "Steamed Milk + 1 Shot of Expresso"),
    ("LATTE", "15.00", "200", "2", "Milk foam + Steamed Milk + 1 Shot of Expresso"),
    ("ICED COFFEE", "15.00", "200", "2", "Ice + Milk + 1 Shot of Expresso"),
    ("BLACK EYE", "10.00", "50", "5", "Brewed Coffee + 1 Shot of Expresso"),
    ("FLAT WHITE", "10.00", "150", "3", "Steamed Milk + Double Expresso"),
    ("FRAPPE", "20.00", "150", "1", "Ice Cream + Steamed Milk + 1 Shot of Expresso"),
    ("IRISH COFFEE", "25.00", "50", "5", "Whipped Cream + Whiskey + 1 Shot of Expresso")
]
images = []

cursor.executemany(sql_drinks, drinks)

cursor.execute('select * from coffee_shop.drinks')
print('---------------- Drinks: ----------------')
for drink in cursor.fetchall():
    print(drink[1])
    pk = drink[0]
    filename = str(pk) + ".png"
    images.append((pk, filename))
print("\n")

cursor.executemany(sql_images, images)
cursor.execute('select * from coffee_shop.images')
print('---------------- Images: ----------------')
for image in cursor.fetchall():
    print(image[1])
print("\n")

#inserting states and stores

sql_states = 'INSERT INTO states (region_code, region_name) VALUES (%s, %s)'
states = [
    ("AC", "Acre"),
    ("AL", "Alagoas"),
    ("AP", "Amapá"),
    ("AM", "Amazonas"),
    ("BA", "Bahia"),
    ("CE", "Ceará"),
    ("ES", "Espírito Santo"),
    ("GO", "Goiás"),
    ("MA", "Maranhão"),
    ("MT", "Mato Grosso"),
    ("MS", "Mato Grosso do Sul"),
    ("MG", "Minas Gerais"),
    ("PA", "Pará"),
    ("PB", "Paraíba"),
    ("PR", "Paraná"),
    ("PE", "Pernambuco"),
    ("PI", "Piauí"),
    ("RJ", "Rio de Janeiro"),
    ("RN", "Rio Grande do Norte"),
    ("RS", "Rio Grande do Sul"),
    ("RO", "Rondônia"),
    ("RR", "Roraima"),
    ("SC", "Santa Catarina"),
    ("SP", "São Paulo"),
    ("SE", "Sergipe"),
    ("TO", "Tocantins")
]


cursor.executemany(sql_states, states)
cursor.execute('select * from coffee_shop.states')
print('---------------- States: ----------------')
for state in cursor.fetchall():
    print(state[1])
print("\n")

sql_stores = 'INSERT INTO stores (id, store_city, store_region, lat, lon) VALUES (%s, %s, %s, %s, %s)'
stores = [
    ("Q167436", "João Pessoa", "PB", "-7.144081", "-34.818773"),
    ("Q22061296", "Recife", "PE", "-7.952330", "-34.925290"),
    ("Q131620", "Natal", "RN", "-5.719577", "-35.262229")
]

cursor.executemany(sql_stores, stores)
cursor.execute('select * from coffee_shop.stores')
print('---------------- Stores: ----------------')
for store in cursor.fetchall():
    print(str(store[0]) + " - " + store[1])

#commiting the changes

conn.commit()

cursor.close()
conn.close()
