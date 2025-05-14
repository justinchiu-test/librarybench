import argparse
import random
import sys
from typing import Dict, List, Optional, Any

from .process_engine import (
    reset_machine,
    define_transition,
    simulate_sequence,
    export_machine,
    load_machine,
    export_visualization,
    run_tests
)

# Global session tracking
_SESSIONS: Dict[int, Any] = {}

def scaffold_process() -> int:
    """
    Create a new process ID for tracking.
    
    Returns:
        int: A unique process ID
    """
    # Generate a random process ID
    pid = random.randint(10000, 99999)
    while pid in _SESSIONS:
        pid = random.randint(10000, 99999)
    
    # Store empty state for this process
    _SESSIONS[pid] = None
    return pid

def dump_state(pid: int) -> Optional[Dict[str, Any]]:
    """
    Dump the current state of a process.
    
    Args:
        pid: The process ID to dump state for
    
    Returns:
        dict: The current state, or None if not set
        
    Raises:
        ValueError: If the process ID is invalid
    """
    if pid not in _SESSIONS:
        raise ValueError(f"Invalid process ID: {pid}")
    
    return _SESSIONS[pid]

def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command line arguments.

    Args:
        args: Command line arguments (defaults to sys.argv if None)

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Business Process State Machine CLI")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Define transition command
    transition_parser = subparsers.add_parser("define", help="Define a transition")
    transition_parser.add_argument("name", help="Transition name")
    transition_parser.add_argument("from_state", help="Source state (or 'None' for initial)")
    transition_parser.add_argument("to_state", help="Destination state")
    transition_parser.add_argument("--trigger", help="Trigger event name")
    
    # Simulate command
    simulate_parser = subparsers.add_parser("simulate", help="Simulate a sequence of triggers")
    simulate_parser.add_argument("triggers", nargs="+", help="Sequence of triggers to execute")
    simulate_parser.add_argument("--assert-final", help="Assert the final state")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export the state machine")
    export_parser.add_argument("--format", choices=["yaml", "json", "dict"], default="yaml", help="Export format")
    export_parser.add_argument("--output", help="Output file path")
    
    # Load command
    load_parser = subparsers.add_parser("load", help="Load a state machine definition")
    load_parser.add_argument("file", help="File to load from")
    
    # Visualize command
    visualize_parser = subparsers.add_parser("visualize", help="Generate visualization")
    visualize_parser.add_argument("--format", choices=["dot", "interactive"], default="dot", help="Visualization format")
    visualize_parser.add_argument("--output", help="Output file path")
    
    # Run tests command
    subparsers.add_parser("test", help="Run built-in tests")
    
    # Reset command
    subparsers.add_parser("reset", help="Reset the state machine")
    
    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the CLI.

    Args:
        args: Command line arguments (defaults to sys.argv if None)

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    parsed_args = parse_args(args)
    
    if parsed_args.command == "define":
        from_state = None if parsed_args.from_state.lower() == "none" else parsed_args.from_state
        define_transition(
            parsed_args.name,
            from_state,
            parsed_args.to_state,
            trigger=parsed_args.trigger
        )
        print(f"Defined transition: {parsed_args.name}")
        
    elif parsed_args.command == "simulate":
        try:
            result = simulate_sequence(parsed_args.triggers, assert_final=parsed_args.assert_final)
            print(f"Simulation completed. Final state: {result}")
        except Exception as e:
            print(f"Simulation failed: {e}")
            return 1
        
    elif parsed_args.command == "export":
        data = export_machine(format=parsed_args.format)
        if parsed_args.output:
            with open(parsed_args.output, "w") as f:
                f.write(data if isinstance(data, str) else str(data))
            print(f"State machine exported to {parsed_args.output}")
        else:
            print(data)
        
    elif parsed_args.command == "load":
        try:
            with open(parsed_args.file, "r") as f:
                data = f.read()
            load_machine(data)
            print(f"State machine loaded from {parsed_args.file}")
        except Exception as e:
            print(f"Failed to load state machine: {e}")
            return 1
        
    elif parsed_args.command == "visualize":
        result = export_visualization(
            format=parsed_args.format,
            file_path=parsed_args.output
        )
        if parsed_args.output:
            print(f"Visualization exported to {result}")
        else:
            print(result)
        
    elif parsed_args.command == "test":
        success = run_tests()
        if success:
            print("All tests passed.")
        else:
            print("Tests failed.")
            return 1
        
    elif parsed_args.command == "reset":
        reset_machine()
        print("State machine reset.")
        
    else:
        print("No command specified. Use --help for usage information.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())