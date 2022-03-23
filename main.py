'''Main module'''
from atexit import register

from dotenv import load_dotenv

from client.logger import logger as client_logger
from disenchanter.callbacks import on_browse
from disenchanter.callbacks import on_start
from disenchanter.entries import entries
from disenchanter.entries import entries_internal_names
from disenchanter.gui import get_gui
from disenchanter.logger import logger as disenchanter_logger
from disenchanter.options import get_options
from disenchanter.persistence import atexit
from disenchanter.persistence import atstart
from handlers import TkinterHandler
from logger import formatter
from logger import logger as root_logger


def setup_tkinter_handler(console):
    handler = TkinterHandler(text=console)
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    disenchanter_logger.addHandler(handler)
    client_logger.addHandler(handler)


def main():
    '''Main function'''
    load_dotenv('default.env')
    options, options_internal_names, _ = get_options()
    root, variables = get_gui({
        'title': 'Auto Disenchanter v2',
        'checkboxes': options,
        'entries': entries,
        'entries_per_row': 3,
        'geometry': '800x600',
        'callbacks': {
            'on_browse': on_browse,
            'on_start': on_start,
        }
    })
    setup_tkinter_handler(variables['console'])
    register(atexit, variables, options_internal_names, entries_internal_names)
    atstart(variables, options_internal_names, entries_internal_names)
    root.mainloop()


if __name__ == '__main__':
    main()
