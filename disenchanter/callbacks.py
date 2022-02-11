import csv
import os
import time
import traceback
from tkinter import filedialog
from tkinter import messagebox

from .logger import logger
from .persistence import atexit
from .tasks import disenchant_task


def on_browse(variables):
    file = filedialog.askopenfilename()
    if file:
        variables['input_path'].set(file)
        atexit(variables, [])  # save persistence data


def on_start(variables):
    try:
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
        disenchant_task(accounts, variables)
    except UnicodeDecodeError:
        logger.error('Invalid input file.')
    except Exception:
        messagebox.showerror('Contact the developer', traceback.format_exc())
