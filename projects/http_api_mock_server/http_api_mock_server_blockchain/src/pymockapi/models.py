from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from eth_utils import to_hex, to_int
from hexbytes import HexBytes
import time


class Block(BaseModel):
    number: int
    hash: str
    parent_hash: str
    timestamp: int
    nonce: str = "0x0000000000000000"
    difficulty: str = "0x1"
    total_difficulty: str = "0x1"
    size: str = "0x1000"
    gas_limit: str = "0x1c9c380"
    gas_used: str = "0x0"
    miner: str
    transactions: List[Union[str, Dict[str, Any]]] = Field(default_factory=list)
    uncles: List[str] = Field(default_factory=list)
    base_fee_per_gas: Optional[str] = None
    
    def to_rpc_format(self, full_transactions: bool = False) -> Dict[str, Any]:
        return {
            "number": to_hex(self.number),
            "hash": self.hash,
            "parentHash": self.parent_hash,
            "timestamp": to_hex(self.timestamp),
            "nonce": self.nonce,
            "difficulty": self.difficulty,
            "totalDifficulty": self.total_difficulty,
            "size": self.size,
            "gasLimit": self.gas_limit,
            "gasUsed": self.gas_used,
            "miner": self.miner,
            "transactions": self.transactions,
            "uncles": self.uncles,
            "baseFeePerGas": self.base_fee_per_gas,
        }


class Transaction(BaseModel):
    hash: str
    nonce: int
    block_hash: Optional[str] = None
    block_number: Optional[int] = None
    transaction_index: Optional[int] = None
    from_address: str = Field(alias="from")
    to_address: Optional[str] = Field(alias="to", default=None)
    value: str
    gas: str
    gas_price: Optional[str] = None
    max_fee_per_gas: Optional[str] = None
    max_priority_fee_per_gas: Optional[str] = None
    input: str = "0x"
    v: str = "0x1b"
    r: str = "0x" + "0" * 64
    s: str = "0x" + "0" * 64
    type: str = "0x2"
    
    class Config:
        populate_by_name = True
    
    def to_rpc_format(self) -> Dict[str, Any]:
        result = {
            "hash": self.hash,
            "nonce": to_hex(self.nonce),
            "blockHash": self.block_hash,
            "blockNumber": to_hex(self.block_number) if self.block_number is not None else None,
            "transactionIndex": to_hex(self.transaction_index) if self.transaction_index is not None else None,
            "from": self.from_address,
            "to": self.to_address,
            "value": self.value,
            "gas": self.gas,
            "input": self.input,
            "v": self.v,
            "r": self.r,
            "s": self.s,
            "type": self.type,
        }
        
        if self.gas_price:
            result["gasPrice"] = self.gas_price
        if self.max_fee_per_gas:
            result["maxFeePerGas"] = self.max_fee_per_gas
        if self.max_priority_fee_per_gas:
            result["maxPriorityFeePerGas"] = self.max_priority_fee_per_gas
            
        return result


class TransactionReceipt(BaseModel):
    transaction_hash: str
    transaction_index: int
    block_hash: str
    block_number: int
    from_address: str = Field(alias="from")
    to_address: Optional[str] = Field(alias="to", default=None)
    cumulative_gas_used: str
    gas_used: str
    contract_address: Optional[str] = None
    logs: List[Dict[str, Any]] = Field(default_factory=list)
    logs_bloom: str = "0x" + "0" * 512
    status: str = "0x1"
    effective_gas_price: str
    type: str = "0x2"
    
    class Config:
        populate_by_name = True
    
    def to_rpc_format(self) -> Dict[str, Any]:
        return {
            "transactionHash": self.transaction_hash,
            "transactionIndex": to_hex(self.transaction_index),
            "blockHash": self.block_hash,
            "blockNumber": to_hex(self.block_number),
            "from": self.from_address,
            "to": self.to_address,
            "cumulativeGasUsed": self.cumulative_gas_used,
            "gasUsed": self.gas_used,
            "contractAddress": self.contract_address,
            "logs": self.logs,
            "logsBloom": self.logs_bloom,
            "status": self.status,
            "effectiveGasPrice": self.effective_gas_price,
            "type": self.type,
        }


class Log(BaseModel):
    address: str
    topics: List[str]
    data: str
    block_number: int
    transaction_hash: str
    transaction_index: int
    block_hash: str
    log_index: int
    removed: bool = False
    
    def to_rpc_format(self) -> Dict[str, Any]:
        return {
            "address": self.address,
            "topics": self.topics,
            "data": self.data,
            "blockNumber": to_hex(self.block_number),
            "transactionHash": self.transaction_hash,
            "transactionIndex": to_hex(self.transaction_index),
            "blockHash": self.block_hash,
            "logIndex": to_hex(self.log_index),
            "removed": self.removed,
        }


class FilterOptions(BaseModel):
    from_block: Optional[Union[str, int]] = None
    to_block: Optional[Union[str, int]] = None
    address: Optional[Union[str, List[str]]] = None
    topics: Optional[List[Optional[Union[str, List[str]]]]] = None
    block_hash: Optional[str] = None