from .logger import logger


def post_recipe(connection, recipe, materials, repeat=1):
    if repeat == 0:
        return
    logger.info(f'Posting recipe {recipe}...')
    url = f'/lol-loot/v1/recipes/{recipe}/craft?repeat={repeat}'
    connection.post(url, json=materials)


def post_key_fragment_forge(connection, repeat=1):
    post_recipe(
        connection,
        'MATERIAL_key_fragment_forge',
        ['MATERIAL_key_fragment'],
        repeat=repeat,
    )


def post_generic_chest_open(connection, repeat=1):
    logger.info(f'Opening {repeat} generic chests...')
    post_recipe(
        connection,
        'CHEST_generic_OPEN',
        ['CHEST_generic', 'MATERIAL_key'],
        repeat=repeat,
    )


def post_masterwork_chest_open(connection, repeat=1):
    logger.info(f'Opening {repeat} masterwork chests...')
    post_recipe(
        connection,
        'CHEST_224_OPEN',
        ['CHEST_224', 'MATERIAL_key'],
        repeat=repeat,
    )


def post_champion_mastery_chest_open(connection, repeat=1):
    logger.info(f'Opening {repeat} champion mastery chests...')
    post_recipe(
        connection,
        'CHEST_champion_mastery_OPEN',
        ['CHEST_champion_mastery', 'MATERIAL_key'],
        repeat=repeat,
    )
