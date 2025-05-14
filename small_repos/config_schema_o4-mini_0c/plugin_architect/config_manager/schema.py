from .merge import merge_configs

def compose_schema(*schemas):
    return merge_configs(*schemas)
