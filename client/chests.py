import time

from .exceptions import LootRetrieveException
from .loot import get_champion_mastery_chest_count
from .loot import get_generic_chest_count
from .loot import get_key_count
from .loot import get_loot
from .loot import get_masterwork_chest_count
from .recipes import post_champion_mastery_chest_open
from .recipes import post_generic_chest_open
from .recipes import post_masterwork_chest_open


def open_generic_chests(connection, retry_limit=10):
    for _ in range(retry_limit):
        try:
            loot_json = get_loot(connection)
        except LootRetrieveException:
            time.sleep(1)
            continue
        key_count = get_key_count(loot_json)
        generic = get_generic_chest_count(loot_json)
        mastery = get_champion_mastery_chest_count(loot_json)
        chest_count = generic + mastery
        allowed = min(key_count, chest_count)
        if allowed <= 0:
            return
        post_generic_chest_open(connection)
        post_champion_mastery_chest_open(connection)
    raise LootRetrieveException


def open_masterwork_chests(connection, retry_limit=10):
    for _ in range(retry_limit):
        try:
            loot_json = get_loot(connection)
        except LootRetrieveException:
            time.sleep(1)
            continue
        key_count = get_key_count(loot_json)
        chest_count = get_masterwork_chest_count(loot_json)
        allowed = min(key_count, chest_count)
        if allowed <= 0:
            return
        post_masterwork_chest_open(connection)
    raise LootRetrieveException
