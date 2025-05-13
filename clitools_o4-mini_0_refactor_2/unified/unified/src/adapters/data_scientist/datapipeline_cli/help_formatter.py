"""
Help formatting for data_scientist datapipeline CLI.
"""
def format_help(commands, mode='plain'):
    if mode == 'md':
        return '\n'.join(f"### `{k}`\n\n{v}" for k, v in commands.items())
    elif mode == 'color':
        return '\n'.join(f"\033[94m{k}\033[0m: {v}" for k, v in commands.items())
    else:
        raise ValueError(f"Unknown mode: {mode}")