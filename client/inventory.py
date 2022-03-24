from .exceptions import LootRetrieveException
from .logger import logger


def get_inventory_by_type(connection, inventory_type):
    res = connection.get(f'/lol-inventory/v2/inventory/{inventory_type}')
    if not res.ok:
        logger.info('Cannot retrieve inventory.')
        raise LootRetrieveException
    res_json = res.json()
    return res_json
