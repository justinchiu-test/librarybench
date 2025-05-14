import json
import configparser

def parse_config_files(paths):
    result = {}
    for path in paths:
        if path.lower().endswith('.json'):
            with open(path, 'r') as f:
                data = json.load(f)
            result.update(data)
        elif path.lower().endswith('.ini'):
            parser = configparser.ConfigParser()
            parser.read(path)
            # use 'default' section if present, otherwise fall back to DEFAULT
            if parser.has_section('default'):
                data = dict(parser.items('default'))
            else:
                data = dict(parser.defaults())
            result.update(data)
        else:
            pass  # Skip unsupported formats
    return result