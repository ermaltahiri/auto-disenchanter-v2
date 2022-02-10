from logger import logger


def get_champion_cost(champion_catalog, champion_id):
    try:
        champion = [c for c in champion_catalog if str(c['itemId']) == str(champion_id)]
        if champion == []:
            return None
        return champion[0]['prices'][0]['cost']
    except TypeError:
        logger.info(f'DEBUG: champion_catalog: {champion_catalog}')
        return None


def get_champions_by_cost(champion_catalog, cost):
    champions = [c['itemId'] for c in champion_catalog if c['prices'][0]['cost'] == cost]
    return champions


def get_champion_name(champion_catalog, champion_id):
    for champion in champion_catalog:
        if str(champion['itemId']) == str(champion_id):
            localizations = champion['localizations']
            localization = list(localizations.values())[0]
            return localization['name']
    return 'UNKNOWN'
