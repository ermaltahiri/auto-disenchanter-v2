import re

from .loot import get_loot


def get_shard_ids(connection, pattern):
    ids = []
    all_loot = get_loot(connection)
    for loot in all_loot:
        match = re.match(pattern, loot['lootId'])
        if match is not None:
            ids.append(int(match.group(1)))
    return ids


def get_permanent_shard_ids(connection):
    return get_shard_ids(connection, 'CHAMPION_SKIN_(\d+)')


def get_rental_shard_ids(connection):
    return get_shard_ids(connection, 'CHAMPION_SKIN_RENTAL_(\d+)')
