import os
import traceback
from datetime import datetime
from functools import partial
from threading import Thread
from tkinter import messagebox

import requests
from league_connection import LeagueConnection
from league_connection.exceptions import LeagueConnectionError

from client.exceptions import AccountBannedException
from client.exceptions import AuthenticationFailureException
from client.exceptions import ClientException
from client.exceptions import ConsentRequiredException
from client.exceptions import NameChangeRequiredException
from client.exceptions import RegionMissingException
from client.export import add_info_to_account
from client.export import export_account
from client.login import login
from client.session import wait_session
from client.username import check_username
from process.league import kill_league_client
from process.league import kill_riot_client
from process.league import open_league_client
from process.league import open_riot_client
from process.league import remove_lockfile

from .entries import get_config_from_entries
from .logger import logger
from .options import get_options

SKIP_ACCOUNT_EXCEPTIONS = (
    AccountBannedException,
    AuthenticationFailureException,
    ConsentRequiredException,
    NameChangeRequiredException,
    RegionMissingException,
)

now = datetime.now().strftime("%Y-%b-%d %H-%M-%S").lower()
output_file = f'output_{now}.txt'


def execute(connection, selected, options_mapped):
    for option in selected:
        _, display_name, data = options_mapped[option]
        logger.info(f'Current task: {display_name}')
        func, args, kwargs = data
        func = partial(func, connection)
        func(*args, **kwargs)


def execute_tasks_single_account(username, password, selected, options_mapped):
    account = {'username': username, 'password': password}
    riot_lockfile = os.path.expanduser(os.environ['RIOT_CLIENT_LOCKFILE'])
    lockfile_dir = os.path.dirname(os.environ['LEAGUE_CLIENT'])
    league_lockfile = os.path.join(lockfile_dir, 'lockfile')
    while True:
        try:
            open_riot_client(os.environ['RIOT_CLIENT_SERVICES'])
            logger.info('Getting riot client connection...')
            riot_connection = LeagueConnection(riot_lockfile)
            login(riot_connection, username, password)
            open_league_client(os.environ['LEAGUE_CLIENT'])
            logger.info('Getting league client connection...')
            league_connection = LeagueConnection(league_lockfile)
            league_connection.post('/riotclient/kill-ux')
            wait_session(league_connection)
            check_username(league_connection, username)
            execute(league_connection, selected, options_mapped)
            add_info_to_account(league_connection, account)
            export_account(account, output_file)
            logger.info('Logging out...')
            kill_league_client()
            kill_riot_client()
            remove_lockfile(league_lockfile)
            return True
        except requests.RequestException as exp:
            logger.error(f'{exp.__class__.__name__}. Retrying...')
        except SKIP_ACCOUNT_EXCEPTIONS as exp:
            logger.error(f'{exp.__class__.__name__}. Skipping account...')
            kill_league_client()
            kill_riot_client()
            remove_lockfile(league_lockfile)
            export_account(account, output_file)
            return False
        except (ClientException, LeagueConnectionError) as exp:
            logger.error(f'{exp.__class__.__name__}. Retrying...')
            kill_league_client()
            kill_riot_client()
            remove_lockfile(league_lockfile)


def execute_tasks(accounts, variables):
    try:
        variables['browse_button']['state'] = 'disabled'
        variables['start_button']['state'] = 'disabled'
        variables['input_path_entry']['state'] = 'disabled'
        selected = []
        config = get_config_from_entries(variables)
        if config is None:
            return
        _, options_internal_names, options_mapped = get_options(config)
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
            execute_tasks_single_account(username, password, selected, options_mapped)
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
