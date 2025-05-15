def format_help(help_dict, mode='md'):
    out = []
    if mode == 'md':
        for cmd, desc in help_dict.items():
            out.append(f'### `{cmd}`\n\n{desc}\n')
    elif mode == 'color':
        for cmd, desc in help_dict.items():
            out.append(f'\033[94m{cmd}\033[0m: {desc}')
    else:
        raise ValueError('Unknown mode')
    return '\n'.join(out)
