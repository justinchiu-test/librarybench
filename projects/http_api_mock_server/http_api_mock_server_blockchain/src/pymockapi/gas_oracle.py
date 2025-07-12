from typing import Dict, List, Optional, Tuple, Any
from eth_utils import to_hex, to_int
import random
import time


class GasOracle:
    def __init__(self, base_fee: int = 1000000000):
        self.base_fee = base_fee
        self.priority_fees: List[int] = []
        self.max_priority_fee_history_size = 1000
        self.congestion_factor = 1.0
        self.last_update = time.time()
        
    def update_base_fee(self, parent_gas_used: int, parent_gas_limit: int, parent_base_fee: int) -> int:
        # EIP-1559 base fee calculation
        target_gas_used = parent_gas_limit // 2
        
        if parent_gas_used > target_gas_used:
            gas_delta = parent_gas_used - target_gas_used
            base_fee_delta = max(1, parent_base_fee * gas_delta // target_gas_used // 8)
            new_base_fee = min(parent_base_fee + base_fee_delta, 10**18)  # Cap at 1000 ETH
        elif parent_gas_used < target_gas_used:
            gas_delta = target_gas_used - parent_gas_used
            base_fee_delta = parent_base_fee * gas_delta // target_gas_used // 8
            new_base_fee = max(parent_base_fee - base_fee_delta, 1000000000)  # Floor at 1 gwei
        else:
            new_base_fee = parent_base_fee
            
        self.base_fee = new_base_fee
        return new_base_fee
        
    def estimate_gas(self, tx_data: Dict[str, Any]) -> int:
        # Base gas costs
        base_gas = 21000  # Standard transfer
        
        # Additional gas for contract interactions
        if tx_data.get("data") and tx_data["data"] != "0x":
            data_bytes = bytes.fromhex(tx_data["data"][2:])
            
            # Gas per byte: 4 for zero bytes, 16 for non-zero
            for byte in data_bytes:
                if byte == 0:
                    base_gas += 4
                else:
                    base_gas += 16
                    
            # Additional gas for contract execution (mock)
            base_gas += 10000  # Base contract execution
            
            # Simulate different operation costs
            if len(data_bytes) >= 4:
                selector = data_bytes[:4]
                selector_int = int.from_bytes(selector, byteorder='big')
                
                # Mock different gas costs based on function selector
                if selector_int % 10 == 0:  # Storage write operations
                    base_gas += 20000
                elif selector_int % 10 < 5:  # Storage read operations
                    base_gas += 2500
                else:  # Compute operations
                    base_gas += 5000
                    
        # Account creation
        if not tx_data.get("to"):
            base_gas += 32000
            
        # Apply congestion factor
        estimated_gas = int(base_gas * self.congestion_factor)
        
        # Add 10% buffer
        return int(estimated_gas * 1.1)
        
    def get_gas_price(self) -> int:
        # Legacy gas price = base fee + priority fee
        priority_fee = self.get_priority_fee()
        return self.base_fee + priority_fee
        
    def get_priority_fee(self, percentile: float = 50.0) -> int:
        if not self.priority_fees:
            # Default priority fees based on network conditions
            return int(1000000000 * self.congestion_factor)  # 1 gwei * congestion
            
        # Calculate percentile from historical priority fees
        sorted_fees = sorted(self.priority_fees)
        index = int((percentile / 100) * len(sorted_fees))
        index = min(index, len(sorted_fees) - 1)
        
        return sorted_fees[index]
        
    def add_transaction_priority_fee(self, priority_fee: int):
        self.priority_fees.append(priority_fee)
        
        # Maintain history size
        if len(self.priority_fees) > self.max_priority_fee_history_size:
            self.priority_fees.pop(0)
            
    def simulate_congestion(self):
        # Simulate network congestion changes
        current_time = time.time()
        if current_time - self.last_update > 60:  # Update every minute
            # Random walk for congestion factor
            change = random.uniform(-0.1, 0.1)
            self.congestion_factor = max(0.5, min(3.0, self.congestion_factor + change))
            self.last_update = current_time
            
    def get_fee_history(
        self,
        block_count: int,
        percentiles: List[float],
        base_fees: List[int],
        gas_used_ratios: List[float]
    ) -> Dict[str, List[Any]]:
        rewards = []
        
        for i, ratio in enumerate(gas_used_ratios):
            block_rewards = []
            
            for percentile in percentiles:
                # Simulate priority fees based on gas usage ratio
                if ratio > 0.9:  # High congestion
                    base_priority = 2000000000  # 2 gwei
                elif ratio > 0.7:  # Medium congestion
                    base_priority = 1000000000  # 1 gwei
                else:  # Low congestion
                    base_priority = 100000000  # 0.1 gwei
                    
                # Add variance based on percentile
                variance_factor = 1 + (percentile - 50) / 100
                priority_fee = int(base_priority * variance_factor * self.congestion_factor)
                
                block_rewards.append(to_hex(priority_fee))
                
            rewards.append(block_rewards)
            
        return {
            "baseFeePerGas": [to_hex(fee) for fee in base_fees],
            "gasUsedRatio": gas_used_ratios,
            "reward": rewards,
        }
        
    def get_eip1559_estimates(self) -> Dict[str, str]:
        # Get current fee estimates for different priority levels
        base_fee_hex = to_hex(self.base_fee)
        
        return {
            "baseFee": base_fee_hex,
            "low": {
                "maxPriorityFeePerGas": to_hex(self.get_priority_fee(10)),
                "maxFeePerGas": to_hex(self.base_fee + self.get_priority_fee(10)),
            },
            "medium": {
                "maxPriorityFeePerGas": to_hex(self.get_priority_fee(50)),
                "maxFeePerGas": to_hex(self.base_fee + self.get_priority_fee(50)),
            },
            "high": {
                "maxPriorityFeePerGas": to_hex(self.get_priority_fee(90)),
                "maxFeePerGas": to_hex(self.base_fee + self.get_priority_fee(90)),
            },
        }