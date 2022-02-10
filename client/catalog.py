import json
import time

from .exceptions import LogoutNeededException


def catalog(connection, item_type):
    for _ in range(10):
        url = f'/lol-store/v1/catalog?inventoryType=["{item_type}"]'
        response = connection.get(url)
        if response.ok:
            response = response.json()
            if response != []:
                with open('catalog.json', 'w') as fp:
                    json.dump(response, fp)
                return response
        catalog_local = catalog_from_file()
        if catalog_local != []:
            return catalog_local
        time.sleep(1)
    raise LogoutNeededException


def catalog_from_file():
    try:
        with open('catalog.json') as fp:
            return json.load(fp)
    except (OSError, json.decoder.JSONDecodeError):
        return []
