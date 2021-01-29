import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
import re
import geojson

URL = 'https://sushiwok.ru/spb/addresses/'

# Получение данных о названии городов и их id (для соотнесения id города и названия города)
def getId (URL):
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'lxml')

    scripts = soup.findAll('script')

    for index, script in enumerate(scripts):
        script_content = script.string

        if script_content is not None and "window.__INITIAL_DATA__" in script_content:

            match = re.search(r'"cities":\[(.+)region_top":false\}\]', str(script_content))
            string = match.group(0)
            string = string[9:]
            data = json.loads(string)

            updated_cities_data = update_cities(data)
            return updated_cities_data

# Получение данных о магазинах
def extract_points (city):
    
    response = requests.get("https://sushiwok.ru/" + city["city_name"] + "/addresses/")
    soup = BeautifulSoup(response.text, 'lxml')

    scripts = soup.findAll('script')

    for index, script in enumerate(scripts): 
        script_content = script.string

        if script_content is not None and "window.__INITIAL_DATA__" in script_content:

            match = re.search(r'"stores":\[(.+)\]', str(script_content))
            if match == None: 
                break

            string = match.group(0)
            string = string[9:]
            data = json.loads(string)
                
            updated_location_data = update_location(data, city["city_text_name"])
            return updated_location_data


def update_cities (feature_list):
    update_features = []

    for feature in feature_list:

        modified_feature = {
            'city_id': feature['id'],
            'city_name': feature['text_id'],
            'city_text_name': feature['city_name'],
        }
        update_features.append(modified_feature)
        
    return update_features


def update_location (feature_list, city_name):
    modified_feature_list = []

    for feature in feature_list:

        pn = "Пн: " + feature['worktime'][0]['worktime_from'] + " - " + feature['worktime'][0]['worktime_to'] + ", "
        vt = "вт: " + feature['worktime'][1]['worktime_from'] + " - " + feature['worktime'][1]['worktime_to'] + ", "
        sr = "ср: " + feature['worktime'][2]['worktime_from'] + " - " + feature['worktime'][2]['worktime_to'] + ", "
        ch = "чт: " + feature['worktime'][3]['worktime_from'] + " - " + feature['worktime'][3]['worktime_to'] + ", "
        pt = "пт: " + feature['worktime'][4]['worktime_from'] + " - " + feature['worktime'][4]['worktime_to'] + ", "
        sb = "сб: " + feature['worktime'][5]['worktime_from'] + " - " + feature['worktime'][5]['worktime_to'] + ", "
        vs = "вс: " + feature['worktime'][6]['worktime_from'] + " - " + feature['worktime'][6]['worktime_to']
        time = pn + vt + sr + ch + pt + sb + vs
        
        modified_feature = {
            'id': feature['id'],
            'city_name': city_name,
            'address': feature['address'], 
            'latitude': feature['latitude'], 
            'longitude': feature['longitude'], 
            'phone': feature['phone'], 
            'pickup_before_close': feature['pickup_before_close'],
            'has_online_payment': feature['has_online_payment'],
            'store_name_site': feature['store_name_site'],
            'worktime': time,
        }
        
        modified_feature_list.append(modified_feature)

    return modified_feature_list


def to_geojson(data):
    features = []

    for row in data: 
        full_address = ""
        
        if row['city_name'] in row['address']:
            full_address = row['address']
        elif row['city_name'] in row['store_name_site']:
            full_address = row['store_name_site']
        elif "г." in row['address']:
            full_address = row['address']
        elif "г." in row['store_name_site']:
            full_address = row['store_name_site']
        elif row['city_name'] and row['city_name'] not in row['address'] and row['address']:
            full_address = row['city_name'] + ", " + row['address']
        elif row['city_name'] and row['store_name_site']:
            full_address = row['city_name'] + ", " + row['store_name_site']


        feature = {
            "type": "Feature",
            "properties": {
                'id': row['id'],
                'city_name': row['city_name'],
                'address': row['address'], 
                'phone': row['phone'],
                'pickup_before_close': row['pickup_before_close'],
                'has_online_payment': row['has_online_payment'],
                'store_name_site': row['store_name_site'],
                'full_address': full_address,
                'worktime': row['worktime']
            },
            "geometry": {
                "type": "Point",
                "coordinates": [row['longitude'], row['latitude']]
            }
        }

        features.append(feature)

    return features


if __name__ == '__main__':
    features = []
    cities = getId(URL) 
    
    for city in cities:
        points = extract_points(city) 

        if points: 
            features += to_geojson(points)


    featureCollection = {
        "type": "FeatureCollection",
        "features": features
    }

    with open('sushiwok.geojson', 'w', encoding='utf-8') as file:
        geojson.dump(featureCollection, file, ensure_ascii=False, indent=4)

    

