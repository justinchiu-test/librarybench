"""
Privilege management extension for VM security.

This module provides mechanisms for managing and enforcing privilege levels
and access controls within the virtual machine.
"""

from __future__ import annotations
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Union, Any, Callable

from common.core.processor import PrivilegeLevel


class PrivilegeViolationEvent:
    """Records a privilege violation event."""
    
    def __init__(
        self,
        instruction: str,
        address: int,
        required_level: PrivilegeLevel,
        current_level: PrivilegeLevel,
        context: Dict[str, Any] = None,
    ):
        """
        Initialize the privilege violation event.
        
        Args:
            instruction: The instruction that caused the violation
            address: Memory address of the instruction
            required_level: Required privilege level
            current_level: Current privilege level
            context: Additional context for the event
        """
        self.instruction = instruction
        self.address = address
        self.required_level = required_level
        self.current_level = current_level
        self.context = context or {}
    
    def __str__(self) -> str:
        return (
            f"Privilege violation at 0x{self.address:08x}: "
            f"{self.instruction} requires {self.required_level.name}, "
            f"current level is {self.current_level.name}"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the privilege violation to a dictionary."""
        return {
            "instruction": self.instruction,
            "address": self.address,
            "required_level": self.required_level.name,
            "current_level": self.current_level.name,
            "context": self.context,
        }


class ProtectionKey:
    """Memory protection key for fine-grained access control."""
    
    def __init__(
        self,
        key_id: int,
        allow_read: bool = True,
        allow_write: bool = False,
        allow_execute: bool = False,
        restricted: bool = True,
    ):
        """
        Initialize the protection key.
        
        Args:
            key_id: Unique identifier for the key
            allow_read: Whether to allow read access
            allow_write: Whether to allow write access
            allow_execute: Whether to allow execute access
            restricted: Whether the key is restricted to higher privilege levels
        """
        self.key_id = key_id
        self.allow_read = allow_read
        self.allow_write = allow_write
        self.allow_execute = allow_execute
        self.restricted = restricted
    
    def check_access(
        self,
        access_type: str,
        level: PrivilegeLevel
    ) -> bool:
        """
        Check if access is allowed with this key.
        
        Args:
            access_type: Type of access (read, write, execute)
            level: Current privilege level
            
        Returns:
            Whether access is allowed
        """
        # Restricted keys require supervisor or kernel privilege
        if self.restricted and level == PrivilegeLevel.USER:
            return False
        
        # Check access type
        if access_type == "read":
            return self.allow_read
        elif access_type == "write":
            return self.allow_write
        elif access_type == "execute":
            return self.allow_execute
        else:
            return False


class PrivilegeManager:
    """
    Manages privilege levels and transitions within the VM.
    
    This class provides mechanisms for enforcing privilege restrictions,
    tracking privilege changes, and detecting privilege violations.
    """
    
    def __init__(self):
        """Initialize the privilege manager."""
        self.privilege_changes: List[Dict[str, Any]] = []
        self.protection_keys: Dict[int, ProtectionKey] = {}
        self.violations: List[PrivilegeViolationEvent] = []
    
    def validate_transition(
        self,
        from_level: PrivilegeLevel,
        to_level: PrivilegeLevel,
        instruction: str,
        address: int,
        context: Dict[str, Any] = None
    ) -> bool:
        """
        Validate a privilege level transition.
        
        Args:
            from_level: Current privilege level
            to_level: Target privilege level
            instruction: Instruction causing the transition
            address: Address of the instruction
            context: Additional context
            
        Returns:
            Whether the transition is allowed
        """
        # Record the transition attempt
        transition = {
            "from_level": from_level.name,
            "to_level": to_level.name,
            "instruction": instruction,
            "address": address,
            "context": context or {},
        }
        
        # Rules for privilege transitions:
        # 1. Higher privilege levels can transition to any level
        # 2. Lower privilege levels can only lower their privilege further
        # 3. Lowering privilege is always allowed
        # 4. Only KERNEL level can elevate to KERNEL
        
        valid = True
        
        # Check elevation
        if to_level.value > from_level.value:
            # Attempting to elevate privilege
            if to_level == PrivilegeLevel.KERNEL and from_level != PrivilegeLevel.KERNEL:
                # Only KERNEL can elevate to KERNEL
                valid = False
                
            # SUPERVISOR can only be reached from KERNEL or SUPERVISOR
            if to_level == PrivilegeLevel.SUPERVISOR and from_level == PrivilegeLevel.USER:
                # Only SUPERVISOR or KERNEL can elevate to SUPERVISOR
                valid = False
        
        # Check special cases from context
        if context and context.get("syscall"):
            # Syscalls can temporarily elevate privilege from USER to SUPERVISOR
            if from_level == PrivilegeLevel.USER and to_level == PrivilegeLevel.SUPERVISOR:
                valid = True
        
        # Record the result
        transition["valid"] = valid
        self.privilege_changes.append(transition)
        
        # Record violation if invalid
        if not valid:
            violation = PrivilegeViolationEvent(
                instruction=instruction,
                address=address,
                required_level=PrivilegeLevel.KERNEL if to_level == PrivilegeLevel.KERNEL else PrivilegeLevel.SUPERVISOR,
                current_level=from_level,
                context=context,
            )
            self.violations.append(violation)
        
        return valid
    
    def register_protection_key(self, key: ProtectionKey) -> None:
        """
        Register a protection key.
        
        Args:
            key: Protection key to register
        """
        self.protection_keys[key.key_id] = key
    
    def check_key_access(
        self,
        key_id: int,
        access_type: str,
        level: PrivilegeLevel
    ) -> bool:
        """
        Check if a protection key allows the specified access.
        
        Args:
            key_id: Protection key ID
            access_type: Type of access (read, write, execute)
            level: Current privilege level
            
        Returns:
            Whether access is allowed
        """
        # KERNEL level bypasses protection keys
        if level == PrivilegeLevel.KERNEL:
            return True
        
        # Check if the key exists
        if key_id not in self.protection_keys:
            return False
        
        # Check access with the key
        return self.protection_keys[key_id].check_access(access_type, level)
    
    def get_privilege_changes(self) -> List[Dict[str, Any]]:
        """
        Get all recorded privilege changes.
        
        Returns:
            List of privilege change records
        """
        return self.privilege_changes
    
    def get_violations(self) -> List[PrivilegeViolationEvent]:
        """
        Get all recorded privilege violations.
        
        Returns:
            List of privilege violation events
        """
        return self.violations
    
    def reset(self) -> None:
        """Reset the privilege manager state."""
        self.privilege_changes = []
        self.violations = []
        # Keep protection keys