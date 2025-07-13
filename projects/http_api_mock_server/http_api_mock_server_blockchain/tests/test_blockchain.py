import pytest
import asyncio
from eth_utils import to_hex, to_int, to_checksum_address
from pymockapi.blockchain import BlockchainState
from pymockapi.models import Transaction, Log


class TestBlockchainState:
    @pytest.fixture
    def blockchain(self):
        return BlockchainState(chain_id=1)
        
    def test_genesis_block(self, blockchain):
        assert blockchain.current_block_number == 0
        assert 0 in blockchain.blocks
        genesis = blockchain.blocks[0]
        assert genesis.number == 0
        assert genesis.parent_hash == "0x" + "0" * 64
        
    def test_add_transaction(self, blockchain):
        tx_data = {
            "from": "0x" + "1" * 40,
            "to": "0x" + "2" * 40,
            "value": "0x1",
            "gas": "0x5208",
        }
        
        tx_hash = blockchain.add_transaction(tx_data)
        
        assert tx_hash in blockchain.transactions
        assert len(blockchain.pending_transactions) == 1
        tx = blockchain.transactions[tx_hash]
        assert tx.from_address == to_checksum_address("0x" + "1" * 40)
        assert tx.to_address == to_checksum_address("0x" + "2" * 40)
        
    def test_mine_new_block(self, blockchain):
        # Add some transactions
        for i in range(3):
            tx_data = {
                "from": "0x" + str(i) * 40,
                "to": "0x" + str(i+1) * 40,
                "value": to_hex(i),
                "gas": "0x5208",
            }
            blockchain.add_transaction(tx_data)
            
        assert len(blockchain.pending_transactions) == 3
        
        # Mine a block
        blockchain._mine_new_block()
        
        assert blockchain.current_block_number == 1
        assert 1 in blockchain.blocks
        assert len(blockchain.pending_transactions) == 0
        
        block = blockchain.blocks[1]
        assert len(block.transactions) == 3
        
    def test_get_balance(self, blockchain):
        address = "0x" + "1" * 40
        
        # Default balance
        balance = blockchain.get_balance(address)
        assert to_int(hexstr=balance) == 10**18
        
        # Set balance
        blockchain.set_balance(address, "0x1234")
        balance = blockchain.get_balance(address)
        assert balance == "0x1234"
        
    def test_get_nonce(self, blockchain):
        address = "0x" + "1" * 40
        
        # Initial nonce
        assert blockchain.get_nonce(address) == 0
        
        # Add transaction
        tx_data = {
            "from": address,
            "to": "0x" + "2" * 40,
            "value": "0x0",
        }
        blockchain.add_transaction(tx_data)
        
        # Nonce should increment
        assert blockchain.get_nonce(address) == 1
        
    def test_contract_code(self, blockchain):
        address = "0x" + "1" * 40
        code = "0x606060"
        
        # No code initially
        assert blockchain.get_code(address) == "0x"
        
        # Set code
        blockchain.set_code(address, code)
        assert blockchain.get_code(address) == code
        
    def test_storage(self, blockchain):
        address = "0x" + "1" * 40
        position = "0x0"
        value = "0x" + "f" * 64
        
        # No storage initially
        assert blockchain.get_storage_at(address, position) == "0x" + "0" * 64
        
        # Set storage
        blockchain.set_storage_at(address, position, value)
        assert blockchain.get_storage_at(address, position) == value
        
    def test_add_log(self, blockchain):
        log = Log(
            address="0x" + "1" * 40,
            topics=["0x" + "a" * 64],
            data="0x",
            block_number=0,
            transaction_hash="0x" + "b" * 64,
            transaction_index=0,
            block_hash="0x" + "c" * 64,
            log_index=0,
        )
        
        blockchain.add_log(log)
        assert len(blockchain.logs) == 1
        assert blockchain.logs[0] == log
        
    def test_get_logs_filtering(self, blockchain):
        # Add various logs
        for i in range(5):
            # Create proper addresses
            if i % 2 == 0:
                address = to_checksum_address("0x" + "0" * 40)
            else:
                address = to_checksum_address("0x" + "1" * 40)
                
            log = Log(
                address=address,
                topics=["0x" + "a" * 64 if i % 2 == 0 else "0x" + "b" * 64],
                data="0x",
                block_number=i,
                transaction_hash="0x" + str(i) * 64,
                transaction_index=0,
                block_hash="0x" + "c" * 64,
                log_index=i,
            )
            blockchain.add_log(log)
            
        # Filter by block range
        logs = blockchain.get_logs({"fromBlock": 1, "toBlock": 3})
        assert len(logs) == 3
        
        # Filter by address (need to specify block range since we're at block 0)
        logs = blockchain.get_logs({
            "address": to_checksum_address("0x" + "0" * 40),
            "fromBlock": 0,
            "toBlock": 4
        })
        assert len(logs) == 3
        
        # Filter by topics
        logs = blockchain.get_logs({
            "topics": ["0x" + "a" * 64],
            "fromBlock": 0,
            "toBlock": 4
        })
        assert len(logs) == 3
        
    @pytest.mark.asyncio
    async def test_mining_task(self, blockchain):
        blockchain.block_time = 0.1  # Fast mining for test
        
        await blockchain.start_mining()
        await asyncio.sleep(0.3)
        await blockchain.stop_mining()
        
        # Should have mined at least 2 blocks
        assert blockchain.current_block_number >= 2
        
    def test_base_fee_update(self, blockchain):
        initial_base_fee = blockchain.base_fee_per_gas
        
        # Mine block with high gas usage
        parent = blockchain.blocks[0]
        parent.gas_used = "0x1c9c380"  # Max gas
        
        blockchain._mine_new_block()
        
        # Base fee should increase
        assert blockchain.base_fee_per_gas > initial_base_fee