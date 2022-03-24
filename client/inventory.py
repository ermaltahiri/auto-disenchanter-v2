from .exceptions import LootRetrieveException
from .logger import logger


def get_inventory_by_type(connection, inventory_type):
    res = connection.get(f'/lol-inventory/v2/inventory/{inventory_type}')
    res_json = res.json()
    if res_json == []:
        logger.info('Can not retrieve inventory...')
        raise LootRetrieveException
    return res_json
