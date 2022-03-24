

import json

import requests

from .logger import logger


def get_mythic_skins_count(connection):
    try:
        res = connection.get('/lol-loot/v1/player-loot/')
        loot_data = res.json()
        mythic_count = len([
            l for l in loot_data
            if l['lootId'].startswith('CHAMPION_SKIN_') and
            l['rarity'] == 'MYTHIC'])
        logger.info(f'Mythic skin shards count: {mythic_count}')
        return mythic_count
    except (json.decoder.JSONDecodeError, requests.exceptions.RequestException):
        return None
