import re
import time

from .exceptions import LootRetrieveException
from .logger import logger
from .loot import get_loot

capsule_re = 'CHEST_((?!(generic|224|champion_mastery)).)*'


def open_champion_capsules(connection, retry_limit=1):
    logger.info('Opening all champion capsules...')
    for _ in range(retry_limit):
        try:
            res_json = get_loot(connection)
        except LootRetrieveException:
            time.sleep(1)
            continue
        loot_result = [m for m in res_json if re.fullmatch(capsule_re, m['lootId'])]
        if loot_result == []:
            return
        for loot in loot_result:
            name, count = loot['lootName'], loot['count']
            logger.info(f'Opening chest: {name}, Count: {count}')
            url = f'/lol-loot/v1/recipes/{name}_OPEN/craft?repeat={count}'
            data = [name]
            connection.post(url, json=data)
    raise LootRetrieveException
