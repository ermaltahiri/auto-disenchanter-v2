import time

from logger import logger

from .exceptions import LootRetrieveException
from .loot import get_loot


def disenchant(connection, retry_limit=10):
    logger.info('Disenchanting all champion shards...')
    for _ in range(retry_limit):
        try:
            res_json = get_loot(logger, connection)
        except LootRetrieveException:
            time.sleep(1)
            continue
        loot_result = [m for m in res_json if m['displayCategories'] == 'CHAMPION']
        if loot_result == []:
            return
        for loot in loot_result:
            desc = loot['itemDesc']
            count = loot['count']
            loot_type = loot['type']
            logger.info(f'Dienchanting: {desc}, Count: {count}')
            url = f'/lol-loot/v1/recipes/{loot_type}_disenchant/craft?repeat={count}'
            data = [loot['lootName']]
            connection.post(url, json=data)
    raise LootRetrieveException
