import requests
import geojson

# Базовый URL получения данных
URL ="https://www.victoria-group.ru/ajax/getmap.php?x1=55.22419925354242&y1=36.56757084374999&x2=56.15504292294658&y2=39.207036175781234&section=300"

# Функция извлечения данных
def get_data (url=None):
    
    # Обработчик ошибки если отсутствует аргумент url
    if url is None:
        return False
    
    # Запрос методом GET
    response = requests.get(URL, verify=False)

    # Если статус ответа 200 возвращаем данные
    if response.status_code is 200:
        print("Data successfully extracted")
        return response.json()
    else:
        print("Error while extracting data")
        return False

def save_data (data=None):
    if data is None:
        return False

    with open('victoria.geojson', 'w', encoding='utf-8') as file:
        geojson.dump(data, file, ensure_ascii=False, indent=4)
        return True

# Скрипт выполнится только при условии если запущен как программа
if __name__ == "__main__":
    data = get_data(url=URL)
    if data:
        result = save_data(data)
        if result:
            print("Data successfully saved")
        else:
            print("Error while saving data")