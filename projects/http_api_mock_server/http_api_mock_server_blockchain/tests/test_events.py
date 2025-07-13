import pytest
from eth_utils import keccak, to_hex
from pymockapi.blockchain import BlockchainState
from pymockapi.events import EventEmitter
from pymockapi.models import Log


class TestEventEmitter:
    @pytest.fixture
    def blockchain(self):
        return BlockchainState(chain_id=1)
        
    @pytest.fixture
    def event_emitter(self, blockchain):
        return EventEmitter(blockchain)
        
    def test_emit_event(self, event_emitter, blockchain):
        log = event_emitter.emit_event(
            address="0x" + "1" * 40,
            event_signature="Transfer(address,address,uint256)",
            indexed_params=["0x" + "2" * 40, "0x" + "3" * 40],
            data_params=[1000],
            tx_hash="0x" + "a" * 64,
            tx_index=0,
            block_number=1,
            block_hash="0x" + "b" * 64,
            log_index=0,
        )
        
        assert log.address == "0x" + "1" * 40
        assert len(log.topics) == 3
        # First topic is event signature hash
        assert log.topics[0] == to_hex(keccak(text="Transfer(address,address,uint256)"))
        assert len(blockchain.logs) == 1
        
    def test_emit_transfer(self, event_emitter, blockchain):
        log = event_emitter.emit_transfer(
            token_address="0x" + "1" * 40,
            from_address="0x" + "2" * 40,
            to_address="0x" + "3" * 40,
            amount=1000,
            tx_hash="0x" + "a" * 64,
            tx_index=0,
            block_number=1,
            block_hash="0x" + "b" * 64,
            log_index=0,
        )
        
        assert log.address == "0x" + "1" * 40
        assert len(log.topics) == 3
        # Verify Transfer event signature
        assert log.topics[0] == to_hex(keccak(text="Transfer(address,address,uint256)"))
        
    def test_emit_approval(self, event_emitter, blockchain):
        log = event_emitter.emit_approval(
            token_address="0x" + "1" * 40,
            owner_address="0x" + "2" * 40,
            spender_address="0x" + "3" * 40,
            amount=5000,
            tx_hash="0x" + "a" * 64,
            tx_index=0,
            block_number=1,
            block_hash="0x" + "b" * 64,
            log_index=0,
        )
        
        assert log.address == "0x" + "1" * 40
        assert len(log.topics) == 3
        # Verify Approval event signature
        assert log.topics[0] == to_hex(keccak(text="Approval(address,address,uint256)"))
        
    def test_create_bloom_filter(self, event_emitter):
        logs = []
        for i in range(3):
            log = Log(
                address="0x" + str(i) * 40,
                topics=["0x" + "a" * 64],
                data="0x",
                block_number=i,
                transaction_hash="0x" + str(i) * 64,
                transaction_index=0,
                block_hash="0x" + "b" * 64,
                log_index=i,
            )
            logs.append(log)
            
        bloom = event_emitter.create_bloom_filter(logs)
        
        assert bloom.startswith("0x")
        assert len(bloom) == 514  # 0x + 512 hex chars (256 bytes)
        # Bloom filter should not be all zeros
        assert bloom != "0x" + "0" * 512