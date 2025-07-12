from typing import Any, Dict, List, Optional, Union
from eth_utils import to_hex, to_int, to_checksum_address, is_address
import json

from .blockchain import BlockchainState
from .models import FilterOptions, Log


class JSONRPCEngine:
    def __init__(self, blockchain: BlockchainState):
        self.blockchain = blockchain
        self.filters: Dict[str, Dict[str, Any]] = {}
        self.filter_id_counter = 0
        
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        method = request.get("method")
        params = request.get("params", [])
        request_id = request.get("id", 1)
        
        try:
            if method == "eth_chainId":
                result = self.eth_chain_id()
            elif method == "eth_blockNumber":
                result = self.eth_block_number()
            elif method == "eth_getBlockByNumber":
                result = self.eth_get_block_by_number(params[0], params[1] if len(params) > 1 else False)
            elif method == "eth_getBlockByHash":
                result = self.eth_get_block_by_hash(params[0], params[1] if len(params) > 1 else False)
            elif method == "eth_getTransactionByHash":
                result = self.eth_get_transaction_by_hash(params[0])
            elif method == "eth_getTransactionReceipt":
                result = self.eth_get_transaction_receipt(params[0])
            elif method == "eth_sendTransaction":
                result = self.eth_send_transaction(params[0])
            elif method == "eth_sendRawTransaction":
                result = self.eth_send_raw_transaction(params[0])
            elif method == "eth_call":
                result = self.eth_call(params[0], params[1] if len(params) > 1 else "latest")
            elif method == "eth_estimateGas":
                result = self.eth_estimate_gas(params[0])
            elif method == "eth_gasPrice":
                result = self.eth_gas_price()
            elif method == "eth_getBalance":
                result = self.eth_get_balance(params[0], params[1] if len(params) > 1 else "latest")
            elif method == "eth_getCode":
                result = self.eth_get_code(params[0], params[1] if len(params) > 1 else "latest")
            elif method == "eth_getStorageAt":
                result = self.eth_get_storage_at(params[0], params[1], params[2] if len(params) > 2 else "latest")
            elif method == "eth_getTransactionCount":
                result = self.eth_get_transaction_count(params[0], params[1] if len(params) > 1 else "latest")
            elif method == "eth_newFilter":
                result = self.eth_new_filter(params[0] if params else {})
            elif method == "eth_newBlockFilter":
                result = self.eth_new_block_filter()
            elif method == "eth_newPendingTransactionFilter":
                result = self.eth_new_pending_transaction_filter()
            elif method == "eth_uninstallFilter":
                result = self.eth_uninstall_filter(params[0])
            elif method == "eth_getFilterChanges":
                result = self.eth_get_filter_changes(params[0])
            elif method == "eth_getFilterLogs":
                result = self.eth_get_filter_logs(params[0])
            elif method == "eth_getLogs":
                result = self.eth_get_logs(params[0] if params else {})
            elif method == "eth_accounts":
                result = self.eth_accounts()
            elif method == "eth_coinbase":
                result = self.eth_coinbase()
            elif method == "eth_mining":
                result = self.eth_mining()
            elif method == "eth_hashrate":
                result = self.eth_hashrate()
            elif method == "eth_syncing":
                result = self.eth_syncing()
            elif method == "net_version":
                result = self.net_version()
            elif method == "net_listening":
                result = self.net_listening()
            elif method == "net_peerCount":
                result = self.net_peer_count()
            elif method == "web3_clientVersion":
                result = self.web3_client_version()
            elif method == "web3_sha3":
                result = self.web3_sha3(params[0])
            elif method == "eth_maxPriorityFeePerGas":
                result = self.eth_max_priority_fee_per_gas()
            elif method == "eth_feeHistory":
                result = self.eth_fee_history(params[0], params[1], params[2] if len(params) > 2 else [])
            else:
                return self._error_response(request_id, -32601, "Method not found")
                
            return self._success_response(request_id, result)
            
        except Exception as e:
            return self._error_response(request_id, -32603, str(e))
            
    def _success_response(self, request_id: Any, result: Any) -> Dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result,
        }
        
    def _error_response(self, request_id: Any, code: int, message: str) -> Dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message,
            }
        }
        
    def eth_chain_id(self) -> str:
        return to_hex(self.blockchain.chain_id)
        
    def eth_block_number(self) -> str:
        return to_hex(self.blockchain.current_block_number)
        
    def eth_get_block_by_number(self, block_number: Union[str, int], full_transactions: bool) -> Optional[Dict[str, Any]]:
        if isinstance(block_number, str):
            if block_number == "latest":
                block_number = self.blockchain.current_block_number
            elif block_number == "pending":
                return None  # No pending block in this implementation
            elif block_number == "earliest":
                block_number = 0
            else:
                block_number = to_int(hexstr=block_number)
                
        block = self.blockchain.blocks.get(block_number)
        if block:
            block_data = block.to_rpc_format(full_transactions)
            if full_transactions:
                block_data["transactions"] = [
                    self.blockchain.transactions[tx_hash].to_rpc_format()
                    for tx_hash in block.transactions
                    if tx_hash in self.blockchain.transactions
                ]
            return block_data
        return None
        
    def eth_get_block_by_hash(self, block_hash: str, full_transactions: bool) -> Optional[Dict[str, Any]]:
        block = self.blockchain.blocks_by_hash.get(block_hash)
        if block:
            block_data = block.to_rpc_format(full_transactions)
            if full_transactions:
                block_data["transactions"] = [
                    self.blockchain.transactions[tx_hash].to_rpc_format()
                    for tx_hash in block.transactions
                    if tx_hash in self.blockchain.transactions
                ]
            return block_data
        return None
        
    def eth_get_transaction_by_hash(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        tx = self.blockchain.transactions.get(tx_hash)
        return tx.to_rpc_format() if tx else None
        
    def eth_get_transaction_receipt(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        receipt = self.blockchain.receipts.get(tx_hash)
        return receipt.to_rpc_format() if receipt else None
        
    def eth_send_transaction(self, tx_data: Dict[str, Any]) -> str:
        return self.blockchain.add_transaction(tx_data)
        
    def eth_send_raw_transaction(self, raw_tx: str) -> str:
        # For simplicity, we'll just create a mock transaction
        tx_data = {
            "from": to_checksum_address("0x" + "1" * 40),
            "to": to_checksum_address("0x" + "2" * 40),
            "value": "0x0",
            "gas": "0x5208",
            "gasPrice": to_hex(self.blockchain.base_fee_per_gas),
        }
        return self.blockchain.add_transaction(tx_data)
        
    def eth_call(self, call_data: Dict[str, Any], block_number: Union[str, int]) -> str:
        # Mock implementation - return empty result
        return "0x"
        
    def eth_estimate_gas(self, tx_data: Dict[str, Any]) -> str:
        # Simple gas estimation
        base_gas = 21000
        if tx_data.get("data") and tx_data["data"] != "0x":
            data_gas = len(tx_data["data"]) * 16
            base_gas += data_gas
        return to_hex(base_gas)
        
    def eth_gas_price(self) -> str:
        return to_hex(self.blockchain.base_fee_per_gas)
        
    def eth_get_balance(self, address: str, block_number: Union[str, int]) -> str:
        return self.blockchain.get_balance(address)
        
    def eth_get_code(self, address: str, block_number: Union[str, int]) -> str:
        return self.blockchain.get_code(address)
        
    def eth_get_storage_at(self, address: str, position: str, block_number: Union[str, int]) -> str:
        return self.blockchain.get_storage_at(address, position)
        
    def eth_get_transaction_count(self, address: str, block_number: Union[str, int]) -> str:
        return to_hex(self.blockchain.get_nonce(address))
        
    def eth_new_filter(self, filter_params: Dict[str, Any]) -> str:
        filter_id = to_hex(self.filter_id_counter)
        self.filter_id_counter += 1
        self.filters[filter_id] = {
            "type": "log",
            "params": filter_params,
            "last_poll_block": self.blockchain.current_block_number,
        }
        return filter_id
        
    def eth_new_block_filter(self) -> str:
        filter_id = to_hex(self.filter_id_counter)
        self.filter_id_counter += 1
        self.filters[filter_id] = {
            "type": "block",
            "last_poll_block": self.blockchain.current_block_number,
        }
        return filter_id
        
    def eth_new_pending_transaction_filter(self) -> str:
        filter_id = to_hex(self.filter_id_counter)
        self.filter_id_counter += 1
        self.filters[filter_id] = {
            "type": "pending_transaction",
            "seen_txs": set(),
        }
        return filter_id
        
    def eth_uninstall_filter(self, filter_id: str) -> bool:
        if filter_id in self.filters:
            del self.filters[filter_id]
            return True
        return False
        
    def eth_get_filter_changes(self, filter_id: str) -> List[Any]:
        if filter_id not in self.filters:
            return []
            
        filter_data = self.filters[filter_id]
        
        if filter_data["type"] == "log":
            logs = self.blockchain.get_logs(filter_data["params"])
            new_logs = [
                log.to_rpc_format() for log in logs
                if log.block_number > filter_data["last_poll_block"]
            ]
            filter_data["last_poll_block"] = self.blockchain.current_block_number
            return new_logs
            
        elif filter_data["type"] == "block":
            new_blocks = []
            for block_num in range(filter_data["last_poll_block"] + 1, self.blockchain.current_block_number + 1):
                if block_num in self.blockchain.blocks:
                    new_blocks.append(self.blockchain.blocks[block_num].hash)
            filter_data["last_poll_block"] = self.blockchain.current_block_number
            return new_blocks
            
        elif filter_data["type"] == "pending_transaction":
            new_txs = []
            for tx in self.blockchain.pending_transactions:
                if tx.hash not in filter_data["seen_txs"]:
                    new_txs.append(tx.hash)
                    filter_data["seen_txs"].add(tx.hash)
            return new_txs
            
        return []
        
    def eth_get_filter_logs(self, filter_id: str) -> List[Dict[str, Any]]:
        if filter_id not in self.filters:
            return []
            
        filter_data = self.filters[filter_id]
        if filter_data["type"] == "log":
            logs = self.blockchain.get_logs(filter_data["params"])
            return [log.to_rpc_format() for log in logs]
            
        return []
        
    def eth_get_logs(self, filter_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        logs = self.blockchain.get_logs(filter_params)
        return [log.to_rpc_format() for log in logs]
        
    def eth_accounts(self) -> List[str]:
        return list(self.blockchain.accounts.keys())
        
    def eth_coinbase(self) -> str:
        return to_checksum_address("0x" + "1" * 40)
        
    def eth_mining(self) -> bool:
        return self.blockchain._mining_task is not None
        
    def eth_hashrate(self) -> str:
        return "0x0"
        
    def eth_syncing(self) -> Union[bool, Dict[str, str]]:
        return False
        
    def net_version(self) -> str:
        return str(self.blockchain.chain_id)
        
    def net_listening(self) -> bool:
        return True
        
    def net_peer_count(self) -> str:
        return "0x0"
        
    def web3_client_version(self) -> str:
        return "PyMockAPI/0.1.0"
        
    def web3_sha3(self, data: str) -> str:
        from eth_utils import keccak
        return to_hex(keccak(hexstr=data))
        
    def eth_max_priority_fee_per_gas(self) -> str:
        return to_hex(1000000000)  # 1 gwei
        
    def eth_fee_history(self, block_count: int, newest_block: Union[str, int], percentiles: List[float]) -> Dict[str, Any]:
        if isinstance(newest_block, str):
            if newest_block == "latest":
                newest_block = self.blockchain.current_block_number
            else:
                newest_block = to_int(hexstr=newest_block)
                
        oldest_block = max(0, newest_block - block_count + 1)
        
        base_fees = []
        gas_used_ratios = []
        rewards = []
        
        for block_num in range(oldest_block, newest_block + 1):
            if block_num in self.blockchain.blocks:
                block = self.blockchain.blocks[block_num]
                base_fees.append(block.base_fee_per_gas or "0x0")
                
                gas_limit = to_int(hexstr=block.gas_limit)
                gas_used = to_int(hexstr=block.gas_used)
                gas_used_ratios.append(gas_used / gas_limit if gas_limit > 0 else 0)
                
                # Mock rewards based on percentiles
                block_rewards = []
                for percentile in percentiles:
                    reward = int(1000000000 * (1 + percentile / 100))
                    block_rewards.append(to_hex(reward))
                rewards.append(block_rewards)
                
        # Add next block's base fee
        if newest_block == self.blockchain.current_block_number:
            base_fees.append(to_hex(self.blockchain.base_fee_per_gas))
            
        return {
            "oldestBlock": to_hex(oldest_block),
            "baseFeePerGas": base_fees,
            "gasUsedRatio": gas_used_ratios,
            "reward": rewards,
        }