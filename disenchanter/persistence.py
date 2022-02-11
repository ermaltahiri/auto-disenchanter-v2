import json


def atstart(variables, options):
    try:
        with open('state.json') as fp:
            state = json.load(fp)
            variables['input_path'].set(state['input_path'])
            for option in options:
                if option in state:
                    variables[f'checkbox_{option}'].set(state[option])
    except (OSError, json.decoder.JSONDecodeError):
        pass


def atexit(variables, options):
    state = {'input_path': variables['input_path'].get()}
    for option in options:
        state[option] = variables[f'checkbox_{option}'].get()
    with open('state.json', 'w') as fp:
        json.dump(state, fp, indent=2)
