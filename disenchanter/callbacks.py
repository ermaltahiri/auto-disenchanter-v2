import csv
import os
import traceback
from tkinter import filedialog
from tkinter import messagebox

from .logger import logger
from .persistence import atexit
from .tasks import execute_tasks_in_background


def on_browse(variables):
    file = filedialog.askopenfilename()
    if file:
        variables['input_path'].set(file)
        atexit(variables, [], [])  # save persistence data


def on_start(variables):
    try:
        if 'RIOT_CLIENT_SERVICES' not in os.environ:
            logger.error('RIOT_CLIENT_SERVICES value not set in .env file.')
            return
        if not os.path.isfile(os.environ.get('RIOT_CLIENT_SERVICES')):
            logger.error('FileNotFound. Set a valid RIOT_CLIENT_SERVICES file path in .env file.')
            return
        if 'LEAGUE_CLIENT' not in os.environ:
            logger.error('LEAGUE_CLIENT value not set in .env file.')
            return
        if not os.path.isfile(os.environ.get('LEAGUE_CLIENT')):
            logger.error('FileNotFound. Set a valid LEAGUE_CLIENT file path in .env file.')
            return
        input_path = variables['input_path'].get()
        if input_path == '':
            logger.error('Input file is empty.')
            return
        if not os.path.isfile(input_path):
            logger.error(f'File "{input_path}" does not exist.')
            return
        logger.info('Reading input file...')
        with open(input_path) as fp:
            accounts = []
            reader = csv.reader(fp, delimiter=":")
            for row in reader:
                accounts.append(row)
        if accounts == []:
            logger.error('Empty file loaded.')
            return
        execute_tasks_in_background(accounts, variables)
    except UnicodeDecodeError:
        logger.error('Invalid input file.')
    except Exception:
        messagebox.showerror('Contact the developer', traceback.format_exc())
