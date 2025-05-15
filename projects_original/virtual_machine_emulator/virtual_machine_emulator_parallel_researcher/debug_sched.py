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

print("==== Initial state ====")
print("Thread ID:", thread_id)
print("Thread PC:", vm.threads[thread_id].pc)
print("Thread state:", vm.threads[thread_id].state)
print("Ready queue:", vm.ready_queue)

# Start the VM explicitly
vm.start()

# Call the scheduler directly to see what happens
print("\n==== After scheduling ====")
vm._schedule_threads()
print("Thread ID:", thread_id)
print("Thread PC:", vm.threads[thread_id].pc)
print("Thread state:", vm.threads[thread_id].state)
print("Thread processor:", vm.threads[thread_id].processor_id)
print("Ready queue:", vm.ready_queue)

for i, processor in enumerate(vm.processors):
    print(f"Processor {i}:")
    print(f"  Thread ID: {processor.current_thread_id}")
    print(f"  PC: {processor.pc}")
    print(f"  State: {processor.state}")
    print(f"  Stall cycles: {processor.stall_cycles}")
