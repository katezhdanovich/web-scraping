import requests
import geojson
import json

URL ="https://www.victoria-group.ru/ajax/getmap.php?x1=55.22419925354242&y1=36.56757084374999&x2=56.15504292294658&y2=39.207036175781234&section=300"

def get_data (url=None):
    
    if url is None:
        return False
    response = requests.get(URL, verify=False)
    if response.status_code is 200:
        print("Data successfully extracted")
        return response.json()
    else:
        print("Error while extracting data")
        return False

def save_data (data=None):
    if data is None:
        return False

    data_geo = to_geojson(data)

    with open('victoria.geojson', 'w', encoding='utf-8') as file:
        geojson.dump(data_geo, file, ensure_ascii=False, indent=4)
        return True

def to_geojson(data_frame):
    features = []

    for row in data_frame: 
        
        feature = {
            "type": "Feature",
            "properties": {
                'name': row['name'],
                'address': row['address'],
                'id': row['id'], 
                'distance': row['distance'],
                'title': row['title'],
                'adr': row['adr'],
                'work_time': row['work_time'],
            },
            "geometry": {
                "type": "Point",
                "coordinates": [row['lon'], row['lat']]
            }
        }

        features.append(feature)
    
    featureCollection = {
       "type": "FeatureCollection",
        "features": features
    }

    return featureCollection

if __name__ == "__main__":
    data = get_data(url=URL)
    if data:
        result = save_data(data)
        if result:
            print("Data successfully saved")
        else:
            print("Error while saving data")