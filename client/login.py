import json
import time

import requests

from .exceptions import AccountBannedException
from .exceptions import AuthenticationFailureException
from .exceptions import ConsentRequiredException
from .exceptions import LoginUnsuccessfulException
from .exceptions import LogoutNeededException
from .exceptions import NameChangeRequiredException
from .exceptions import RateLimitedException
from .exceptions import RegionMissingException
from .logger import logger
from .login_phases import ACCOUNT_ALIAS_CHANGE_PHASE
from .login_phases import BANNED_PHASES
from .login_phases import CONSENT_REQUIRED_PHASES
from .login_phases import EULA_PHASES
from .login_phases import LOGIN_PHASES
from .login_phases import REGION_MISSING_PHASES
from .login_phases import SUCCESS_PHASES
from .login_phases import WAIT_FOR_LAUNCH_PHASES


def get_auth_state(connection):
    res = connection.get('/rso-auth/v1/authorization')
    if not res.ok:
        return 'no_authorization'
    res = connection.get('/eula/v1/agreement')
    res_json = res.json()
    if 'acceptance' not in res_json:
        return 'no_authorization'
    if res_json['acceptance'] != 'Accepted':
        return 'agreement_not_accepted'
    return 'success'


def is_age_restricted(connection):
    try:
        response = connection.get('/age-restriction/v1/age-restriction/products/league_of_legends')
        response = response.json()
        return response.get('restricted', False)
    except (json.decoder.JSONDecodeError, requests.exceptions.RequestException):
        return False


def is_country_region_missing(connection):
    try:
        response = connection.get('/riot-client-auth/v1/userinfo')
        response = response.json()
        return response.get('country', 'npl') == 'nan'
    except (json.decoder.JSONDecodeError, requests.exceptions.RequestException):
        return False


def accept_agreement(connection):
    connection.put('/eula/v1/agreement/acceptance')


def wait_until_patched(connection, timeout=7200):
    start_time = time.time()
    while True:
        try:
            time.sleep(10)
            time_elapsed = time.time() - start_time
            logger.info(f'Patching riot client. Time elapsed: {int(time_elapsed)}s.')
            if time_elapsed > timeout:
                raise LogoutNeededException
            res = connection.get('/rnet-lifecycle/v1/product-context-phase')
            phase = res.json()
            if phase not in ['PatchStatus', 'WaitingForPatchStatus']:
                break
        except requests.exceptions.RequestException:
            pass


def authorize(connection, username, password):
    state = get_auth_state(connection)
    logger.info(f'Auth state: {state}')
    if state == 'success':
        if is_age_restricted(connection):
            logger.info('Age restricted account detected.')
            raise ConsentRequiredException
        if is_country_region_missing(connection):
            logger.info('Country/region missing account detected.')
            raise ConsentRequiredException
        return True
    if state == 'agreement_not_accepted':
        accept_agreement(connection)
        return True
    data = {'clientId': 'riot-client', 'trustLevels': ['always_trusted']}
    res = connection.post('/rso-auth/v2/authorizations', json=data)
    if not res.ok and 'rate_limited' in res.text:
        raise RateLimitedException
    data = {'username': username, 'password': password, 'persistLogin': False}
    res = connection.put('/rso-auth/v1/session/credentials', json=data)
    res_json = res.json()
    if 'message' in res_json:
        if res_json['message'] == 'authorization_error: consent_required: ':
            raise ConsentRequiredException
    if 'error' in res_json:
        if res_json['error'] == 'auth_failure':
            raise AuthenticationFailureException
        if res_json['error'] == 'rate_limited':
            raise RateLimitedException
    return False


def launch_league(connection):
    logger.info('Launching league...')
    connection.post('/product-launcher/v1/products/league_of_legends/patchlines/live')


def get_product_context_phase(connection):
    res = connection.get('/rnet-lifecycle/v1/product-context-phase')
    if res.status_code == 404:
        return None
    return res.json()


def login(connection, username, password, timeout=180):
    logger.info('Logging in...')
    start_time = time.time()
    while True:
        if time.time() - start_time >= timeout:
            raise LoginUnsuccessfulException('Timeout')

        phase = get_product_context_phase(connection)
        logger.info(f'Riot client phase: {phase}')

        # Bad phases
        if phase == 'Unknown':
            raise LoginUnsuccessfulException('Phase "Unknown" returned by riot client')
        if phase in REGION_MISSING_PHASES:
            raise RegionMissingException
        if phase in BANNED_PHASES:
            raise AccountBannedException('RIOT_BAN')
        if phase in CONSENT_REQUIRED_PHASES:
            raise ConsentRequiredException
        if phase in ACCOUNT_ALIAS_CHANGE_PHASE:
            raise NameChangeRequiredException

        # Good phases
        if phase in SUCCESS_PHASES:
            break

        if phase in WAIT_FOR_LAUNCH_PHASES:
            launch_league(connection)
            time.sleep(2)
            continue
        if phase is None or phase in LOGIN_PHASES:
            if authorize(connection, username, password):
                break
        if phase in EULA_PHASES:
            accept_agreement(connection)
            time.sleep(2)
            continue
        if phase in ['PatchStatus', 'WaitingForPatchStatus']:
            wait_until_patched(connection)
            continue
        time.sleep(2)
