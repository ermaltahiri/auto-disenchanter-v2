import json

import requests

from .logger import logger
from .loot import get_loot


def get_mythic_skins_count(connection):
    try:
        loot_data = get_loot(connection)
        mythic_count = len([
            l for l in loot_data
            if l['lootId'].startswith('CHAMPION_SKIN_') and
            l['rarity'] == 'MYTHIC'])
        logger.info(f'Mythic skin shards count: {mythic_count}')
        return mythic_count
    except (json.decoder.JSONDecodeError, requests.exceptions.RequestException):
        return None


def _reroll_skins(connection, skins, repeat=1):
    logger.info(
        f'''Rerolling using skins: {', '.join([f'{s["itemDesc"]}({s["disenchantValue"]} OE, {s["rarity"]})' for s in skins])}...''')
    skinIds = [s['lootId'] for s in skins]
    url = f'/lol-loot/v1/recipes/SKIN_reroll/craft?repeat={repeat}'
    res = connection.post(url, json=skinIds)
    if res.ok:
        res_json = res.json()
        try:
            new_skin = res_json['added'][0]['playerLoot']
            logger.info(
                f'Skin received after rerolling: {new_skin.get("itemDesc")}, Rarity: {new_skin.get("rarity")}')
        except IndexError:
            pass


def get_rerollable_skins(connection):
    try:
        loot_data = get_loot(connection)
        rerollable_skins = [l for l in loot_data
                            if l['lootId'].startswith('CHAMPION_SKIN_') and
                            l['rarity'] not in ['MYTHIC', 'ULTIMATE', 'LEGENDARY']]
        logger.info(f'Rerollable skin count: {len(rerollable_skins)}')
        rerollable_skins.sort(key=lambda x: x['disenchantValue'])
        return rerollable_skins
    except (json.decoder.JSONDecodeError, requests.exceptions.RequestException):
        return None


def reroll_skins(connection):
    while True:
        rerollable_skins = get_rerollable_skins(connection)
        if len(rerollable_skins) < 3:
            logger.info('Cannot reroll skins anymore.')
            break
        _reroll_skins(connection, rerollable_skins[:3])
