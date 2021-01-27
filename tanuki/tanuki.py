import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
import re
import geojson

URL = 'https://www.tanuki.ru/restaurants/'

def update_location (feature_list):

    for key in feature_list:

        modified_feature = {
            'id': feature_list[key]['id'],
            'address': feature_list[key]['address'],
            'timework': feature_list[key]['timework'],
            'metro': feature_list[key]['metro'], 
            "phone": feature_list[key]['phone'],
            "latitude": feature_list[key]['latitude'],
            "longitude": feature_list[key]['longitude'],
            "sitPlaces": feature_list[key]['sitPlaces'],
            "share": feature_list[key]['share'],
            }

        yield modified_feature

def extract_points (URL):

    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'lxml')

    scripts = soup.findAll('script')

    for index, script in enumerate(scripts): 
        script_content = script.string

        if script_content is not None and " __NEXT_DATA__ = {" in script_content:
            match = re.search(r'"restaurants":\{(.+)"tags":""\}\}', str(script_content))
            data = match.group(0).replace('"restaurants":{"isPending":false,"isRejected":false,"isFulfilled":true,"error":null,"data":', "")                
            
            json_data = json.loads(data)
    
            updated_location_data = update_location(json_data)
            return updated_location_data


def to_geojson(data_frame):
    features = []

    for index, row in data_frame.iterrows(): 
        
        feature = {
            "type": "Feature",
            "properties": {
                'id': row['id'],
                'address': row['address'],
                'timework': row['timework'], 
                'metro': row['metro'],
                'phone': row['phone'],
                'sitPlaces': row['sitPlaces'],
                'share': row['share'],
            },
            "geometry": {
                "type": "Point",
                "coordinates": [float(row['longitude']), float(row['latitude'])]
            }
        }

        features.append(feature)
    
    featureCollection = {
       "type": "FeatureCollection",
        "features": features
    }

    return featureCollection

if __name__ == '__main__':
    
    points = pd.DataFrame( extract_points(URL) )
    geo = to_geojson(points)    
    with open('tanuki.geojson', 'w', encoding='utf-8') as file:
        geojson.dump(geo, file, ensure_ascii=False, indent=4)