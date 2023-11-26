import json
import requests
import time
from models import Stores
from store import db
from flask import request, session
from collections import abc
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from decimal import Decimal
import random

# key = Fernet.generate_key()
# fernet = Fernet(key)

def api_distance_request(input):

    if len(input) > 0:
        user_city_id = input.get('wikiDataId')
        user_city_name = input.get('city')
        user_region_code = input.get('regionCode')
        user_region_name = input.get('region')
        stores = db.session.scalars(db.select(Stores).order_by(Stores.id)).all()
        results = list()
        api_response = dict()

        for store in stores:
            store_id = store.id
            store_city = store.store_city
            store_region = store.store_region
            lat = store.lat
            lon = store.lon

            if store_region == user_region_code:
                print("here")
                user_data = {
                    'user_region_code': user_region_code,
                    'user_region_name': user_region_name,
                    'user_city_id': user_city_id
                }
                print(user_data)
                store_data = {
                    'store_region': store_region,
                    'store_city': store_city,
                    'lat': lat,
                    'lon': lon,
                }
                print(store_data)
                url = f"https://wft-geo-db.p.rapidapi.com/v1/geo/places/{user_city_id}/distance"

                querystring = {"distanceUnit": "KM", "toPlaceId": f"{store_id}"}

                headers = {
                    "X-RapidAPI-Key": "b4ad606c18msha453e09d2767c55p17fde4jsn0a11e55d4816",
                    "X-RapidAPI-Host": "wft-geo-db.p.rapidapi.com"
                }

                response = requests.get(url, headers=headers, params=querystring)

                json = response.json()
                distance = json.get('data')
                time.sleep(1)

                store_data.update({'distance': distance})
                api_response.update({'user_data': user_data})
                api_response.update({'store_data': store_data})
                results.append(api_response)

                print("printing results")
                print(results)
                return results
    else:
        return False


def api_city_request(query):
    url = "https://wft-geo-db.p.rapidapi.com/v1/geo/cities"

    querystring = {"types": "CITY", "countryIds": "BR", "namePrefix": "{}".format(query),
                   "languageCode": "pt"}

    headers = {
        "X-RapidAPI-Key": "5765fe14aamsh4d3dfedb2a71ecdp1d75ffjsn941a187fc95c",
        "X-RapidAPI-Host": "wft-geo-db.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    time.sleep(0.6)

    json = response.json()

    data = json.get('data')
    return data


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


def cart_item_to_json (data_bytes):
    for item in data_bytes:
        for key, value in item.items():
            if isinstance(value, Decimal):
                item[key] = float(value)

    data_bytes = json.dumps(session['cart_items']).encode('utf-8')

    return data_bytes

def json_encrypt (data_bytes):
    print(f"cart items before encryption \n{data_bytes}\n")
    key = Fernet.generate_key()
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data_bytes)
    data = {
        'key': key,
        'token': encrypted_data
    }
    print(f"cart items after encryption \n{data['token']}\n")
    return data


def decrypt_json (key, token):
    print(f"cart items before decryption \n{token}\n")
    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(token)
    print(f"cart items after decryption \n{decrypted_data}\n")
    return decrypted_data
