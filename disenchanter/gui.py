import tkinter as tk
import tkinter.font
import tkinter.scrolledtext as tkscroledtext
from functools import partial
from uuid import uuid4


def create_frames(root):
    frames = {
        'config': tk.LabelFrame(root, name='config', text='Configuration'),
        'options': tk.LabelFrame(root, name='options', text='Options'),
        'entries': tk.LabelFrame(root, name='entries', text='Entries'),
        'console': tk.LabelFrame(root, name='console', text='Console'),
        'status': tk.LabelFrame(root, name='status', text='Status'),
    }
    frames['config'].pack(fill='both')
    frames['options'].pack(fill='both')
    frames['entries'].pack(fill='both')
    frames['console'].pack(fill='both', expand='yes')
    frames['status'].pack(fill='both')
    return frames


def create_config(frame, callbacks):
    variables = {}
    input_path_variable = tk.StringVar()
    input_label = tk.Label(frame, text='Input file')
    input_path = tk.Entry(frame, textvariable=input_path_variable)
    browse_button = tk.Button(frame, text='Browse', command=callbacks['on_browse'])
    start_button = tk.Button(frame, text='Start', command=callbacks['on_start'])
    tk.Grid.columnconfigure(frame, 1, weight=1)
    input_label.grid(row=0, column=0)
    input_path.grid(row=0, column=1, sticky='NSEW')
    browse_button.grid(row=0, column=2)
    start_button.grid(row=0, column=3)
    variables['input_path'] = input_path_variable
    variables['input_path_entry'] = input_path
    variables['browse_button'] = browse_button
    variables['start_button'] = start_button
    return variables


def create_entries(frame, options, entries_per_row=5):
    variables = {}
    for i, option in enumerate(options):
        internal_name, display_name = option[:2]
        row = (i // entries_per_row) * 2
        column = i % entries_per_row
        entry_variable = tk.StringVar()
        label = tk.Label(frame, text=display_name)
        entry = tk.Entry(frame, textvariable=entry_variable)
        label.grid(row=row, column=column)
        entry.grid(row=row + 1, column=column, sticky='NSEW')
        variables[f'entry_{internal_name}'] = entry_variable
    return variables


def create_checkboxes(frame, options, entries_per_row=5):
    variables = {}
    for i, option in enumerate(options):
        internal_name, display_name = option[:2]
        row = i // entries_per_row
        column = i % entries_per_row
        variable = tk.BooleanVar()
        button = tk.Checkbutton(frame, variable=variable, text=display_name)
        tk.Grid.columnconfigure(frame, column, weight=1)
        button.grid(row=row, column=column, sticky='NSW')
        variables[f'checkbox_{internal_name}'] = variable
    return variables


def create_console(frame):
    text = tkscroledtext.ScrolledText(frame, name='text', height=0)
    text.pack(fill='both', expand='yes')
    text.bind('<Key>', lambda e: 'break')  # makes readonly
    return {'console': text}


def create_status(frame):
    variable = tk.StringVar()
    entry = tk.Entry(frame, textvariable=variable)
    entry.bind('<Key>', lambda e: 'break')  # makes readonly
    entry.pack(fill='both')
    return {'status': variable}


def _get_gui_root(configuration):
    font_size = configuration.get('font_size', 10)

    entries_per_row = configuration.get('entries_per_row', 5)
    title = configuration.get('title', str(uuid4()))
    geometry = configuration.get('geometry', '600x400+0+0')

    root = tk.Tk()
    default = tkinter.font.nametofont('TkFixedFont').cget('family')
    font_family = configuration.get('font_family', default)
    font = tkinter.font.Font(family=font_family, size=font_size)
    root.option_add('*Font', font)
    root.title(title)
    root.geometry(geometry)
    if configuration.get('always_on_top', False):
        root.wm_attributes('-topmost', 1)
    frames = create_frames(root)
    variables = {}

    partial_callbacks = {}
    for name, callback in configuration['callbacks'].items():
        partial_callbacks[name] = partial(callback, variables)

    checkboxes = configuration.get('checkboxes', [])
    entries = configuration.get('entries', [])
    variables.update(create_config(frames['config'], partial_callbacks))
    variables.update(create_checkboxes(frames['options'], checkboxes, entries_per_row))
    variables.update(create_entries(frames['entries'], entries, entries_per_row))
    variables.update(create_console(frames['console']))
    variables.update(create_status(frames['status']))
    return root, variables


def get_gui(configuration=None):
    if configuration is None:
        configuration = {}
    root, variables = _get_gui_root(configuration)
    return root, variables
