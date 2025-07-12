from typing import Any, Dict, List, Optional
from eth_utils import keccak, to_hex, to_checksum_address, encode_hex
from eth_abi import encode
import json

from .models import Log


class EventEmitter:
    def __init__(self, blockchain):
        self.blockchain = blockchain
        
    def emit_event(
        self,
        address: str,
        event_signature: str,
        indexed_params: List[Any],
        data_params: List[Any],
        tx_hash: str,
        tx_index: int,
        block_number: int,
        block_hash: str,
        log_index: int,
    ) -> Log:
        # Calculate event topic (keccak256 of signature)
        event_topic = to_hex(keccak(text=event_signature))
        
        # Build topics array
        topics = [event_topic]
        for param in indexed_params:
            if isinstance(param, str) and param.startswith("0x"):
                topics.append(param)
            elif isinstance(param, int):
                topics.append(to_hex(param))
            elif isinstance(param, bytes):
                topics.append(encode_hex(param))
            else:
                # For complex types, hash them
                topics.append(to_hex(keccak(str(param).encode())))
                
        # Encode data parameters
        if data_params:
            # Simple encoding for common types
            data_bytes = b""
            for param in data_params:
                if isinstance(param, int):
                    data_bytes += param.to_bytes(32, byteorder='big')
                elif isinstance(param, str) and param.startswith("0x"):
                    data_bytes += bytes.fromhex(param[2:].zfill(64))
                elif isinstance(param, bytes):
                    data_bytes += param.ljust(32, b'\x00')[:32]
                else:
                    # For complex types, encode as bytes32
                    data_bytes += keccak(str(param).encode())[:32]
            data = encode_hex(data_bytes)
        else:
            data = "0x"
            
        log = Log(
            address=to_checksum_address(address),
            topics=topics,
            data=data,
            block_number=block_number,
            transaction_hash=tx_hash,
            transaction_index=tx_index,
            block_hash=block_hash,
            log_index=log_index,
        )
        
        self.blockchain.add_log(log)
        return log
        
    def emit_transfer(
        self,
        token_address: str,
        from_address: str,
        to_address: str,
        amount: int,
        tx_hash: str,
        tx_index: int,
        block_number: int,
        block_hash: str,
        log_index: int,
    ) -> Log:
        # Transfer(address indexed from, address indexed to, uint256 value)
        from_padded = "0x" + from_address[2:].lower().zfill(64)
        to_padded = "0x" + to_address[2:].lower().zfill(64)
        
        return self.emit_event(
            address=token_address,
            event_signature="Transfer(address,address,uint256)",
            indexed_params=[from_padded, to_padded],
            data_params=[amount],
            tx_hash=tx_hash,
            tx_index=tx_index,
            block_number=block_number,
            block_hash=block_hash,
            log_index=log_index,
        )
        
    def emit_approval(
        self,
        token_address: str,
        owner_address: str,
        spender_address: str,
        amount: int,
        tx_hash: str,
        tx_index: int,
        block_number: int,
        block_hash: str,
        log_index: int,
    ) -> Log:
        # Approval(address indexed owner, address indexed spender, uint256 value)
        owner_padded = "0x" + owner_address[2:].lower().zfill(64)
        spender_padded = "0x" + spender_address[2:].lower().zfill(64)
        
        return self.emit_event(
            address=token_address,
            event_signature="Approval(address,address,uint256)",
            indexed_params=[owner_padded, spender_padded],
            data_params=[amount],
            tx_hash=tx_hash,
            tx_index=tx_index,
            block_number=block_number,
            block_hash=block_hash,
            log_index=log_index,
        )
        
    def create_bloom_filter(self, logs: List[Log]) -> str:
        # Simple bloom filter implementation
        bloom = bytearray(256)  # 2048 bits
        
        for log in logs:
            # Add address to bloom
            address_hash = keccak(bytes.fromhex(log.address[2:]))
            for i in range(3):
                bit_pos = (address_hash[i * 2] << 8) | address_hash[i * 2 + 1]
                byte_pos = bit_pos // 8
                bit_in_byte = bit_pos % 8
                bloom[byte_pos % 256] |= (1 << bit_in_byte)
                
            # Add topics to bloom
            for topic in log.topics:
                topic_hash = keccak(bytes.fromhex(topic[2:]))
                for i in range(3):
                    bit_pos = (topic_hash[i * 2] << 8) | topic_hash[i * 2 + 1]
                    byte_pos = bit_pos // 8
                    bit_in_byte = bit_pos % 8
                    bloom[byte_pos % 256] |= (1 << bit_in_byte)
                    
        return "0x" + bloom.hex()