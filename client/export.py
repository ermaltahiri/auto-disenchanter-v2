import csv
import time

from .logger import logger
from .skins import get_mythic_skins_count
from .summoner import get_level


def export_account(account, output_file):
    logger.info('Exporting account...')
    try:
        with open(output_file, 'a+', newline='') as file_pointer:
            writer = csv.writer(file_pointer, delimiter=':')
            writer.writerow(account.values())
    except OSError as exp:
        logger.error(f'{exp.__class__.__name__}. Cannot export account.')


def export_level_and_mythic_count(connection, account, output_file):
    logger.info('Fetching level and mythic count...')
    while 'level' not in account or 'mythic_count' not in account:
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
    export_account(account, output_file)
