import time

from .exceptions import LootRetrieveException
from .loot import get_key_fragment_count
from .loot import get_loot
from .recipes import post_key_fragment_forge


def forge_keys(connection, retry_limit=10):
    for _ in range(retry_limit):
        try:
            loot_json = get_loot(connection)
        except LootRetrieveException:
            time.sleep(1)
            continue
        forgable_keys = get_key_fragment_count(loot_json) // 3
        if forgable_keys > 0:
            post_key_fragment_forge(connection, forgable_keys)
            continue
    raise LootRetrieveException
