from vm_emulator.core.vm import VirtualMachine
from vm_emulator.core.program import Program
from vm_emulator.core.instruction import InstructionSet

# Create a VM instance
vm = VirtualMachine(num_processors=2, memory_size=100, random_seed=42)

# Create a simple program that adds two numbers and stores the result
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

# Start the VM
vm.start()

# Execute manually step by step
for i in range(20):  # Should complete in fewer steps
    # Get thread and processor information
    thread = vm.threads[thread_id]
    processor = None
    if thread.processor_id is not None:
        processor = vm.processors[thread.processor_id]
    
    # Print state before step
    print(f"Step {i} - Before:")
    print(f"  Thread PC: {thread.pc}, Processor PC: {processor.pc if processor else 'N/A'}")
    print(f"  Thread state: {thread.state}, Processor state: {processor.state if processor else 'N/A'}")
    print(f"  Registers: {thread.registers}")
    print(f"  Memory[30]: {vm.memory.memory[30]}")
    
    # Execute a step
    still_running = vm.step()
    
    # Print state after step
    print(f"Step {i} - After:")
    print(f"  Thread PC: {thread.pc}, Processor PC: {processor.pc if processor else 'N/A'}")
    print(f"  Thread state: {thread.state}, Processor state: {processor.state if processor else 'N/A'}")
    print(f"  Registers: {thread.registers}")
    print(f"  Memory[30]: {vm.memory.memory[30]}")
    print("="*80)
    
    if not still_running:
        print("VM terminated")
        break

# Print final state
print("\nFinal state:")
print(f"Memory[30] = {vm.memory.memory[30]}")
