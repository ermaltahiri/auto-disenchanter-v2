import json
import time

import requests

from .exceptions import LootRetrieveException
from .inventory import get_inventory_by_type
from .logger import logger
from .loot import get_loot
from .loot import get_loot_by_id


def get_skin_rarity(connection, skin):
    skin_id = f'CHAMPION_SKIN_{skin["itemId"]}'
    loot_data = get_loot_by_id(connection, skin_id)
    if loot_data is None:
        raise LootRetrieveException
    return loot_data.get('rarity')


def get_mythic_skins_count(connection):
    try:
        loot_data = get_loot(connection)
        mythic_loot_skins_count = len([
            l for l in loot_data
            if l['lootId'].startswith('CHAMPION_SKIN_') and
            l['rarity'] == 'MYTHIC'])
        mythic_inventory_skins_count = 0

        inventory_skins = get_inventory_by_type(connection, 'CHAMPION_SKIN')
        for skin in inventory_skins:
            if get_skin_rarity(connection, skin) == 'MYTHIC':
                mythic_inventory_skins_count += 1
        mythic_skins_count = mythic_loot_skins_count + mythic_inventory_skins_count
        logger.info(f'''Mythic skins count: Loot: {mythic_loot_skins_count}, '''
                    f'''Inventory: {mythic_inventory_skins_count}, Total: {mythic_skins_count}''')
        return mythic_skins_count
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
            new_skins = res_json['added']
            if new_skins == []:
                new_skins = res_json['redeemed']
            for skin in new_skins:
                skin = skin.get('playerLoot')
                if skin is None:
                    continue
                desc = skin.get('itemDesc')
                rarity = skin.get('rarity')
                logger.info(f'Loot recieved after rerolling: {desc}, Rarity: {rarity}')
            return True
        except IndexError:
            logger.info(f'Did not receive skin when rerolling: {res_json}')
            return False
    else:
        logger.info(
            f'Error when rerolling skins: Status: {res.status_code}, content: {res.content}')
        return False


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


def reroll_skins(connection, retry_limit=20):
    retries = 0
    while True:
        if retries >= retry_limit:
            logger.info('Retry limit exceeded when rerolling skins.')
            break
        rerollable_skins = get_rerollable_skins(connection)
        if len(rerollable_skins) < 3:
            logger.info('Cannot reroll skins anymore.')
            break
        if not _reroll_skins(connection, rerollable_skins[:3]):
            retries += 1
        time.sleep(1)
