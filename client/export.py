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
                account['region'],
                account['username'],
                account['password'],
                account['level'],
                account['mythic_count'],
                account['be'],
                account['oe'],
                account['rental'],
                account['perma'],
                account['inventory'],
            ])
    except OSError as exp:
        logger.error(f'{exp.__class__.__name__}. Cannot export account.')


def export_info(connection, account, output_file, retry_limit=10):
    logger.info('Fetching account info...')
    retries = 0
    while True:
        try:
            done = (
                'level' in account and
                'mythic_count' in account and
                'be' in account and
                'oe' in account and
                'rental' in account and
                'perma' in account and
                'inventory' in account and
                'region' in account
            )
            if done:
                break
            if retries >= retry_limit:
                logger.info('Retry limit exceeded.')
                account['mythic_count'] = 0
            if 'level' not in account:
                level = get_level(connection)
                if level == -1:
                    time.sleep(1)
                    continue
                account['level'] = level
            if 'mythic_count' not in account:
                mythic_count = get_mythic_skins_count(connection)
                if mythic_count is None:
                    time.sleep(1)
                    continue
                account['mythic_count'] = mythic_count
            loot = get_loot(connection)
            if 'be' not in account:
                account['be'] = get_loot_count(loot, 'CURRENCY_champion')
            if 'oe' not in account:
                account['oe'] = get_loot_count(loot, 'CURRENCY_cosmetic')
            if 'rental' not in account:
                ids = get_rental_shard_ids(connection)
                account['rental'] = ','.join(str(i) for i in ids)
            if 'perma' not in account:
                ids = get_permanent_shard_ids(connection)
                account['perma'] = ','.join(str(i) for i in ids)
            if 'inventory' not in account:
                inventory_skins = get_inventory_by_type(connection, 'CHAMPION_SKIN')
                account['inventory'] = ','.join(str(i['itemId']) for i in inventory_skins)
            if 'region' not in account:
                account['region'] = get_region_locale(connection).get('region')
        except LootRetrieveException:
            retries += 1
            time.sleep(1)
    export_account(account, output_file)
