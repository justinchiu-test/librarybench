"""
CLI utilities for Game Developer state machine
"""
import os
from pathlib import Path
from .statemachine import StateMachine

def scaffold_machine(name):
    filename = f"{name}.py"
    content = f"def create_machine():\n    pass\n"
    with open(filename, 'w') as f:
        f.write(content)
    return filename

def visualize_machine(json_file):
    with open(json_file) as f:
        json_str = f.read()
    m = StateMachine.load_machine(json_str)
    p = Path(json_file)
    out = str(p.with_suffix('.dot'))
    m.export_visualization(out)
    return out