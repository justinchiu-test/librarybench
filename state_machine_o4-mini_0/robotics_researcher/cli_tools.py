import json
from gait_controller import GaitController

def scaffold_gait_machine() -> dict:
    return {
        "states": ["idle", "walk", "stop_gait"],
        "transitions": [
            {"name": "start_walk", "from": "idle", "to": "walk"},
            {"name": "stop_gait", "from": "walk", "to": "stop_gait"}
        ]
    }

def run_step_simulation(actions: list) -> list:
    logs = []
    for step, act in enumerate(actions):
        logs.append(f"Step {step}: {act}")
    return logs

def export_timing_diagram(actions: list) -> str:
    return json.dumps({"timing": actions})
