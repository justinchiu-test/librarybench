import pytest
import asyncio
from eth_utils import to_hex, to_int, to_checksum_address, keccak
from pymockapi.blockchain import BlockchainState
from pymockapi.models import Transaction, Log


class TestBlockchainAdvanced:
    @pytest.fixture
    def blockchain(self):
        return BlockchainState(chain_id=1)
        
    def test_multiple_transactions_same_account(self, blockchain):
        address = "0x" + "1" * 40
        
        # Add multiple transactions from same account
        tx_hashes = []
        for i in range(5):
            tx_data = {
                "from": address,
                "to": "0x" + str(i) * 40,
                "value": to_hex(i * 10**18),
                "gas": "0x5208",
            }
            tx_hash = blockchain.add_transaction(tx_data)
            tx_hashes.append(tx_hash)
            
        # Check nonce incremented correctly
        assert blockchain.get_nonce(address) == 5
        
        # Check all transactions are pending
        assert len(blockchain.pending_transactions) == 5
        
    def test_transaction_with_max_gas(self, blockchain):
        tx_data = {
            "from": "0x" + "1" * 40,
            "to": "0x" + "2" * 40,
            "value": "0x0",
            "gas": "0x1c9c380",  # Max gas limit
        }
        
        tx_hash = blockchain.add_transaction(tx_data)
        tx = blockchain.transactions[tx_hash]
        assert tx.gas == "0x1c9c380"
        
    def test_contract_creation_transaction(self, blockchain):
        tx_data = {
            "from": "0x" + "1" * 40,
            "to": None,  # Contract creation
            "value": "0x0",
            "gas": "0x100000",
            "data": "0x606060",  # Mock bytecode
        }
        
        tx_hash = blockchain.add_transaction(tx_data)
        tx = blockchain.transactions[tx_hash]
        assert tx.to_address is None
        assert tx.input == "0x606060"
        
    def test_eip1559_transaction(self, blockchain):
        tx_data = {
            "from": "0x" + "1" * 40,
            "to": "0x" + "2" * 40,
            "value": "0x1",
            "gas": "0x5208",
            "maxFeePerGas": "0x4a817c800",
            "maxPriorityFeePerGas": "0x3b9aca00",
        }
        
        tx_hash = blockchain.add_transaction(tx_data)
        tx = blockchain.transactions[tx_hash]
        assert tx.max_fee_per_gas == "0x4a817c800"
        assert tx.max_priority_fee_per_gas == "0x3b9aca00"
        assert tx.type == "0x2"
        
    def test_legacy_transaction(self, blockchain):
        tx_data = {
            "from": "0x" + "1" * 40,
            "to": "0x" + "2" * 40,
            "value": "0x1",
            "gas": "0x5208",
            "gasPrice": "0x3b9aca00",
        }
        
        tx_hash = blockchain.add_transaction(tx_data)
        tx = blockchain.transactions[tx_hash]
        assert tx.gas_price == "0x3b9aca00"
        
    def test_block_gas_limit_enforcement(self, blockchain):
        # Fill block with transactions
        for i in range(100):
            tx_data = {
                "from": "0x" + str(i % 10) * 40,
                "to": "0x" + str((i + 1) % 10) * 40,
                "value": "0x0",
                "gas": "0x5208",
            }
            blockchain.add_transaction(tx_data)
            
        # Mine block
        blockchain._mine_new_block()
        
        # Check gas limit was respected
        block = blockchain.blocks[1]
        assert to_int(hexstr=block.gas_used) <= to_int(hexstr=block.gas_limit)
        
    def test_balance_updates_after_mining(self, blockchain):
        from_address = "0x" + "1" * 40
        to_address = "0x" + "2" * 40
        
        # Set initial balance
        blockchain.set_balance(from_address, 10**20)  # 100 ETH
        
        # Add transaction
        tx_data = {
            "from": from_address,
            "to": to_address,
            "value": to_hex(10**18),  # 1 ETH
            "gas": "0x5208",
        }
        blockchain.add_transaction(tx_data)
        
        # Balance should remain same until mined
        assert to_int(hexstr=blockchain.get_balance(from_address)) == 10**20
        
    def test_storage_operations(self, blockchain):
        address = "0x" + "1" * 40
        
        # Test multiple storage slots
        for i in range(10):
            position = to_hex(i)
            value = "0x" + str(i) * 64
            blockchain.set_storage_at(address, position, value)
            assert blockchain.get_storage_at(address, position) == value
            
    def test_block_timestamp_progression(self, blockchain):
        import time
        timestamps = []
        
        for _ in range(3):
            blockchain._mine_new_block()
            block = blockchain.blocks[blockchain.current_block_number]
            timestamps.append(block.timestamp)
            time.sleep(0.01)  # Small delay to ensure timestamp changes
            
        # Timestamps should increase or be equal (if mined very quickly)
        for i in range(1, len(timestamps)):
            assert timestamps[i] >= timestamps[i-1]
            
    def test_block_hash_uniqueness(self, blockchain):
        hashes = set()
        
        for _ in range(10):
            blockchain._mine_new_block()
            block = blockchain.blocks[blockchain.current_block_number]
            assert block.hash not in hashes
            hashes.add(block.hash)
            
    def test_get_logs_with_multiple_addresses(self, blockchain):
        addresses = [to_checksum_address("0x" + str(i) * 40) for i in range(5)]
        
        # Add logs for different addresses
        for i, address in enumerate(addresses):
            for j in range(3):
                log = Log(
                    address=address,
                    topics=["0x" + "a" * 64],
                    data="0x" + str(i) + str(j),
                    block_number=i,
                    transaction_hash="0x" + str(i) + str(j) * 63,
                    transaction_index=j,
                    block_hash="0x" + "b" * 64,
                    log_index=i * 3 + j,
                )
                blockchain.add_log(log)
                
        # Filter by multiple addresses
        logs = blockchain.get_logs({
            "address": addresses[:3],
            "fromBlock": 0,
            "toBlock": 10
        })
        assert len(logs) == 9  # 3 addresses * 3 logs each
        
    def test_get_logs_complex_topic_filtering(self, blockchain):
        # Add logs with different topic combinations
        test_cases = [
            (["0x" + "a" * 64], "match_single"),
            (["0x" + "a" * 64, "0x" + "b" * 64], "match_double"),
            (["0x" + "a" * 64, "0x" + "c" * 64], "match_mixed"),
            (["0x" + "d" * 64], "no_match"),
        ]
        
        for i, (topics, data) in enumerate(test_cases):
            log = Log(
                address=to_checksum_address("0x" + "1" * 40),
                topics=topics,
                data="0x" + data.encode().hex(),
                block_number=i,
                transaction_hash="0x" + str(i) * 64,
                transaction_index=0,
                block_hash="0x" + "b" * 64,
                log_index=i,
            )
            blockchain.add_log(log)
            
        # Filter with just first topic
        logs = blockchain.get_logs({
            "topics": ["0x" + "a" * 64],  # First topic must match
            "fromBlock": 0,
            "toBlock": 10
        })
        assert len(logs) == 3  # Should match first three logs with topic "a"
        
    def test_transaction_receipt_generation(self, blockchain):
        # Add transaction with data
        tx_data = {
            "from": "0x" + "1" * 40,
            "to": None,  # Contract creation
            "value": "0x0",
            "gas": "0x100000",
            "data": "0x606060",
        }
        
        tx_hash = blockchain.add_transaction(tx_data)
        blockchain._mine_new_block()
        
        receipt = blockchain.receipts[tx_hash]
        assert receipt.contract_address is not None
        assert receipt.transaction_hash == tx_hash
        assert receipt.status == "0x1"
        
    @pytest.mark.asyncio
    async def test_concurrent_transaction_additions(self, blockchain):
        async def add_transactions(start_idx):
            for i in range(10):
                tx_data = {
                    "from": "0x" + str(start_idx) * 40,
                    "to": "0x" + str(i) * 40,
                    "value": "0x1",
                    "gas": "0x5208",
                }
                blockchain.add_transaction(tx_data)
                
        # Add transactions concurrently
        await asyncio.gather(
            add_transactions(1),
            add_transactions(2),
            add_transactions(3),
        )
        
        assert len(blockchain.pending_transactions) == 30
        
    def test_block_reorganization_scenario(self, blockchain):
        # Mine some blocks
        for i in range(5):
            for j in range(3):
                tx_data = {
                    "from": "0x" + str(j) * 40,
                    "to": "0x" + str(j+1) * 40,
                    "value": to_hex(i * j * 10**16),
                    "gas": "0x5208",
                }
                blockchain.add_transaction(tx_data)
            blockchain._mine_new_block()
            
        # Verify chain integrity
        for i in range(1, blockchain.current_block_number + 1):
            block = blockchain.blocks[i]
            parent = blockchain.blocks[i - 1]
            assert block.parent_hash == parent.hash
            
    def test_gas_refund_simulation(self, blockchain):
        # Transaction that should get gas refund (e.g., storage deletion)
        tx_data = {
            "from": "0x" + "1" * 40,
            "to": "0x" + "2" * 40,
            "value": "0x0",
            "gas": "0x30000",  # High gas limit
            "data": "0x" + "00" * 32,  # SSTORE to zero
        }
        
        tx_hash = blockchain.add_transaction(tx_data)
        blockchain._mine_new_block()
        
        receipt = blockchain.receipts[tx_hash]
        # Gas used should be less than gas limit
        assert to_int(hexstr=receipt.gas_used) < to_int(hexstr=blockchain.transactions[tx_hash].gas)
        
    def test_base_fee_extreme_conditions(self, blockchain):
        # Test base fee at minimum
        blockchain.base_fee_per_gas = 1000000000  # 1 gwei
        
        # Set parent block to have low gas usage
        parent = blockchain.blocks[blockchain.current_block_number]
        parent.gas_used = "0x1000"  # Very low gas usage
        
        # Mine empty block
        blockchain._mine_new_block()
        
        # Base fee should decrease but not below minimum
        assert blockchain.base_fee_per_gas >= 1000000000
        
        # Test base fee at high value
        blockchain.base_fee_per_gas = 10**17  # High value
        
        # Set parent block to have high gas usage
        parent = blockchain.blocks[blockchain.current_block_number]
        parent.gas_used = parent.gas_limit  # Simulate full block
        
        blockchain._mine_new_block()
        
        # Base fee should increase but stay within bounds
        assert blockchain.base_fee_per_gas <= 10**18
        
    def test_chain_id_consistency(self, blockchain):
        # Verify chain ID is consistent across operations
        assert blockchain.chain_id == 1
        
        # Add transaction and verify it doesn't change
        tx_data = {
            "from": "0x" + "1" * 40,
            "to": "0x" + "2" * 40,
            "value": "0x1",
        }
        blockchain.add_transaction(tx_data)
        assert blockchain.chain_id == 1
        
    def test_empty_block_mining(self, blockchain):
        initial_block_number = blockchain.current_block_number
        
        # Mine empty block
        blockchain._mine_new_block()
        
        assert blockchain.current_block_number == initial_block_number + 1
        block = blockchain.blocks[blockchain.current_block_number]
        assert len(block.transactions) == 0
        assert block.gas_used == "0x0"