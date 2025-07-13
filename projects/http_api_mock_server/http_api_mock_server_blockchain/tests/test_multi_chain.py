import pytest
from pymockapi.multi_chain import MultiChainRouter, ChainConfig


class TestChainConfig:
    def test_chain_config_creation(self):
        config = ChainConfig(
            chain_id=1337,
            name="Test Chain",
            native_currency="TEST",
            block_time=5,
            gas_limit=50000000,
            base_fee=2000000000,
        )
        
        assert config.chain_id == 1337
        assert config.name == "Test Chain"
        assert config.native_currency == "TEST"
        assert config.block_time == 5
        assert config.gas_limit == 50000000
        assert config.base_fee == 2000000000


class TestMultiChainRouter:
    @pytest.fixture
    def router(self):
        return MultiChainRouter()
        
    def test_default_chains(self, router):
        # Check default chains are set up
        assert 1 in router.chains  # Ethereum Mainnet
        assert 5 in router.chains  # Goerli
        assert 137 in router.chains  # Polygon
        assert 42161 in router.chains  # Arbitrum
        assert 10 in router.chains  # Optimism
        
    def test_add_chain(self, router):
        config = ChainConfig(
            chain_id=9999,
            name="Custom Chain",
            native_currency="CUSTOM",
            block_time=3,
        )
        
        router.add_chain(config)
        
        assert 9999 in router.chains
        assert 9999 in router.rpc_engines
        assert 9999 in router.chain_configs
        
        chain = router.get_chain(9999)
        assert chain.chain_id == 9999
        assert chain.block_time == 3
        
    def test_get_chain(self, router):
        chain = router.get_chain(1)
        assert chain is not None
        assert chain.chain_id == 1
        
        # Non-existent chain
        assert router.get_chain(99999) is None
        
    def test_get_rpc_engine(self, router):
        engine = router.get_rpc_engine(1)
        assert engine is not None
        assert engine.blockchain.chain_id == 1
        
    def test_get_chain_config(self, router):
        config = router.get_chain_config(137)  # Polygon
        assert config is not None
        assert config.chain_id == 137
        assert config.name == "Polygon"
        assert config.native_currency == "MATIC"
        
    def test_list_chains(self, router):
        chains = router.list_chains()
        
        assert len(chains) >= 5  # At least the default chains
        assert 1 in chains
        
        # Check chain info structure
        eth_info = chains[1]
        assert eth_info["chain_id"] == 1
        assert eth_info["name"] == "Ethereum Mainnet"
        assert eth_info["native_currency"] == "ETH"
        assert "current_block" in eth_info
        assert "base_fee" in eth_info
        
    @pytest.mark.asyncio
    async def test_start_all_chains(self, router):
        await router.start_all_chains()
        
        # Check that all chains have mining tasks
        for chain in router.chains.values():
            assert chain._mining_task is not None
            
        await router.stop_all_chains()
        
    @pytest.mark.asyncio
    async def test_stop_all_chains(self, router):
        await router.start_all_chains()
        await router.stop_all_chains()
        
        # Check that all mining tasks are stopped
        for chain in router.chains.values():
            assert chain._mining_task is None
            
    def test_chain_specific_settings(self, router):
        # Check Polygon settings
        polygon = router.get_chain(137)
        polygon_config = router.get_chain_config(137)
        
        assert polygon.block_time == 2
        assert polygon.base_fee_per_gas == 30000000000  # 30 gwei
        assert polygon_config.native_currency == "MATIC"
        
        # Check Arbitrum settings
        arbitrum = router.get_chain(42161)
        arbitrum_config = router.get_chain_config(42161)
        
        assert arbitrum.block_time == 1
        assert arbitrum.base_fee_per_gas == 100000000  # 0.1 gwei
        assert arbitrum_config.native_currency == "ETH"
        
        # Check Optimism settings
        optimism = router.get_chain(10)
        optimism_config = router.get_chain_config(10)
        
        assert optimism.block_time == 2
        assert optimism.base_fee_per_gas == 1000000  # 0.001 gwei
        assert optimism_config.native_currency == "ETH"