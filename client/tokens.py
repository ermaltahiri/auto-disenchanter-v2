import time

from logger import logger

from .exceptions import LootRetrieveException
from .loot import get_loot
from .loot import get_loot_count
from .recipes import post_recipe


def forge_tokens(connection, recipe, material, cost, retry_limit=10):
    for _ in range(retry_limit):
        try:
            loot_json = get_loot(connection)
        except LootRetrieveException:
            time.sleep(1)
            continue
        tokens_count = get_loot_count(loot_json, material)
        forgable = tokens_count // cost
        if forgable == 0:
            return
        post_recipe(connection, recipe, [material], repeat=forgable)
    raise LootRetrieveException


def forge_tokens_into_champion_shards(connection, retry_limit=10):
    response = connection.get('/lol-loot/v1/player-loot-map').json()
    loots = [l for l in response if l.startswith('MATERIAL_') and l != 'MATERIAL_key_fragment']
    for loot in loots:
        res = connection.get(f'/lol-loot/v1/recipes/initial-item/{loot}').json()
        for recipe in res:
            if any(o['lootName'] == 'CHEST_241' for o in recipe['outputs']):
                name = recipe['contextMenuText']
                cost = recipe['slots'][0]['quantity']
                recipe_name = recipe['recipeName']
                logger.info(f'{name} found. Price: {cost}, Recipe name: {recipe_name}')
                forge_tokens(connection, recipe_name, loot, cost, retry_limit)
