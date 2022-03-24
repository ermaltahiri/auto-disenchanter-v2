

from datetime import datetime
from tkinter import messagebox

from .logger import logger

entries = [
    ['max_champs', 'Max Champions', int]
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
    now = datetime.now().strftime("%Y-%b-%d %H-%M-%S").lower()
    output_file = f'output_{now}.txt'
    config['output_file'] = output_file
    return config
