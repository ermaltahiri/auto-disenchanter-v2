import time

from .exceptions import AccountChangeNeededException
from .exceptions import LoginUnsuccessfulException
from .logger import logger


def get_username(connection):
    res = connection.get('/lol-login/v1/login-platform-credentials')
    if not res.ok:
        return None
    res_json = res.json()
    if 'username' not in res_json:
        return None
    return res_json['username']


def check_username(connection, expected_username, timeout=20):
    logger.info('Checking username...')
    start = time.time()
    while True:
        if time.time() - start > timeout:
            raise LoginUnsuccessfulException
        username_client = get_username(connection)
        if username_client is None or username_client == '':
            time.sleep(1)
            continue
        if expected_username.lower() == username_client.lower():
            break
        logger.info(
            f'Expected username: {expected_username.lower()}. '
            f'Current username: {username_client.lower()}')
        raise AccountChangeNeededException
