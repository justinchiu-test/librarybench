# Game Developer CLI for State Machine
import os
import json
import random
import string

from .statemachine import StateMachine


def generate_id(length=6):
    """Generate a random string ID"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


def scaffold_machine(name):
    """
    Generate a new state machine scaffold file.
    
    Args:
        name: Name for the state machine
    
    Returns:
        str: Filename of the created scaffold
    """
    # Create a template file
    template = f"""# {name} State Machine
from game_developer.statemachine import StateMachine

def create_machine():
    '''Create a new state machine for {name}'''
    sm = StateMachine()
    
    # Define states and transitions
    sm.define_transition("start", None, "initial", "start")
    sm.define_transition("next", "initial", "middle", "next")
    sm.define_transition("finish", "middle", "final", "finish")
    
    # Set initial state
    sm.current_state = "initial"
    
    # Optional: define hooks
    sm.on_enter("final", lambda m, ev, t: print("Reached final state"))
    
    return sm

if __name__ == "__main__":
    # Example usage
    machine = create_machine()
    print(f"Initial state: {{machine.current_state}}")
    machine.trigger("next")
    print(f"Current state: {{machine.current_state}}")
"""
    
    # Save to file
    filename = f"{name.lower().replace(' ', '_')}_{generate_id()}.py"
    with open(filename, 'w') as f:
        f.write(template)
    
    return filename


def visualize_machine(json_file, output=None):
    """
    Generate a visualization for a state machine from a JSON file.
    
    Args:
        json_file: Path to JSON file containing state machine data
        output: Optional output file path
    
    Returns:
        str: Path to the generated visualization file
    """
    # Read JSON file
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Load machine
    machine = StateMachine.load_machine(data)
    
    # Generate output filename if not provided
    if output is None:
        base = os.path.splitext(json_file)[0]
        output = f"{base}.dot"
    
    # Generate visualization
    machine.export_visualization(file_path=output)
    
    return output