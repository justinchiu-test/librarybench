import os
import sys
import argparse

def main(args=None):
    """
    Main entry point for the data pipeline CLI
    
    Args:
        args: Command line arguments (defaults to sys.argv[1:])
        
    Returns:
        dict: Result of command execution
    """
    if args is None:
        args = sys.argv[1:]
    
    parser = argparse.ArgumentParser(description='Data Pipeline CLI')
    parser.add_argument('--version', action='store_true', help='Show version and exit')
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest='action', help='Commands')
    
    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract data')
    extract_parser.add_argument('--param', default=os.environ.get('PARAM', 'default'), 
                                help='Parameter for extraction')
    
    # Transform command
    transform_parser = subparsers.add_parser('transform', help='Transform data')
    transform_parser.add_argument('--input', required=True, help='Input file')
    transform_parser.add_argument('--output', required=True, help='Output file')
    
    # Load command
    load_parser = subparsers.add_parser('load', help='Load data')
    load_parser.add_argument('--source', required=True, help='Source file')
    load_parser.add_argument('--target', required=True, help='Target destination')
    
    parsed_args = parser.parse_args(args)
    
    # Handle version flag
    if parsed_args.version:
        try:
            with open('version.txt', 'r') as f:
                version = f.read().strip()
                print(version)
                return version
        except FileNotFoundError:
            version = '0.1.0'  # Default version
            print(version)
            return version
    
    # Convert namespace to dictionary
    result = vars(parsed_args)
    
    # Print the result
    print(result)
    
    return result