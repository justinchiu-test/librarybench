"""
Main entry point for the unified command-line task manager CLI.
"""

import sys
from typing import List, Optional

from cli.commands import create_parser, execute_command
from cli.task_manager import UnifiedTaskManager


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the CLI.
    
    Args:
        args: Command line arguments (defaults to sys.argv[1:])
        
    Returns:
        int: Exit code (0 for success, non-zero for error)
    """
    parser = create_parser()
    
    # Parse arguments
    parsed_args = parser.parse_args(args if args is not None else sys.argv[1:])
    
    # Show help if no command specified
    if not parsed_args.command:
        parser.print_help()
        return 0
    
    # Initialize task manager
    task_manager = UnifiedTaskManager()
    
    # Execute command
    try:
        result = execute_command(parsed_args, task_manager)
        print(result)
        return 0
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())