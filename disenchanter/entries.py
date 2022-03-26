

from tkinter import messagebox

from .logger import logger


def parse_max_champs(value):
    if value == '':
        return 9999
    return int(value)


entries = [
    ['max_champs', 'Max Champions', parse_max_champs]
]
entries_internal_names = [e[0] for e in entries]
entries_mapped = {e[0]: e for e in entries}


def get_config_from_entries(variables):
    config = {}
    for entry in entries_internal_names:
        _, display_name, parse_entry = entries_mapped[entry]
        try:
            config[entry] = parse_entry(variables[f'entry_{entry}'].get())
        except ValueError:
            logger.error(f'Invalid value set for entry: {display_name}.')
            messagebox.showerror('Error', f'Invalid value set for entry: {display_name}.')
            return None
    return config
