from vm_emulator.core.vm import VirtualMachine
from vm_emulator.core.program import Program
from vm_emulator.core.instruction import InstructionSet

# Create a VM instance
vm = VirtualMachine(num_processors=2, memory_size=100, random_seed=42)

# Create the test program
instructions = [
    InstructionSet.create_instruction("LOAD", ["R0", 10]),  # Load value 10 into R0
    InstructionSet.create_instruction("LOAD", ["R1", 20]),  # Load value 20 into R1
    InstructionSet.create_instruction("ADD", ["R2", "R0", "R1"]),  # R2 = R0 + R1
    InstructionSet.create_instruction("STORE", ["R2", 30]),  # Store R2 to memory address 30
    InstructionSet.create_instruction("HALT", []),  # Halt the thread
]

program = Program(
    name="add_program",
    instructions=instructions,
    entry_point=0,
)

# Load the program
program_id = vm.load_program(program)

# Create a thread to execute the program
thread_id = vm.create_thread(program_id)

print("Before execution, memory[30] =", vm.memory.memory[30])

# Run step by step for debugging
print("Running step by step:")
for i in range(20):  # Should complete in fewer steps
    still_running = vm.step()
    thread = vm.threads[thread_id]
    if thread.program.get_instruction(thread.pc) is not None:
        print(f"Step {i}: PC={thread.pc}, Instruction={thread.program.get_instruction(thread.pc)}")
        # Print all registers
        print(f"  Registers: {thread.registers}")
        # Print memory value
        print(f"  Memory[30] = {vm.memory.memory[30]}")
    else:
        print(f"Step {i}: Thread terminated")
    
    if not still_running:
        print("VM terminated")
        break

print("\nAfter execution, memory[30] =", vm.memory.memory[30])
print("Execution trace:")
for event in vm.execution_trace:
    if event.get("event") in ["memory_write", "memory_read"]:
        print(f"{event['timestamp']}: {event['event']} addr={event['address']} value={event.get('value')}")
