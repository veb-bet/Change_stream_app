import json
import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionError
from concurrent.futures import ThreadPoolExecutor

# Функция для отслеживания изменений в коллекции
def watch_changes(service_name, collection_name, uri, database):
    try:
        client = MongoClient(uri)
        db = client[database]
        collection = db[collection_name]
        
        # Создаем Change Stream для коллекции
        change_stream = collection.watch()
        
        print(f"[{service_name}] Отслеживаем изменения в коллекции: {collection_name}")
        
        for change in change_stream:
            print(f"[{service_name}] Обнаружено изменение в {collection_name}: {change}")
    
    except ConnectionError:
        print(f"[{service_name}] Ошибка подключения к MongoDB.")
    except Exception as e:
        print(f"[{service_name}] Ошибка при отслеживании изменений: {e}")

# Загрузка конфигурации из JSON файла
def load_config(config_path='config.json'):
    with open(config_path, 'r') as f:
        return json.load(f)

# Основная функция
def main():
    # Загружаем конфигурацию
    config = load_config()
    mongodb_uri = config["mongodb"]["uri"]
    database = config["mongodb"]["database"]
    
    # Инициализируем пул потоков для параллельной работы
    with ThreadPoolExecutor() as executor:
        # Для каждого сервиса создаем поток для каждого его коллекции
        for service in config["services"]:
            service_name = service["name"]
            collections = service["collections"]
            for collection in collections:
                executor.submit(watch_changes, service_name, collection, mongodb_uri, database)

if __name__ == "__main__":
    main()
