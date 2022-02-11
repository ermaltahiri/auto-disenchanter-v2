import time

from .exceptions import LootRetrieveException
from .logger import logger
from .loot import get_loot
from .recipes import post_recipe


def post_redeem(connection, loot):
    desc = loot['itemDesc']
    count = loot['count']
    logger.info(f'Redeeming: {desc}, Count: {count}')
    connection.post('/lol-loot/v1/player-loot/%s/redeem' % loot['lootName'])


def redeem(connection, value, type, status):
    for _ in range(10):
        try:
            res_json = get_loot(connection)
        except LootRetrieveException:
            time.sleep(1)
            continue
        loot_result = [
            m for m in res_json if
            m['value'] == value and
            m['type'] == type and
            m['redeemableStatus'] == status
        ]
        if loot_result == []:
            return
        for loot in loot_result:
            if value == 0:
                post_redeem(connection, loot)
            else:
                materials = [loot['lootId'], 'CURRENCY_champion']
                post_recipe(connection, 'CHAMPION_upgrade', materials)
    raise LootRetrieveException


def redeem_free(connection):
    logger.info('Redeeming free shards...')
    redeem(connection, 0, 'CHAMPION', 'REDEEMABLE')


def redeem_by_value(connection, value):
    logger.info(f'Redeeming {value} BE shards...')
    redeem(connection, value, 'CHAMPION_RENTAL', 'REDEEMABLE_RENTAL')
