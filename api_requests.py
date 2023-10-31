import requests
import time
from models import Stores


def api_distance_request(input):

    if len(input) > 0:
        user_city_id = input.get('wikiDataId')
        user_region_code = input.get('regionCode')
        user_region_name = input.get('region')

        stores = Stores.query.order_by(Stores.id)

        results = []
        api_response = {}
        for store in stores:
            store_id = store.id
            store_city = store.store_city
            store_region = store.store_region
            lat = store.lat
            lon = store.lon

            print(store_region)
            print(user_region_code)

            if store_region == user_region_code:

                user_data = {
                    'user_region_code': user_region_code,
                    'user_region_name': user_region_name,
                    'user_city_id': user_city_id
                }

                store_data = {
                    'store_region': store_region,
                    'store_city': store_city,
                    'lat': lat,
                    'lon': lon,
                }

                url = f"https://wft-geo-db.p.rapidapi.com/v1/geo/places/{user_city_id}/distance"
                print(store_id)
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

                print("printing the output of the api")
                print(results)
                return results
            else:
                return False
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
