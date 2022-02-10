import time

import requests

from .logger import logger


def change_icon(connection, icon_id):
    while get_icon(connection) != icon_id:
        try:
            data = {'profileIconId': icon_id}
            logger.info('Changing summoner icon...')
            connection.put('/lol-summoner/v1/current-summoner/icon', json=data)
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)


def get_icon(connection):
    try:
        res = connection.get('/lol-summoner/v1/current-summoner')
        res_json = res.json()
        return res_json['profileIconId']
    except requests.exceptions.RequestException:
        return -1
