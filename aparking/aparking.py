import requests
import geojson
import pandas as pd

URL_PARKOMATS = "https://old.aparking.kz/admin/guard.php?api=getzoneparkomats&params=number="
URL_TERMINALS ="https://old.aparking.kz/admin/terminals.php"
numbers = ['1001', '1002', '1003', '1004', '1005', '1007', '1008', '1009', '1011', '1012', '1501', '9001', '9002', '9003', '9004', '9005', '9006', '9007', '9008', '9010', '9011']

def get_data (url=None):
    
    if url is None:
        return False
    
    response = requests.get(url)
    return response.json()

def to_geojson(data_frame):

    features = []

    for row in data_frame: 
        
        feature = {
            "type": "Feature",
            "properties": {
                'id': row['id'],
                'adress': row['adress'],
                'workTime': row['workTime'], 
                'price': row['price'],
                'number_zone': row['number_zone'],
            },
            "geometry": {
                "type": "Point",
                "coordinates": [row['placemarkCoords'][1], row['placemarkCoords'][0]]
            }
        }

        features.append(feature)

    return features

def to_geojson_terminals(data_frame):

    features = []

    for row in data_frame: 
        
        feature = {
            "type": "Feature",
            "properties": {
                'terminal_id': row['terminal_id'],
                'organization': row['organization'],
                'city': row['city'], 
                'street': row['street'],
                'house_number': row['house_number'],
            },
            "geometry": {
                "type": "Point",
                "coordinates": [float(row['placemarkCoords'][1]), float(row['placemarkCoords'][0])]
            }
        }

        features.append(feature)

        featureCollection = {
            "type": "FeatureCollection",
            "features": features
        }

    return featureCollection

def save_data(data, name):
    with open(name + '.geojson', 'w', encoding='utf-8') as file:
        geojson.dump(data, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":

    features = []

    # Парковки
    for number in numbers:
        data = get_data(URL_PARKOMATS + number + "/type=admin")
        if data :
            features += to_geojson(data['data'])

    featureCollection = {
       "type": "FeatureCollection",
        "features": features
    }
    save_data(featureCollection, "aparking")

    # Терминалы
    data = get_data(URL_TERMINALS)
    if data:
        data_geo = to_geojson_terminals(data['data'])
        save_data(data_geo, "terminals")

        