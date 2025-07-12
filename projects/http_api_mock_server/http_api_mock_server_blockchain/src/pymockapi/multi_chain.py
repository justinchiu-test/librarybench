from typing import Dict, Optional, Any
from .blockchain import BlockchainState
from .rpc_engine import JSONRPCEngine


class ChainConfig:
    def __init__(
        self,
        chain_id: int,
        name: str,
        native_currency: str = "ETH",
        block_time: int = 12,
        gas_limit: int = 30000000,
        base_fee: int = 1000000000,
    ):
        self.chain_id = chain_id
        self.name = name
        self.native_currency = native_currency
        self.block_time = block_time
        self.gas_limit = gas_limit
        self.base_fee = base_fee


class MultiChainRouter:
    def __init__(self):
        self.chains: Dict[int, BlockchainState] = {}
        self.rpc_engines: Dict[int, JSONRPCEngine] = {}
        self.chain_configs: Dict[int, ChainConfig] = {}
        self._setup_default_chains()
        
    def _setup_default_chains(self):
        # Ethereum Mainnet
        self.add_chain(ChainConfig(
            chain_id=1,
            name="Ethereum Mainnet",
            native_currency="ETH",
            block_time=12,
        ))
        
        # Goerli Testnet
        self.add_chain(ChainConfig(
            chain_id=5,
            name="Goerli Testnet",
            native_currency="ETH",
            block_time=12,
        ))
        
        # Polygon
        self.add_chain(ChainConfig(
            chain_id=137,
            name="Polygon",
            native_currency="MATIC",
            block_time=2,
            base_fee=30000000000,  # 30 gwei
        ))
        
        # Arbitrum
        self.add_chain(ChainConfig(
            chain_id=42161,
            name="Arbitrum One",
            native_currency="ETH",
            block_time=1,
            base_fee=100000000,  # 0.1 gwei
        ))
        
        # Optimism
        self.add_chain(ChainConfig(
            chain_id=10,
            name="Optimism",
            native_currency="ETH",
            block_time=2,
            base_fee=1000000,  # 0.001 gwei
        ))
        
    def add_chain(self, config: ChainConfig):
        blockchain = BlockchainState(chain_id=config.chain_id)
        blockchain.block_time = config.block_time
        blockchain.base_fee_per_gas = config.base_fee
        
        # Update genesis block with chain-specific settings
        genesis = blockchain.blocks[0]
        genesis.gas_limit = f"0x{config.gas_limit:x}"
        
        self.chains[config.chain_id] = blockchain
        self.rpc_engines[config.chain_id] = JSONRPCEngine(blockchain)
        self.chain_configs[config.chain_id] = config
        
    def get_chain(self, chain_id: int) -> Optional[BlockchainState]:
        return self.chains.get(chain_id)
        
    def get_rpc_engine(self, chain_id: int) -> Optional[JSONRPCEngine]:
        return self.rpc_engines.get(chain_id)
        
    def get_chain_config(self, chain_id: int) -> Optional[ChainConfig]:
        return self.chain_configs.get(chain_id)
        
    async def start_all_chains(self):
        for blockchain in self.chains.values():
            await blockchain.start_mining()
            
    async def stop_all_chains(self):
        for blockchain in self.chains.values():
            await blockchain.stop_mining()
            
    def list_chains(self) -> Dict[int, Dict[str, Any]]:
        return {
            chain_id: {
                "chain_id": config.chain_id,
                "name": config.name,
                "native_currency": config.native_currency,
                "block_time": config.block_time,
                "current_block": self.chains[chain_id].current_block_number,
                "base_fee": self.chains[chain_id].base_fee_per_gas,
            }
            for chain_id, config in self.chain_configs.items()
        }