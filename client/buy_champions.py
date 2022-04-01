import time
from copy import deepcopy

from .buy_schema import buy_schema
from .catalog import catalog
from .champions import get_champion_cost
from .champions import get_champion_name
from .champions import get_champions_by_cost
from .logger import logger


def post_buy(connection, item_id, price):
    schema = deepcopy(buy_schema)
    schema['items'][0]['itemKey']['itemId'] = item_id
    schema['items'][0]['purchaseCurrencyInfo']['price'] = price
    response = connection.post('/lol-purchase-widget/v2/purchaseItems', json=schema)
    if response.ok:
        return None
    return response.json()


def buy_champions_by_id(connection, ids, max_champs=999, retry=10):
    if retry <= 0:
        return False
    response = connection.get('/lol-champions/v1/owned-champions-minimal')
    if response.ok:
        response = response.json()
        champions_owned = [str(c['id']) for c in response if c['ownership']['owned']]
        champions_to_buy = [c for c in ids if str(c) not in champions_owned]
        if champions_to_buy == []:
            logger.info('All champions are already purchased.')
            return True
        champion_catalog = catalog(connection, 'CHAMPION')
        for _ in range(60):
            if len(champions_owned) >= max_champs:
                logger.info('''Max no of champions already owned, '''
                            f'''Max champs: {max_champs}, Champions owned: {len(champions_owned)}.''')
                break
            if champions_to_buy == []:
                logger.info('All champions are already purchased.')
                return True
            champion = champions_to_buy[0]
            name = get_champion_name(champion_catalog, champion)
            cost = get_champion_cost(champion_catalog, champion)
            if cost is None:
                logger.error(f'{name} not found in champion catalog.')
                return False
            logger.info(f'Buying champion: {name}...')
            errors = post_buy(connection, champion, cost)
            if errors is None:
                champions_owned.append(champions_to_buy.pop(0))
                continue
            logger.error(errors)
            if not isinstance(errors, dict):
                time.sleep(5)
                continue
            error_details = errors.get('errorDetails', [])
            error_message = errors.get('message', '')
            error_code = errors.get('errorCode')
            if 'validation.item.owned' in error_details or 'purchase.alreadyOwned' in error_message:
                logger.info(f'{name} is already owned.')
                champions_to_buy.pop(0)
                continue
            if error_code == 'BAD_AUTHORIZATION_PARAM':
                logger.info(
                    'BAD_AUTHORIZATION_PARAM. Could not handle buy error. Skipping champion purchase...')
                champions_to_buy.pop(0)
                continue
            if 'validation.item.not.enough.currency' in error_details or 'purchase.notEnoughCurrency' in error_message:
                logger.info('Not enough BE to buy champion.')
                return False
            logger.info('Unknown error occurred when buying the champion')
            logger.error(errors)
            time.sleep(10)
    else:
        logger.debug('Cannot fetch owned champions')
        logger.info(f'Res: {response.status_code}, {response.content}')
        if response.status_code == 404:
            time.sleep(1)
            return buy_champions_by_id(connection, ids, max_champs, retry - 1)


def buy_champions_by_cost(connection, cost, max_champs=999):
    champion_catalog = catalog(connection, 'CHAMPION')
    ids = get_champions_by_cost(champion_catalog, cost)
    logger.info(f'Buying {cost} BE champions...')
    buy_champions_by_id(connection, ids, max_champs)
