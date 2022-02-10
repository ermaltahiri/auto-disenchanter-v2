import time

import requests

from .exceptions import AccountBannedException
from .exceptions import LoginUnsuccessfulException
from .exceptions import NameChangeRequiredException
from .logger import logger


def get_session(connection):
    res = connection.get('/lol-login/v1/session')

    if res.status_code == 404:
        return 'not_found'

    res_json = res.json()
    if res_json['state'] == 'IN_PROGRESS':
        return 'in_progress'
    if res_json.get('isNewPlayer', False):
        return 'new_player'
    if res_json['state'] == 'ERROR':
        if res_json['error']['messageId'] == 'ACCOUNT_BANNED':
            raise AccountBannedException('RIOT_BAN')

    # Check if summoner name change required
    res = connection.get('/lol-summoner/v1/current-summoner')
    if not res.ok:
        return 'not_found'
    res_json = res.json()
    if res_json['nameChangeFlag']:
        return 'name_change'
    return 'succeed'


def wait_session_in_progress(connection, timeout=180):
    start = time.time()
    while True:
        if time.time() - start > timeout:
            logger.info('Session stuck in in_progress. Restarting client...')
            raise LoginUnsuccessfulException
        session = get_session(connection)
        logger.debug(f'Session is {session}')
        if session != 'in_progress':
            break
        time.sleep(1)


def wait_session(connection, timeout=60):
    start = time.time()
    logger.info('Waiting for session...')
    while True:
        try:
            if time.time() - start > timeout:
                raise LoginUnsuccessfulException
            session = get_session(connection)
            logger.debug(f'Session is {session}')
            if session == 'succeed':
                break
            if session == 'name_change':
                raise NameChangeRequiredException
            if session == 'new_player':
                raise NameChangeRequiredException
            if session == 'in_progress':
                wait_session_in_progress(connection)
            time.sleep(1)
        except requests.exceptions.RequestException:
            time.sleep(1)
