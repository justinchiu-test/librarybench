"""
Privilege management for the virtual machine emulator.

This module provides privilege management and access control:
- Privilege level management
- Protected mode transitions
- Access control with protection keys
"""

from enum import Enum, auto, IntEnum
from typing import Dict, List, Optional, Set, Tuple, Union, Any, Callable

from common.core.processor import PrivilegeLevel as BasePrivilegeLevel
from common.core.memory import MemorySystem, MemorySegment, MemoryPermission
from common.core.exceptions import PrivilegeViolationException


# Re-export the base privilege levels
PrivilegeLevel = BasePrivilegeLevel


class ProtectionDomain(IntEnum):
    """Protection domains for memory protection keys."""
    DOMAIN_0 = 0
    DOMAIN_1 = 1
    DOMAIN_2 = 2
    DOMAIN_3 = 3
    DOMAIN_4 = 4
    DOMAIN_5 = 5
    DOMAIN_6 = 6
    DOMAIN_7 = 7
    DOMAIN_8 = 8
    DOMAIN_9 = 9
    DOMAIN_10 = 10
    DOMAIN_11 = 11
    DOMAIN_12 = 12
    DOMAIN_13 = 13
    DOMAIN_14 = 14
    DOMAIN_15 = 15


class PrivilegeTransition(Enum):
    """Types of privilege level transitions."""
    ELEVATION = auto()     # Increasing privilege level
    DEMOTION = auto()      # Decreasing privilege level
    SAME_LEVEL = auto()    # Same privilege level
    INVALID = auto()       # Invalid transition


class PrivilegeManager:
    """
    Manages security privilege levels and transitions.
    
    This manager enforces rules for privilege transitions and
    provides a way to monitor and restrict privilege operations.
    """
    
    def __init__(self, initial_level: PrivilegeLevel = PrivilegeLevel.USER):
        """
        Initialize the privilege manager.
        
        Args:
            initial_level: Initial privilege level
        """
        self.current_level = initial_level
        self.transition_history: List[Dict[str, Any]] = []
        
        # Transition permissions matrix
        # This controls which privilege levels can be transitioned to from each level
        self.transition_permissions: Dict[PrivilegeLevel, Set[PrivilegeLevel]] = {
            PrivilegeLevel.USER: {PrivilegeLevel.USER},              # User can only stay user
            PrivilegeLevel.SUPERVISOR: {                             # Supervisor can go to user or stay
                PrivilegeLevel.USER, 
                PrivilegeLevel.SUPERVISOR
            },
            PrivilegeLevel.KERNEL: {                                 # Kernel can go anywhere
                PrivilegeLevel.USER, 
                PrivilegeLevel.SUPERVISOR, 
                PrivilegeLevel.KERNEL
            },
        }
        
        # Special transitions that require syscalls or other mechanisms
        self.special_transitions: Dict[Tuple[PrivilegeLevel, PrivilegeLevel], str] = {
            (PrivilegeLevel.USER, PrivilegeLevel.SUPERVISOR): "syscall",
            (PrivilegeLevel.USER, PrivilegeLevel.KERNEL): "interrupt",
            (PrivilegeLevel.SUPERVISOR, PrivilegeLevel.KERNEL): "elevate",
        }
    
    def get_transition_type(
        self,
        from_level: PrivilegeLevel,
        to_level: PrivilegeLevel
    ) -> PrivilegeTransition:
        """
        Get the type of transition between privilege levels.
        
        Args:
            from_level: Starting privilege level
            to_level: Target privilege level
            
        Returns:
            The transition type
        """
        if from_level.value < to_level.value:
            return PrivilegeTransition.ELEVATION
        elif from_level.value > to_level.value:
            return PrivilegeTransition.DEMOTION
        else:
            return PrivilegeTransition.SAME_LEVEL
    
    def check_transition_permission(
        self,
        from_level: PrivilegeLevel,
        to_level: PrivilegeLevel,
        mechanism: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Check if a privilege transition is permitted.
        
        Args:
            from_level: Starting privilege level
            to_level: Target privilege level
            mechanism: Transition mechanism (e.g., syscall, interrupt)
            
        Returns:
            (is_allowed, reason) tuple
        """
        # Check if target level is in allowed transitions
        if to_level not in self.transition_permissions.get(from_level, set()):
            return False, f"Transition from {from_level.name} to {to_level.name} is not allowed"
        
        # Check if this is a special transition requiring a specific mechanism
        transition_key = (from_level, to_level)
        if transition_key in self.special_transitions:
            required_mechanism = self.special_transitions[transition_key]
            if mechanism != required_mechanism:
                return False, f"Transition requires mechanism '{required_mechanism}', got '{mechanism}'"
        
        return True, "Transition allowed"
    
    def transition_level(
        self,
        to_level: PrivilegeLevel,
        mechanism: Optional[str] = None,
        context: Dict[str, Any] = None
    ) -> Tuple[bool, str]:
        """
        Attempt to transition to a new privilege level.
        
        Args:
            to_level: Target privilege level
            mechanism: Transition mechanism
            context: Additional context information
            
        Returns:
            (success, message) tuple
        """
        from_level = self.current_level
        
        # Check if transition is allowed
        allowed, reason = self.check_transition_permission(from_level, to_level, mechanism)
        if not allowed:
            return False, reason
        
        # Record the transition
        transition_type = self.get_transition_type(from_level, to_level)
        
        transition_record = {
            "from_level": from_level,
            "to_level": to_level,
            "transition_type": transition_type,
            "mechanism": mechanism,
            "context": context or {},
            "success": allowed,
        }
        
        self.transition_history.append(transition_record)
        
        # Update current level if allowed
        if allowed:
            self.current_level = to_level
        
        return allowed, reason
    
    def get_transition_history(self) -> List[Dict[str, Any]]:
        """
        Get the privilege transition history.
        
        Returns:
            List of transition records
        """
        return self.transition_history


class ProtectionKeyManager:
    """
    Manages protection keys for memory isolation.
    
    Protection keys provide a way to restrict memory access based on
    domains, independent of the memory permission system.
    """
    
    def __init__(self, domain_count: int = 16):
        """
        Initialize the protection key manager.
        
        Args:
            domain_count: Number of protection domains
        """
        self.domain_count = domain_count
        
        # Domain to permission mapping (read, write)
        self.domain_permissions: Dict[int, Tuple[bool, bool]] = {
            domain: (True, True) for domain in range(domain_count)
        }
        
        # Segment to domain mapping
        self.segment_domains: Dict[MemorySegment, int] = {}
        
        # Active protection key for current context
        self.active_keys: Set[int] = set()
    
    def set_domain_permissions(
        self,
        domain: int,
        can_read: bool,
        can_write: bool
    ) -> bool:
        """
        Set permissions for a protection domain.
        
        Args:
            domain: Protection domain
            can_read: Whether read access is allowed
            can_write: Whether write access is allowed
            
        Returns:
            True if successful, False otherwise
        """
        if domain < 0 or domain >= self.domain_count:
            return False
        
        self.domain_permissions[domain] = (can_read, can_write)
        return True
    
    def assign_segment_domain(
        self,
        segment: MemorySegment,
        domain: int
    ) -> bool:
        """
        Assign a segment to a protection domain.
        
        Args:
            segment: Memory segment
            domain: Protection domain
            
        Returns:
            True if successful, False otherwise
        """
        if domain < 0 or domain >= self.domain_count:
            return False
        
        self.segment_domains[segment] = domain
        return True
    
    def set_active_keys(self, keys: Set[int]) -> None:
        """
        Set the active protection keys.
        
        Args:
            keys: Set of protection keys
        """
        self.active_keys = {key for key in keys if 0 <= key < self.domain_count}
    
    def add_active_key(self, key: int) -> bool:
        """
        Add a protection key to the active set.
        
        Args:
            key: Protection key to add
            
        Returns:
            True if successful, False otherwise
        """
        if key < 0 or key >= self.domain_count:
            return False
        
        self.active_keys.add(key)
        return True
    
    def remove_active_key(self, key: int) -> bool:
        """
        Remove a protection key from the active set.
        
        Args:
            key: Protection key to remove
            
        Returns:
            True if successful, False otherwise
        """
        if key not in self.active_keys:
            return False
        
        self.active_keys.remove(key)
        return True
    
    def check_access(
        self,
        segment: MemorySegment,
        is_write: bool
    ) -> bool:
        """
        Check if access to a segment is allowed based on protection keys.
        
        Args:
            segment: Memory segment
            is_write: Whether this is a write access
            
        Returns:
            True if access is allowed, False otherwise
        """
        # If segment is not assigned to a domain, default allow
        if segment not in self.segment_domains:
            return True
        
        domain = self.segment_domains[segment]
        
        # If domain is in active keys, check specific permission
        if domain in self.active_keys:
            can_read, can_write = self.domain_permissions[domain]
            
            if is_write:
                return can_write
            else:
                return can_read
        
        # Default deny if domain is not in active keys
        return False


class SecureMode(Enum):
    """Secure execution modes for the VM."""
    REAL = auto()           # No protection, direct access
    PROTECTED = auto()      # Basic memory protection
    VIRTUAL = auto()        # Virtual memory protection
    SECURE = auto()         # Full security features
    ENCLAVE = auto()        # Isolated trusted execution


class SecureModeManager:
    """
    Manages secure execution modes for the VM.
    
    This class allows transitioning between different security
    modes with varying protection features.
    """
    
    def __init__(self, memory: MemorySystem, initial_mode: SecureMode = SecureMode.PROTECTED):
        """
        Initialize the secure mode manager.
        
        Args:
            memory: Memory system
            initial_mode: Initial secure mode
        """
        self.memory = memory
        self.current_mode = initial_mode
        self.transition_history: List[Dict[str, Any]] = []
        
        # Protection features enabled for each mode
        self.mode_features: Dict[SecureMode, Dict[str, bool]] = {
            SecureMode.REAL: {
                "protection_checks": False,
                "privilege_checks": False,
                "segment_limits": False,
                "paging": False,
                "dep": False,
                "aslr": False,
                "protection_keys": False,
            },
            SecureMode.PROTECTED: {
                "protection_checks": True,
                "privilege_checks": True,
                "segment_limits": True,
                "paging": False,
                "dep": True,
                "aslr": False,
                "protection_keys": False,
            },
            SecureMode.VIRTUAL: {
                "protection_checks": True,
                "privilege_checks": True,
                "segment_limits": True,
                "paging": True,
                "dep": True,
                "aslr": True,
                "protection_keys": False,
            },
            SecureMode.SECURE: {
                "protection_checks": True,
                "privilege_checks": True,
                "segment_limits": True,
                "paging": True,
                "dep": True,
                "aslr": True,
                "protection_keys": True,
            },
            SecureMode.ENCLAVE: {
                "protection_checks": True,
                "privilege_checks": True,
                "segment_limits": True,
                "paging": True,
                "dep": True,
                "aslr": True,
                "protection_keys": True,
                "enclave": True,
            },
        }
        
        # Apply initial mode features
        self._apply_mode_features(self.current_mode)
    
    def _apply_mode_features(self, mode: SecureMode) -> None:
        """
        Apply security features for a specific mode.
        
        Args:
            mode: Secure mode to apply
        """
        features = self.mode_features.get(mode, {})
        
        # Apply features to memory system
        if hasattr(self.memory, "enable_dep"):
            self.memory.enable_dep = features.get("dep", False)
    
    def transition_mode(
        self,
        target_mode: SecureMode,
        privilege_level: PrivilegeLevel,
        context: Dict[str, Any] = None
    ) -> Tuple[bool, str]:
        """
        Transition to a new secure mode.
        
        Args:
            target_mode: Target secure mode
            privilege_level: Current privilege level
            context: Additional context information
            
        Returns:
            (success, message) tuple
        """
        # Check privilege level - higher modes require higher privileges
        min_privilege = {
            SecureMode.REAL: PrivilegeLevel.USER,
            SecureMode.PROTECTED: PrivilegeLevel.USER,
            SecureMode.VIRTUAL: PrivilegeLevel.SUPERVISOR,
            SecureMode.SECURE: PrivilegeLevel.SUPERVISOR,
            SecureMode.ENCLAVE: PrivilegeLevel.KERNEL,
        }
        
        required_privilege = min_privilege.get(target_mode, PrivilegeLevel.KERNEL)
        
        if privilege_level.value < required_privilege.value:
            return False, (f"Insufficient privilege: {privilege_level.name} "
                          f"(required: {required_privilege.name})")
        
        # Record the transition
        transition = {
            "from_mode": self.current_mode,
            "to_mode": target_mode,
            "privilege_level": privilege_level,
            "context": context or {},
            "timestamp": 0,  # Would ideally use system time here
        }
        
        self.transition_history.append(transition)
        
        # Apply new mode features
        previous_mode = self.current_mode
        self.current_mode = target_mode
        self._apply_mode_features(target_mode)
        
        return True, f"Transitioned from {previous_mode.name} to {target_mode.name}"
    
    def get_current_features(self) -> Dict[str, bool]:
        """
        Get the security features of the current mode.
        
        Returns:
            Dictionary of enabled security features
        """
        return self.mode_features.get(self.current_mode, {})
    
    def is_feature_enabled(self, feature: str) -> bool:
        """
        Check if a specific security feature is enabled.
        
        Args:
            feature: Feature name
            
        Returns:
            True if the feature is enabled, False otherwise
        """
        return self.get_current_features().get(feature, False)