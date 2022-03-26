import csv
import time

from client.exceptions import LootRetrieveException

from .inventory import get_inventory_by_type
from .logger import logger
from .loot import get_loot
from .loot import get_loot_count
from .region_locale import get_region_locale
from .shards import get_permanent_shard_ids
from .shards import get_rental_shard_ids
from .skins import get_mythic_skins_count
from .summoner import get_level


def export_account(account, output_file):
    logger.info('Exporting account...')
    try:
        with open(output_file, 'a+', newline='') as file_pointer:
            writer = csv.writer(file_pointer, delimiter=':')
            writer.writerow([
                account.get('region', 'null'),
                account.get('username', 'null'),
                account.get('password', 'null'),
                account.get('level', 'null'),
                account.get('mythic_count', 'null'),
                account.get('be', 'null'),
                account.get('oe', 'null'),
                account.get('rental', 'null'),
                account.get('perma', 'null'),
                account.get('inventory', 'null'),
            ])
    except OSError as exp:
        logger.error(f'{exp.__class__.__name__}. Cannot export account.')


def add_info_to_account(connection, account, retry_limit=120):
    logger.info('Fetching account info...')
    start_time = time.time()
    while True:
        try:
            if time.time() - start_time >= retry_limit:
                logger.info('Retry limit exceeded.')
                return account

            account['level'] = get_level(connection)
            if account['level'] == -1:
                time.sleep(1)
                continue

            account['mythic_count'] = get_mythic_skins_count(connection)
            if account['mythic_count'] is None:
                time.sleep(1)
                continue

            loot = get_loot(connection)
            account['be'] = get_loot_count(loot, 'CURRENCY_champion')
            account['oe'] = get_loot_count(loot, 'CURRENCY_cosmetic')
            ids = get_rental_shard_ids(connection)
            account['rental'] = ','.join(str(i) for i in ids)
            ids = get_permanent_shard_ids(connection)
            account['perma'] = ','.join(str(i) for i in ids)
            inventory_skins = get_inventory_by_type(connection, 'CHAMPION_SKIN')
            account['inventory'] = ','.join(str(i['itemId']) for i in inventory_skins)
            account['region'] = get_region_locale(connection).get('region')
            break
        except LootRetrieveException:
            time.sleep(1)
    return account
