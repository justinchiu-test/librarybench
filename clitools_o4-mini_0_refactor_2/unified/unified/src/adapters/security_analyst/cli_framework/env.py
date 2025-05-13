"""
Environment override for Security Analyst CLI.
"""
def env_override(env_dict, keys):
    # env_dict: mapping of environment variables
    result = {}
    for key in keys:
        result[key] = env_dict.get(f"SEC_{key}")
    return result