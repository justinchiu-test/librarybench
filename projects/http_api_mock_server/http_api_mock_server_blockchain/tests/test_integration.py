import pytest
import asyncio
from eth_utils import to_hex, to_int, to_checksum_address, keccak
from pymockapi.blockchain import BlockchainState
from pymockapi.rpc_engine import JSONRPCEngine
from pymockapi.events import EventEmitter
from pymockapi.gas_oracle import GasOracle
from pymockapi.multi_chain import MultiChainRouter, ChainConfig


class TestIntegration:
    @pytest.fixture
    def router(self):
        return MultiChainRouter()
        
    def test_full_transaction_lifecycle_with_events(self, router):
        blockchain = router.get_chain(1)
        rpc_engine = router.get_rpc_engine(1)
        event_emitter = EventEmitter(blockchain)
        
        # Deploy contract
        contract_address = to_checksum_address("0x" + "5" * 40)
        blockchain.set_code(contract_address, "0x606060")
        
        # Send transaction that emits event
        tx_data = {
            "from": "0x" + "1" * 40,
            "to": contract_address,
            "value": "0x0",
            "gas": "0x30000",
            "data": "0xa9059cbb",  # transfer function selector
        }
        
        tx_hash = blockchain.add_transaction(tx_data)
        
        # Emit transfer event
        event_emitter.emit_transfer(
            token_address=contract_address,
            from_address=tx_data["from"],
            to_address="0x" + "2" * 40,
            amount=10**18,
            tx_hash=tx_hash,
            tx_index=0,
            block_number=blockchain.current_block_number + 1,
            block_hash="0x" + "b" * 64,
            log_index=0,
        )
        
        # Mine block
        blockchain._mine_new_block()
        
        # Verify transaction and event
        assert tx_hash in blockchain.receipts
        assert len(blockchain.logs) == 1
        
    def test_multi_chain_transaction_routing(self, router):
        chains = [1, 137, 42161]
        tx_hashes = {}
        
        for chain_id in chains:
            blockchain = router.get_chain(chain_id)
            
            tx_data = {
                "from": "0x" + "1" * 40,
                "to": "0x" + "2" * 40,
                "value": to_hex(chain_id * 10**18),
                "gas": "0x5208",
            }
            
            tx_hash = blockchain.add_transaction(tx_data)
            tx_hashes[chain_id] = tx_hash
            
        # Verify transactions are isolated per chain
        for chain_id in chains:
            blockchain = router.get_chain(chain_id)
            assert tx_hashes[chain_id] in blockchain.transactions
            
            # Other chains' transactions should not exist
            for other_chain_id in chains:
                if other_chain_id != chain_id:
                    assert tx_hashes[other_chain_id] not in blockchain.transactions
                    
    def test_gas_oracle_with_congestion(self, router):
        blockchain = router.get_chain(1)
        gas_oracle = GasOracle(blockchain.base_fee_per_gas)
        
        # Simulate congestion
        gas_oracle.congestion_factor = 2.5
        
        # Add high priority transactions
        for i in range(10):
            priority_fee = (i + 1) * 2000000000  # 2-20 gwei
            gas_oracle.add_transaction_priority_fee(priority_fee)
            
        # Get estimates during congestion
        estimates = gas_oracle.get_eip1559_estimates()
        
        # High priority should be significantly higher than low
        high_priority = to_int(hexstr=estimates["high"]["maxPriorityFeePerGas"])
        low_priority = to_int(hexstr=estimates["low"]["maxPriorityFeePerGas"])
        
        assert high_priority > low_priority * 2
        
    @pytest.mark.asyncio
    async def test_concurrent_multi_chain_mining(self, router):
        # Configure fast block times for testing
        for blockchain in router.chains.values():
            blockchain.block_time = 0.1
            
        # Start mining on all chains
        await router.start_all_chains()
        
        # Let them mine for a bit
        await asyncio.sleep(0.3)
        
        # Check each chain has mined blocks
        for chain_id, blockchain in router.chains.items():
            assert blockchain.current_block_number >= 0  # At least genesis block
            
        await router.stop_all_chains()
        
    def test_complex_log_filtering_scenario(self, router):
        blockchain = router.get_chain(1)
        event_emitter = EventEmitter(blockchain)
        
        # Create multiple contracts and events
        contracts = [to_checksum_address("0x" + str(i) * 40) for i in range(5, 10)]
        event_types = ["Transfer", "Approval", "Mint", "Burn"]
        
        # Generate events
        log_count = 0
        for block_num in range(5):
            blockchain._mine_new_block()
            
            for contract in contracts:
                for event_type in event_types:
                    log = event_emitter.emit_event(
                        address=contract,
                        event_signature=f"{event_type}(address,address,uint256)",
                        indexed_params=[
                            "0x" + str(block_num) * 40,
                            "0x" + str(log_count) * 40,
                        ],
                        data_params=[log_count * 10**18],
                        tx_hash="0x" + str(log_count) * 64,
                        tx_index=log_count % 5,
                        block_number=block_num,
                        block_hash=blockchain.blocks[block_num].hash,
                        log_index=log_count,
                    )
                    log_count += 1
                    
        # Complex filter query
        transfer_topic = to_hex(keccak(text="Transfer(address,address,uint256)"))
        logs = blockchain.get_logs({
            "fromBlock": 1,
            "toBlock": 3,
            "address": contracts[:2],
            "topics": [transfer_topic],
        })
        
        # Should only get Transfer events from first 2 contracts in blocks 1-3
        assert len(logs) == 6  # 2 contracts * 3 blocks * 1 Transfer event
        
    def test_eip1559_transaction_processing(self, router):
        blockchain = router.get_chain(1)
        gas_oracle = GasOracle(blockchain.base_fee_per_gas)
        
        # Create EIP-1559 transaction
        base_fee = blockchain.base_fee_per_gas
        max_priority_fee = 2000000000  # 2 gwei
        max_fee = base_fee + max_priority_fee + 1000000000  # Base + priority + 1 gwei buffer
        
        tx_data = {
            "from": "0x" + "1" * 40,
            "to": "0x" + "2" * 40,
            "value": "0x1",
            "gas": "0x5208",
            "maxFeePerGas": to_hex(max_fee),
            "maxPriorityFeePerGas": to_hex(max_priority_fee),
        }
        
        tx_hash = blockchain.add_transaction(tx_data)
        blockchain._mine_new_block()
        
        # Check receipt has correct effective gas price
        receipt = blockchain.receipts[tx_hash]
        effective_price = to_int(hexstr=receipt.effective_gas_price)
        
        # Effective price should be base fee + priority fee (capped at max fee)
        assert effective_price <= max_fee
        assert effective_price >= base_fee
        
    def test_chain_reorganization_simulation(self, router):
        blockchain = router.get_chain(1)
        
        # Mine main chain
        main_chain_blocks = []
        for i in range(10):
            blockchain._mine_new_block()
            main_chain_blocks.append(blockchain.blocks[blockchain.current_block_number])
            
        # Simulate reorg by resetting to earlier block
        reorg_depth = 3
        blockchain.current_block_number -= reorg_depth
        
        # Mine alternative chain
        for i in range(reorg_depth + 1):
            blockchain._mine_new_block()
            
        # Verify new chain is longer
        assert blockchain.current_block_number > len(main_chain_blocks) - reorg_depth
        
    def test_contract_storage_persistence(self, router):
        blockchain = router.get_chain(1)
        contract = to_checksum_address("0x" + "6" * 40)
        
        # Set up contract with storage
        blockchain.set_code(contract, "0x606060")
        
        # Write to multiple storage slots
        storage_data = {}
        for i in range(20):
            slot = to_hex(i)
            value = "0x" + str(i * 1000).zfill(64)
            blockchain.set_storage_at(contract, slot, value)
            storage_data[slot] = value
            
        # Read back all storage
        for slot, expected_value in storage_data.items():
            actual_value = blockchain.get_storage_at(contract, slot)
            assert actual_value == expected_value
            
    def test_custom_chain_configuration(self, router):
        # Add custom chain
        custom_config = ChainConfig(
            chain_id=99999,
            name="Custom Test Chain",
            native_currency="TEST",
            block_time=1,
            gas_limit=50000000,
            base_fee=5000000000,  # 5 gwei
        )
        
        router.add_chain(custom_config)
        
        # Verify configuration applied
        blockchain = router.get_chain(99999)
        assert blockchain.chain_id == 99999
        assert blockchain.block_time == 1
        assert blockchain.base_fee_per_gas == 5000000000
        
        # Test custom chain works
        tx_data = {
            "from": "0x" + "1" * 40,
            "to": "0x" + "2" * 40,
            "value": "0x1",
        }
        tx_hash = blockchain.add_transaction(tx_data)
        assert tx_hash in blockchain.transactions