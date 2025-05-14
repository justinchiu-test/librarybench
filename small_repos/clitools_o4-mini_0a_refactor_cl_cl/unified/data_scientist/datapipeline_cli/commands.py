"""Command execution for data scientist CLI tools."""

import argparse
import os
import sys
from typing import List, Dict, Any, Optional


def main(args: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Main entry point for data scientist CLI.

    Args:
        args (List[str], optional): Command line arguments. Defaults to None.

    Returns:
        Dict[str, Any]: Command result data.
    """
    if args is None:
        args = sys.argv[1:]

    # Check for version flag
    if len(args) > 0 and args[0] == '--version':
        try:
            with open('version.txt', 'r') as f:
                version = f.read().strip()
            print(version)
            return {'version': version}
        except (FileNotFoundError, IOError):
            print('unknown')
            return {'version': 'unknown'}

    # Basic argument parsing for extract command - using direct parsing to match tests
    if len(args) > 0 and args[0] == 'extract':
        param = None
        if len(args) > 2 and args[1] == '--param':
            param = args[2]
        else:
            param = os.environ.get('PARAM')

        result = {'action': 'extract', 'param': param}
        print(str(result))
        return result

    # Default help output
    return {'error': 'Unknown command'}