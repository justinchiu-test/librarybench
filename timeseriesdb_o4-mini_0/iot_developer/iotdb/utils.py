import json
import fnmatch
import re

def json_import(path):
    with open(path) as f:
        data = json.load(f)
    return data

def tag_pattern_query(devices_tags, pattern):
    key, pat = pattern.split(':',1)
    regex = fnmatch.translate(pat)
    prog = re.compile(regex)
    return [dev for dev,tags in devices_tags.items() if key in tags and prog.match(tags[key])]
