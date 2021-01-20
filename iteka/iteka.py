import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
import re
import geojson

URL = 'https://i-teka.kz/nur-sultan/spisokaptek/'

def update_location (feature_list):
    
    for feature in feature_list:
        
        modified_feature = {
            'item_id': feature['item_id'],
            'lat': feature['lat'],
            'lng': feature['lng'],
            'specialIcon': feature['specialIcon'], 
            "block_name": feature['block_name'],
            "block_until": feature['block_until'],
            "block_address": feature['block_address'],
            "block_budnie": feature['block_budnie'],
            "block_sub": feature['block_sub'],
            "block_vos": feature['block_vos'],
            "url": feature[' url'],
            "phones_text": feature['phones_text'],
        }
        
        yield modified_feature


def extract_points (URL):

    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'lxml')

    scripts = soup.findAll('script')

    for index, script in enumerate(scripts): 
        script_content = script.string

        if script_content is not None and "window.createMarker({" in script_content:
            
            data = script_content.replace('window.createMarker(', '').replace('window.addEventListener("load", function(e) {', '').replace('window.setMapView({ lat: 51.1159782, lng: 71.4312592, zoom: 14 });', '')
            data = data.replace(');', ',').replace('   ', '').replace('\n', '').replace("'", '"')
            data = data[0:-5]
            data = "[" + data + "]"
            data = data.replace("<br/>", " ").replace('lat', '"lat"').replace('lng', '"lng"').replace('item_id', '"item_id"').replace('specialIcon', '"specialIcon"').replace('block_name', '"block_name"').replace('block_address', '"block_address"').replace('block_until', '"block_until"').replace('block_budnie', '"block_budnie"').replace('block_sub', '"block_sub"').replace('block_vos', '"block_vos"').replace(' url', '" url"').replace('phones_text', '"phones_text"')

            json_data = json.loads(data)
    
            updated_location_data = update_location(json_data)
            return updated_location_data

def to_geojson(data_frame):
    features = []

    for index, row in data_frame.iterrows(): 
        
        feature = {
            "type": "Feature",
            "properties": {
                'item_id': row['item_id'],
                'block_address': row['block_address'],
                'specialIcon': row['specialIcon'], 
                'block_name': row['block_name'],
                'block_until': row['block_until'],
                'block_address': row['block_address'],
                'block_budnie': row['block_budnie'],
                'block_sub': row['block_sub'],
                'block_vos': row['block_vos'],
                'url': row['url'],
                'phones_text': row['phones_text'],
            },
            "geometry": {
                "type": "Point",
                "coordinates": [row['lng'], row['lat']]
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
    
    with open('iteka.geojson', 'w', encoding='utf-8') as file:
        geojson.dump(geo, file, ensure_ascii=False, indent=4)