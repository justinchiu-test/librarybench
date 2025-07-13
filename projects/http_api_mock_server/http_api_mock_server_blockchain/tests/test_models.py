import pytest
from eth_utils import to_hex, to_checksum_address
from pymockapi.models import Block, Transaction, TransactionReceipt, Log, FilterOptions


class TestBlock:
    def test_block_creation(self):
        block = Block(
            number=1,
            hash="0x1234",
            parent_hash="0x0000",
            timestamp=1234567890,
            miner=to_checksum_address("0x" + "1" * 40),
        )
        
        assert block.number == 1
        assert block.hash == "0x1234"
        assert block.parent_hash == "0x0000"
        assert block.timestamp == 1234567890
        
    def test_block_to_rpc_format(self):
        block = Block(
            number=1,
            hash="0x1234",
            parent_hash="0x0000",
            timestamp=1234567890,
            miner=to_checksum_address("0x" + "1" * 40),
            gas_used="0x5208",
            base_fee_per_gas="0x3b9aca00",
        )
        
        rpc_format = block.to_rpc_format()
        
        assert rpc_format["number"] == "0x1"
        assert rpc_format["hash"] == "0x1234"
        assert rpc_format["parentHash"] == "0x0000"
        assert rpc_format["timestamp"] == to_hex(1234567890)
        assert rpc_format["gasUsed"] == "0x5208"
        assert rpc_format["baseFeePerGas"] == "0x3b9aca00"


class TestTransaction:
    def test_transaction_creation(self):
        tx = Transaction(
            hash="0xabc",
            nonce=0,
            from_address="0x" + "1" * 40,
            to_address="0x" + "2" * 40,
            value="0x0",
            gas="0x5208",
            gas_price="0x3b9aca00",
        )
        
        assert tx.hash == "0xabc"
        assert tx.nonce == 0
        assert tx.from_address == "0x" + "1" * 40
        assert tx.to_address == "0x" + "2" * 40
        
    def test_transaction_to_rpc_format(self):
        tx = Transaction(
            hash="0xabc",
            nonce=10,
            block_hash="0xdef",
            block_number=5,
            transaction_index=2,
            from_address="0x" + "1" * 40,
            to_address="0x" + "2" * 40,
            value="0x1",
            gas="0x5208",
            max_fee_per_gas="0x4a817c800",
            max_priority_fee_per_gas="0x3b9aca00",
        )
        
        rpc_format = tx.to_rpc_format()
        
        assert rpc_format["hash"] == "0xabc"
        assert rpc_format["nonce"] == "0xa"
        assert rpc_format["blockHash"] == "0xdef"
        assert rpc_format["blockNumber"] == "0x5"
        assert rpc_format["transactionIndex"] == "0x2"
        assert rpc_format["maxFeePerGas"] == "0x4a817c800"
        assert rpc_format["maxPriorityFeePerGas"] == "0x3b9aca00"


class TestTransactionReceipt:
    def test_receipt_creation(self):
        receipt = TransactionReceipt(
            transaction_hash="0xabc",
            transaction_index=0,
            block_hash="0xdef",
            block_number=1,
            from_address="0x" + "1" * 40,
            to_address="0x" + "2" * 40,
            cumulative_gas_used="0x5208",
            gas_used="0x5208",
            effective_gas_price="0x3b9aca00",
        )
        
        assert receipt.transaction_hash == "0xabc"
        assert receipt.status == "0x1"
        assert receipt.gas_used == "0x5208"
        
    def test_receipt_to_rpc_format(self):
        receipt = TransactionReceipt(
            transaction_hash="0xabc",
            transaction_index=2,
            block_hash="0xdef",
            block_number=10,
            from_address="0x" + "1" * 40,
            to_address="0x" + "2" * 40,
            cumulative_gas_used="0xa410",
            gas_used="0x5208",
            effective_gas_price="0x3b9aca00",
            contract_address="0x" + "3" * 40,
        )
        
        rpc_format = receipt.to_rpc_format()
        
        assert rpc_format["transactionHash"] == "0xabc"
        assert rpc_format["transactionIndex"] == "0x2"
        assert rpc_format["blockNumber"] == "0xa"
        assert rpc_format["contractAddress"] == "0x" + "3" * 40
        assert rpc_format["status"] == "0x1"


class TestLog:
    def test_log_creation(self):
        log = Log(
            address="0x" + "1" * 40,
            topics=["0x" + "a" * 64, "0x" + "b" * 64],
            data="0x" + "c" * 64,
            block_number=1,
            transaction_hash="0xabc",
            transaction_index=0,
            block_hash="0xdef",
            log_index=0,
        )
        
        assert log.address == "0x" + "1" * 40
        assert len(log.topics) == 2
        assert log.removed is False
        
    def test_log_to_rpc_format(self):
        log = Log(
            address="0x" + "1" * 40,
            topics=["0x" + "a" * 64],
            data="0x1234",
            block_number=5,
            transaction_hash="0xabc",
            transaction_index=2,
            block_hash="0xdef",
            log_index=3,
        )
        
        rpc_format = log.to_rpc_format()
        
        assert rpc_format["address"] == "0x" + "1" * 40
        assert rpc_format["blockNumber"] == "0x5"
        assert rpc_format["transactionIndex"] == "0x2"
        assert rpc_format["logIndex"] == "0x3"
        assert rpc_format["removed"] is False