
import os
import traceback
from functools import partial
from threading import Thread
from tkinter import messagebox

from league_connection import LeagueConnection

from client.exceptions import AccountBannedException
from client.exceptions import AuthenticationFailureException
from client.exceptions import ClientException
from client.exceptions import ConsentRequiredException
from client.exceptions import NameChangeRequiredException
from client.exceptions import RegionMissingException
from client.login import login
from client.session import wait_session
from client.username import check_username
from logger import logger
from process.league import kill_league_client
from process.league import kill_riot_client
from process.league import open_league_client
from process.league import open_riot_client

from .logger import logger
from .options import options_internal_names
from .options import options_mapped

SKIP_ACCOUNT_EXCEPTIONS = (
    AccountBannedException,
    AuthenticationFailureException,
    ConsentRequiredException,
    NameChangeRequiredException,
    RegionMissingException,
)


def execute(connection, selected):
    for option in selected:
        _, display_name, data = options_mapped[option]
        logger.info(f'Current task: {display_name}')
        func, args, kwargs = data
        func = partial(func, connection)
        func(*args, **kwargs)


def execute_tasks_single_account(username, password, selected):
    while True:
        try:
            open_riot_client(os.environ['RIOT_CLIENT_SERVICES'])
            lockfile = os.path.expanduser(os.environ['RIOT_CLIENT_LOCKFILE'])
            logger.info('Getting riot client connection...')
            riot_connection = LeagueConnection(lockfile)
            login(riot_connection, username, password)
            open_league_client(os.environ['LEAGUE_CLIENT'])
            lockfile_dir = os.path.dirname(os.environ['LEAGUE_CLIENT'])
            lockfile = os.path.join(lockfile_dir, 'lockfile')
            logger.info('Getting league client connection...')
            league_connection = LeagueConnection(lockfile)
            wait_session(league_connection)
            check_username(league_connection, username)
            execute(league_connection, selected)
            logger.info('Logging out...')
            kill_league_client()
            kill_riot_client()
            return True
        except SKIP_ACCOUNT_EXCEPTIONS as exp:
            logger.error(f'{exp.__class__.__name__}. Skipping account...')
            kill_league_client()
            kill_riot_client()
            return False
        except ClientException as exp:
            logger.error(f'{exp.__class__.__name__}. Retrying...')
            kill_league_client()
            kill_riot_client()


def execute_tasks(accounts, variables):
    try:
        variables['browse_button']['state'] = 'disabled'
        variables['start_button']['state'] = 'disabled'
        variables['input_path_entry']['state'] = 'disabled'
        selected = []
        for option in options_internal_names:
            if variables[f'checkbox_{option}'].get():
                selected.append(option)
        total = len(accounts)
        logger.info(f'Found {total} account(s).')
        for i, account in enumerate(accounts):
            progress = i * 100 // total
            variables['status'].set(f'{progress}% completed ({i}/{total}).')
            username, password = account
            logger.info(f'Working on account {username}...')
            execute_tasks_single_account(username, password, selected)
        variables['status'].set(f'100% completed ({total}/{total}).')
        logger.info('Done.')
    except Exception:
        messagebox.showerror('Contact the developer', traceback.format_exc())
        variables['status'].set('')
    finally:
        variables['browse_button']['state'] = 'normal'
        variables['start_button']['state'] = 'normal'
        variables['input_path_entry']['state'] = 'normal'


def execute_tasks_in_background(accounts, variables):
    Thread(target=execute_tasks, daemon=True, args=(accounts, variables)).start()
