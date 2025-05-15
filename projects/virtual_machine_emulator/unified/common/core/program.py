"""
Program representation for virtual machine emulators.

This module provides a common program representation that can be
used by both the security-focused and parallel computing-focused VM implementations.
"""

from typing import Dict, List, Optional, Set, Tuple, Any, Union
import uuid

from common.core.instruction import Instruction, InstructionSet, InstructionType


class Program:
    """
    Representation of a program for the virtual machine.
    
    A program consists of instructions, data, and metadata for execution
    in a virtual machine.
    """
    
    def __init__(
        self,
        name: str,
        instructions: Optional[Dict[int, Instruction]] = None,
        data_segment: Optional[Dict[int, int]] = None,
        entry_point: int = 0,
        symbols: Optional[Dict[str, int]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a program.
        
        Args:
            name: Name of the program
            instructions: Dictionary mapping addresses to instructions
            data_segment: Dictionary mapping data addresses to values
            entry_point: Starting address for execution
            symbols: Dictionary mapping symbol names to addresses
            metadata: Additional metadata for the program
        """
        self.name = name
        self.instructions = instructions or {}
        self.data_segment = data_segment or {}
        self.entry_point = entry_point
        self.symbols = symbols or {}
        self.metadata = metadata or {}
        self.id = str(uuid.uuid4())
    
    def get_instruction(self, address: int) -> Optional[Instruction]:
        """
        Get the instruction at a specific address.
        
        Args:
            address: The address to look up
            
        Returns:
            The instruction at the address, or None if not found
        """
        return self.instructions.get(address)
    
    def get_data(self, address: int) -> Optional[int]:
        """
        Get the data value at a specific address.
        
        Args:
            address: The address to look up
            
        Returns:
            The data value at the address, or None if not found
        """
        return self.data_segment.get(address)
    
    def add_instruction(self, address: int, instruction: Instruction) -> None:
        """
        Add an instruction to the program.
        
        Args:
            address: The address to store the instruction
            instruction: The instruction to add
        """
        self.instructions[address] = instruction
    
    def add_data(self, address: int, value: int) -> None:
        """
        Add a data value to the program.
        
        Args:
            address: The address to store the data
            value: The data value to add
        """
        self.data_segment[address] = value
    
    def add_symbol(self, name: str, address: int) -> None:
        """
        Add a symbol to the program.
        
        Args:
            name: The symbol name
            address: The address associated with the symbol
        """
        self.symbols[name] = address
    
    def get_symbol_address(self, name: str) -> Optional[int]:
        """
        Get the address of a symbol.
        
        Args:
            name: The symbol name to look up
            
        Returns:
            The address of the symbol, or None if not found
        """
        return self.symbols.get(name)
    
    def get_symbol_name(self, address: int) -> Optional[str]:
        """
        Get the name of a symbol by address.
        
        Args:
            address: The address to look up
            
        Returns:
            The name of the symbol, or None if not found
        """
        for name, addr in self.symbols.items():
            if addr == address:
                return name
        return None
    
    def get_size(self) -> int:
        """
        Get the total size of the program.
        
        Returns:
            The total number of instructions and data entries
        """
        return len(self.instructions) + len(self.data_segment)
    
    def get_instruction_addresses(self) -> List[int]:
        """
        Get all instruction addresses in ascending order.
        
        Returns:
            List of instruction addresses
        """
        return sorted(self.instructions.keys())
    
    def get_data_addresses(self) -> List[int]:
        """
        Get all data addresses in ascending order.
        
        Returns:
            List of data addresses
        """
        return sorted(self.data_segment.keys())
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the program.
        
        Returns:
            Dictionary with program information
        """
        return {
            "id": self.id,
            "name": self.name,
            "entry_point": self.entry_point,
            "num_instructions": len(self.instructions),
            "num_data_entries": len(self.data_segment),
            "symbols": len(self.symbols),
            "metadata": self.metadata,
        }


class ProgramBuilder:
    """
    Builder for creating VM programs.
    
    This class helps construct program instances by providing
    convenient methods for adding instructions and data.
    """
    
    def __init__(
        self,
        name: str,
        instruction_set: Optional[InstructionSet] = None,
        entry_point: int = 0
    ):
        """
        Initialize a program builder.
        
        Args:
            name: Name of the program
            instruction_set: Instruction set to use for creating instructions
            entry_point: Starting address for the program
        """
        self.name = name
        self.instruction_set = instruction_set
        self.entry_point = entry_point
        self.instructions: Dict[int, Instruction] = {}
        self.data_segment: Dict[int, int] = {}
        self.symbols: Dict[str, int] = {}
        self.metadata: Dict[str, Any] = {}
        self.current_address = 0
    
    def set_current_address(self, address: int) -> 'ProgramBuilder':
        """
        Set the current address for adding instructions and data.
        
        Args:
            address: The new current address
            
        Returns:
            Self for method chaining
        """
        self.current_address = address
        return self
    
    def add_instruction(
        self,
        opcode: str,
        operands: List[Any],
        address: Optional[int] = None
    ) -> 'ProgramBuilder':
        """
        Add an instruction to the program.
        
        Args:
            opcode: The instruction opcode
            operands: List of operands for the instruction
            address: The address to store the instruction (uses current_address if None)
            
        Returns:
            Self for method chaining
        """
        if address is None:
            address = self.current_address
            self.current_address += 1
        
        if self.instruction_set:
            instruction = self.instruction_set.create_instruction(opcode, operands)
            if instruction is None:
                raise ValueError(f"Unknown instruction opcode: {opcode}")
        else:
            # Create a basic instruction without an instruction set
            from common.core.instruction import Instruction, InstructionType
            instruction = Instruction(
                opcode=opcode,
                type=InstructionType.COMPUTE,  # Default type
                operands=operands
            )
        
        self.instructions[address] = instruction
        return self
    
    def add_data(
        self,
        value: int,
        address: Optional[int] = None
    ) -> 'ProgramBuilder':
        """
        Add a data value to the program.
        
        Args:
            value: The data value to add
            address: The address to store the data (uses current_address if None)
            
        Returns:
            Self for method chaining
        """
        if address is None:
            address = self.current_address
            self.current_address += 1
        
        self.data_segment[address] = value
        return self
    
    def add_symbol(self, name: str, address: int) -> 'ProgramBuilder':
        """
        Add a symbol to the program.
        
        Args:
            name: The symbol name
            address: The address associated with the symbol
            
        Returns:
            Self for method chaining
        """
        self.symbols[name] = address
        return self
    
    def set_metadata(self, key: str, value: Any) -> 'ProgramBuilder':
        """
        Set a metadata value.
        
        Args:
            key: The metadata key
            value: The metadata value
            
        Returns:
            Self for method chaining
        """
        self.metadata[key] = value
        return self
    
    def set_entry_point(self, entry_point: int) -> 'ProgramBuilder':
        """
        Set the entry point for the program.
        
        Args:
            entry_point: The new entry point
            
        Returns:
            Self for method chaining
        """
        self.entry_point = entry_point
        return self
    
    def build(self) -> Program:
        """
        Build the program.
        
        Returns:
            The constructed Program instance
        """
        return Program(
            name=self.name,
            instructions=self.instructions,
            data_segment=self.data_segment,
            entry_point=self.entry_point,
            symbols=self.symbols,
            metadata=self.metadata
        )


def create_simple_program(
    name: str,
    instructions: List[Tuple[str, List[Any]]],
    data: Optional[Dict[int, int]] = None,
    entry_point: int = 0
) -> Program:
    """
    Create a simple program from a list of instructions.
    
    Args:
        name: Name of the program
        instructions: List of (opcode, operands) tuples
        data: Dictionary mapping data addresses to values
        entry_point: Starting address for the program
        
    Returns:
        A Program instance
    """
    builder = ProgramBuilder(name, entry_point=entry_point)
    
    # Add instructions
    for i, (opcode, operands) in enumerate(instructions):
        builder.add_instruction(opcode, operands, i)
    
    # Add data
    if data:
        for address, value in data.items():
            builder.add_data(value, address)
    
    return builder.build()