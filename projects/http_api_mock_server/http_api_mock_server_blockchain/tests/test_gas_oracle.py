import pytest
from eth_utils import to_hex, to_int
from pymockapi.gas_oracle import GasOracle


class TestGasOracle:
    @pytest.fixture
    def gas_oracle(self):
        return GasOracle(base_fee=1000000000)  # 1 gwei
        
    def test_update_base_fee_increase(self, gas_oracle):
        # High gas usage should increase base fee
        parent_gas_used = 20000000  # 20M
        parent_gas_limit = 30000000  # 30M
        parent_base_fee = 1000000000  # 1 gwei
        
        new_base_fee = gas_oracle.update_base_fee(parent_gas_used, parent_gas_limit, parent_base_fee)
        
        assert new_base_fee > parent_base_fee
        assert gas_oracle.base_fee == new_base_fee
        
    def test_update_base_fee_decrease(self, gas_oracle):
        # Low gas usage should decrease base fee
        parent_gas_used = 5000000  # 5M
        parent_gas_limit = 30000000  # 30M
        parent_base_fee = 2000000000  # 2 gwei
        
        new_base_fee = gas_oracle.update_base_fee(parent_gas_used, parent_gas_limit, parent_base_fee)
        
        assert new_base_fee < parent_base_fee
        assert new_base_fee >= 1000000000  # Floor at 1 gwei
        
    def test_update_base_fee_stable(self, gas_oracle):
        # Exactly half gas usage should keep base fee stable
        parent_gas_used = 15000000  # 15M
        parent_gas_limit = 30000000  # 30M
        parent_base_fee = 1500000000  # 1.5 gwei
        
        new_base_fee = gas_oracle.update_base_fee(parent_gas_used, parent_gas_limit, parent_base_fee)
        
        assert new_base_fee == parent_base_fee
        
    def test_estimate_gas_simple_transfer(self, gas_oracle):
        tx_data = {
            "from": "0x" + "1" * 40,
            "to": "0x" + "2" * 40,
            "value": "0x1",
        }
        
        gas = gas_oracle.estimate_gas(tx_data)
        
        # Should be at least 21000 + 10% buffer
        assert gas >= 23100
        
    def test_estimate_gas_with_data(self, gas_oracle):
        tx_data = {
            "from": "0x" + "1" * 40,
            "to": "0x" + "2" * 40,
            "value": "0x0",
            "data": "0x" + "ff" * 100,  # 100 non-zero bytes
        }
        
        gas = gas_oracle.estimate_gas(tx_data)
        
        # Base 21000 + data cost + contract execution + buffer
        assert gas > 35000
        
    def test_estimate_gas_contract_creation(self, gas_oracle):
        tx_data = {
            "from": "0x" + "1" * 40,
            "value": "0x0",
            "data": "0x606060",
        }
        
        gas = gas_oracle.estimate_gas(tx_data)
        
        # Should include contract creation cost
        assert gas > 53000  # 21000 + 32000 + data
        
    def test_get_gas_price(self, gas_oracle):
        gas_price = gas_oracle.get_gas_price()
        
        assert gas_price >= gas_oracle.base_fee
        
    def test_get_priority_fee(self, gas_oracle):
        # Add some priority fees
        for i in range(10):
            gas_oracle.add_transaction_priority_fee((i + 1) * 100000000)
            
        # Get median (50th percentile)
        priority_fee = gas_oracle.get_priority_fee(50.0)
        
        assert priority_fee == 600000000  # 50th percentile of 10 items
        
        # Get high percentile
        high_priority = gas_oracle.get_priority_fee(90.0)
        assert high_priority > priority_fee
        
    def test_simulate_congestion(self, gas_oracle):
        initial_congestion = gas_oracle.congestion_factor
        
        # Simulate multiple times to see changes
        for _ in range(10):
            gas_oracle.simulate_congestion()
            
        # Congestion factor should be within bounds
        assert 0.5 <= gas_oracle.congestion_factor <= 3.0
        
    def test_get_fee_history(self, gas_oracle):
        block_count = 3
        percentiles = [25, 50, 75]
        base_fees = [1000000000, 1100000000, 1200000000]
        gas_used_ratios = [0.5, 0.8, 0.95]
        
        history = gas_oracle.get_fee_history(
            block_count, percentiles, base_fees, gas_used_ratios
        )
        
        assert len(history["baseFeePerGas"]) == 3
        assert len(history["gasUsedRatio"]) == 3
        assert len(history["reward"]) == 3
        
        # Higher gas usage should result in higher rewards
        for i, rewards in enumerate(history["reward"]):
            assert len(rewards) == 3  # One for each percentile
            if i < len(history["reward"]) - 1:
                # Compare with next block
                for j in range(len(percentiles)):
                    if gas_used_ratios[i] < gas_used_ratios[i + 1]:
                        assert to_int(hexstr=rewards[j]) <= to_int(hexstr=history["reward"][i + 1][j])
                        
    def test_get_eip1559_estimates(self, gas_oracle):
        estimates = gas_oracle.get_eip1559_estimates()
        
        assert "baseFee" in estimates
        assert "low" in estimates
        assert "medium" in estimates
        assert "high" in estimates
        
        # Verify structure
        for level in ["low", "medium", "high"]:
            assert "maxPriorityFeePerGas" in estimates[level]
            assert "maxFeePerGas" in estimates[level]
            
        # Verify ordering
        low_priority = to_int(hexstr=estimates["low"]["maxPriorityFeePerGas"])
        med_priority = to_int(hexstr=estimates["medium"]["maxPriorityFeePerGas"])
        high_priority = to_int(hexstr=estimates["high"]["maxPriorityFeePerGas"])
        
        assert low_priority <= med_priority <= high_priority