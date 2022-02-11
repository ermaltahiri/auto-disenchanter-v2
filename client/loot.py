from .exceptions import LootRetrieveException
from .logger import logger


def get_loot(connection):
    res = connection.get('/lol-loot/v1/player-loot')
    res_json = res.json()
    if res_json == []:
        logger.info('Can not retrieve loot...')
        raise LootRetrieveException
    return res_json


def get_loot_count(loot_json, lood_id):
    loot = [l for l in loot_json if l['lootId'] == lood_id]
    if loot == []:
        return 0
    return loot[0]['count']


def get_key_fragment_count(loot_json):
    return get_loot_count(loot_json, 'MATERIAL_key_fragment')


def get_key_count(loot_json):
    return get_loot_count(loot_json, 'MATERIAL_key')


def get_generic_chest_count(loot_json):
    return get_loot_count(loot_json, 'CHEST_generic')


def get_champion_mastery_chest_count(loot_json):
    return get_loot_count(loot_json, 'CHEST_champion_mastery')


def get_masterwork_chest_count(loot_json):
    return get_loot_count(loot_json, 'CHEST_224')
