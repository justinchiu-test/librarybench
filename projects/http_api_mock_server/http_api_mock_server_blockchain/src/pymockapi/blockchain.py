import asyncio
import time
from typing import Dict, List, Optional, Set, Union, Any
from eth_utils import keccak, to_hex, to_int, to_checksum_address
from hexbytes import HexBytes
import secrets
import rlp

from .models import Block, Transaction, TransactionReceipt, Log


class BlockchainState:
    def __init__(self, chain_id: int = 1):
        self.chain_id = chain_id
        self.blocks: Dict[int, Block] = {}
        self.blocks_by_hash: Dict[str, Block] = {}
        self.transactions: Dict[str, Transaction] = {}
        self.receipts: Dict[str, TransactionReceipt] = {}
        self.logs: List[Log] = []
        self.accounts: Dict[str, Dict[str, Union[int, str]]] = {}
        self.contracts: Dict[str, Dict[str, Any]] = {}
        self.current_block_number = 0
        self.pending_transactions: List[Transaction] = []
        self.nonces: Dict[str, int] = {}
        self.base_fee_per_gas = 1000000000  # 1 gwei
        self.block_time = 12  # seconds
        self._mining_task: Optional[asyncio.Task] = None
        self._genesis_block()
        
    def _genesis_block(self):
        genesis = Block(
            number=0,
            hash=self._generate_block_hash(0),
            parent_hash="0x" + "0" * 64,
            timestamp=int(time.time()),
            miner=to_checksum_address("0x" + "0" * 40),
            base_fee_per_gas=to_hex(self.base_fee_per_gas),
        )
        self.blocks[0] = genesis
        self.blocks_by_hash[genesis.hash] = genesis
        
    def _generate_block_hash(self, block_number: int) -> str:
        return to_hex(keccak(to_hex(block_number).encode()))
        
    def _generate_tx_hash(self) -> str:
        return to_hex(keccak(secrets.token_bytes(32)))
        
    async def start_mining(self):
        if self._mining_task is None:
            self._mining_task = asyncio.create_task(self._mine_blocks())
            
    async def stop_mining(self):
        if self._mining_task:
            self._mining_task.cancel()
            try:
                await self._mining_task
            except asyncio.CancelledError:
                pass
            self._mining_task = None
            
    async def _mine_blocks(self):
        while True:
            await asyncio.sleep(self.block_time)
            self._mine_new_block()
            
    def _mine_new_block(self):
        self.current_block_number += 1
        parent_block = self.blocks[self.current_block_number - 1]
        
        # Update base fee (EIP-1559)
        parent_gas_used = to_int(hexstr=parent_block.gas_used)
        parent_gas_limit = to_int(hexstr=parent_block.gas_limit)
        target_gas_used = parent_gas_limit // 2
        
        if parent_gas_used > target_gas_used:
            gas_delta = parent_gas_used - target_gas_used
            base_fee_delta = max(1, self.base_fee_per_gas * gas_delta // target_gas_used // 8)
            self.base_fee_per_gas = min(self.base_fee_per_gas + base_fee_delta, 10**18)
        elif parent_gas_used < target_gas_used:
            gas_delta = target_gas_used - parent_gas_used
            base_fee_delta = self.base_fee_per_gas * gas_delta // target_gas_used // 8
            self.base_fee_per_gas = max(self.base_fee_per_gas - base_fee_delta, 1000000000)
        
        # Process pending transactions
        block_transactions = []
        block_gas_used = 0
        gas_limit = to_int(hexstr=parent_block.gas_limit)
        
        for tx in self.pending_transactions[:]:
            tx_gas = to_int(hexstr=tx.gas)
            if block_gas_used + tx_gas <= gas_limit:
                tx.block_hash = self._generate_block_hash(self.current_block_number)
                tx.block_number = self.current_block_number
                tx.transaction_index = len(block_transactions)
                block_transactions.append(tx)
                block_gas_used += tx_gas
                self.pending_transactions.remove(tx)
                
                # Create receipt
                receipt = self._create_receipt(tx, block_gas_used)
                self.receipts[tx.hash] = receipt
        
        block = Block(
            number=self.current_block_number,
            hash=self._generate_block_hash(self.current_block_number),
            parent_hash=parent_block.hash,
            timestamp=int(time.time()),
            miner=to_checksum_address("0x" + "1" * 40),
            transactions=[tx.hash for tx in block_transactions],
            gas_used=to_hex(block_gas_used),
            base_fee_per_gas=to_hex(self.base_fee_per_gas),
        )
        
        self.blocks[self.current_block_number] = block
        self.blocks_by_hash[block.hash] = block
        
    def _create_receipt(self, tx: Transaction, cumulative_gas_used: int) -> TransactionReceipt:
        gas_used = to_int(hexstr=tx.gas) // 2  # Mock gas usage
        
        receipt = TransactionReceipt(
            transaction_hash=tx.hash,
            transaction_index=tx.transaction_index,
            block_hash=tx.block_hash,
            block_number=tx.block_number,
            from_address=tx.from_address,
            to_address=tx.to_address,
            cumulative_gas_used=to_hex(cumulative_gas_used),
            gas_used=to_hex(gas_used),
            contract_address=None if tx.to_address else self._generate_contract_address(tx.from_address, tx.nonce),
            effective_gas_price=tx.gas_price or tx.max_fee_per_gas or to_hex(self.base_fee_per_gas),
        )
        
        return receipt
        
    def _generate_contract_address(self, from_address: str, nonce: int) -> str:
        return to_checksum_address(
            to_hex(keccak(rlp.encode([bytes.fromhex(from_address[2:]), nonce]))[-20:])
        )
        
    def add_transaction(self, tx_data: Dict[str, Any]) -> str:
        from_address = to_checksum_address(tx_data["from"])
        nonce = self.get_nonce(from_address)
        
        tx = Transaction(
            hash=self._generate_tx_hash(),
            nonce=nonce,
            from_address=from_address,
            to_address=to_checksum_address(tx_data["to"]) if tx_data.get("to") else None,
            value=tx_data.get("value", "0x0"),
            gas=tx_data.get("gas", "0x5208"),
            gas_price=tx_data.get("gasPrice"),
            max_fee_per_gas=tx_data.get("maxFeePerGas"),
            max_priority_fee_per_gas=tx_data.get("maxPriorityFeePerGas"),
            input=tx_data.get("data", "0x"),
        )
        
        self.transactions[tx.hash] = tx
        self.pending_transactions.append(tx)
        self.nonces[from_address] = nonce + 1
        
        return tx.hash
        
    def get_balance(self, address: str) -> str:
        address = to_checksum_address(address)
        return to_hex(self.accounts.get(address, {}).get("balance", 10**18))
        
    def set_balance(self, address: str, balance: Union[str, int]):
        address = to_checksum_address(address)
        if address not in self.accounts:
            self.accounts[address] = {}
        self.accounts[address]["balance"] = to_int(hexstr=balance) if isinstance(balance, str) else balance
        
    def get_nonce(self, address: str) -> int:
        address = to_checksum_address(address)
        return self.nonces.get(address, 0)
        
    def get_code(self, address: str) -> str:
        address = to_checksum_address(address)
        return self.contracts.get(address, {}).get("code", "0x")
        
    def set_code(self, address: str, code: str):
        address = to_checksum_address(address)
        if address not in self.contracts:
            self.contracts[address] = {}
        self.contracts[address]["code"] = code
        
    def get_storage_at(self, address: str, position: str) -> str:
        address = to_checksum_address(address)
        storage = self.contracts.get(address, {}).get("storage", {})
        return storage.get(position, "0x" + "0" * 64)
        
    def set_storage_at(self, address: str, position: str, value: str):
        address = to_checksum_address(address)
        if address not in self.contracts:
            self.contracts[address] = {}
        if "storage" not in self.contracts[address]:
            self.contracts[address]["storage"] = {}
        self.contracts[address]["storage"][position] = value
        
    def add_log(self, log: Log):
        self.logs.append(log)
        
    def get_logs(self, filter_options: Dict[str, Any]) -> List[Log]:
        from_block = filter_options.get("fromBlock", 0)
        to_block = filter_options.get("toBlock", self.current_block_number)
        addresses = filter_options.get("address", [])
        topics = filter_options.get("topics", [])
        
        if isinstance(from_block, str):
            if from_block == "latest":
                from_block = self.current_block_number
            elif from_block == "pending":
                from_block = self.current_block_number + 1
            elif from_block == "earliest":
                from_block = 0
            else:
                from_block = to_int(hexstr=from_block)
                
        if isinstance(to_block, str):
            if to_block == "latest":
                to_block = self.current_block_number
            elif to_block == "pending":
                to_block = self.current_block_number + 1
            elif to_block == "earliest":
                to_block = 0
            else:
                to_block = to_int(hexstr=to_block)
                
        if isinstance(addresses, str):
            addresses = [addresses]
            
        filtered_logs = []
        for log in self.logs:
            if from_block <= log.block_number <= to_block:
                if not addresses or log.address in addresses:
                    if self._match_topics(log.topics, topics):
                        filtered_logs.append(log)
                        
        return filtered_logs
        
    def _match_topics(self, log_topics: List[str], filter_topics: List[Optional[Union[str, List[str]]]]) -> bool:
        if not filter_topics:
            return True
            
        for i, filter_topic in enumerate(filter_topics):
            if filter_topic is None:
                continue
            if i >= len(log_topics):
                return False
            if isinstance(filter_topic, str):
                if log_topics[i] != filter_topic:
                    return False
            elif isinstance(filter_topic, list):
                if log_topics[i] not in filter_topic:
                    return False
                    
        return True