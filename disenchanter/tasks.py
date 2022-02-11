
import time
from threading import Thread

from .logger import logger


def disenchant(accounts, variables):
    try:
        variables['browse_button']['state'] = 'disabled'
        variables['start_button']['state'] = 'disabled'
        variables['input_path_entry']['state'] = 'disabled'
        total = len(accounts)
        logger.info(f'Found {total} account(s).')
        for i, account in enumerate(accounts):
            progress = i * 100 // total
            variables['status'].set(f'{progress}% completed.')
            username, password = account
            logger.info(f'Working on account {username}...')
            time.sleep(5)
        variables['status'].set('100% completed.')
        logger.info('Done.')
    finally:
        variables['browse_button']['state'] = 'normal'
        variables['start_button']['state'] = 'normal'
        variables['input_path_entry']['state'] = 'normal'


def disenchant_task(accounts, variables):
    Thread(target=disenchant, daemon=True, args=(accounts, variables)).start()
