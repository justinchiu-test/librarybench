import argparse

def generate_cli(schema):
    parser = argparse.ArgumentParser()
    for key, val in schema.items():
        arg_type = type(val)
        parser.add_argument(f'--{key}', type=arg_type, default=val, help=f'Set {key} (default: {val})')
    return parser
