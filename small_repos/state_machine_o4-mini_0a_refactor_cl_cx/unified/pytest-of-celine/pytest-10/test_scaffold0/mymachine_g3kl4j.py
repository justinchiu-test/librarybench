# mymachine State Machine
from game_developer.statemachine import StateMachine

def create_machine():
    '''Create a new state machine for mymachine'''
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
    print(f"Initial state: {machine.current_state}")
    machine.trigger("next")
    print(f"Current state: {machine.current_state}")
