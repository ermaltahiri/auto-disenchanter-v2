from client.buy_champions import buy_champions_by_cost
from client.capsules import open_champion_capsules
from client.chests import open_generic_chests
from client.chests import open_masterwork_chests
from client.disenchant import disenchant
from client.export import export_info
from client.icon import change_icon
from client.keys import forge_keys
from client.redeem import redeem_by_value
from client.redeem import redeem_free
from client.skins import reroll_skins
from client.tokens import forge_tokens_into_champion_shards


def get_options(config=None):
    max_champs = 999 if config is None else config['max_champs']
    output_file = None if config is None else config['output_file']
    options = [
        ['forge_keys', 'Forge keys', (forge_keys, [], {})],
        ['open_champion_capsules', 'Open champion capsules', (open_champion_capsules, [], {})],
        ['open_generic_chests', 'Open generic chests', (open_generic_chests, [], {})],
        ['open_masterwork_chests', 'Open masterwork chests', (open_masterwork_chests, [], {})],
        ['forge_tokens', 'Forge tokens to champ shards',
            (forge_tokens_into_champion_shards, [], {})],
        ['redeem_free', 'Redeem free champ shards', (redeem_free, [], {})],
        ['redeem_450', 'Redeem 450BE champ shards', (redeem_by_value, [450], {})],
        ['redeem_1350', 'Redeem 1350BE champ shards', (redeem_by_value, [1350], {})],
        ['redeem_3150', 'Redeem 3150BE champ shards', (redeem_by_value, [3150], {})],
        ['redeem_4800', 'Redeem 4800BE champ shards', (redeem_by_value, [4800], {})],
        ['redeem_6300', 'Redeem 6300BE champ shards', (redeem_by_value, [6300], {})],
        ['disenchant', 'Disenchant all champ shards', (disenchant, [], {})],
        ['buy_450', 'Buy 450BE champs', (buy_champions_by_cost, [450], {
                                         'max_champs': max_champs})],  # tested
        ['buy_1350', 'Buy 1350BE champs', (buy_champions_by_cost, [1350], {
                                           'max_champs': max_champs})],  # tested
        ['buy_3150', 'Buy 3150BE champs', (buy_champions_by_cost, [3150], {
                                           'max_champs': max_champs})],  # tested
        ['buy_4800', 'Buy 4800BE champs', (buy_champions_by_cost, [4800], {
                                           'max_champs': max_champs})],  # tested
        ['buy_6300', 'Buy 6300BE champs', (buy_champions_by_cost, [6300], {
                                           'max_champs': max_champs})],  # tested
        ['change_icon', 'Change icon to plant', (change_icon, [23], {})],  # tested
        ['reroll_skins', 'Reroll skins', (reroll_skins, [], {})],  # tested
        ['export_info', 'Export info',
            (export_info, [], {'account': {}, 'output_file': output_file})],
    ]
    options_internal_names = [o[0] for o in options]
    options_mapped = {o[0]: o for o in options}
    return options, options_internal_names, options_mapped
