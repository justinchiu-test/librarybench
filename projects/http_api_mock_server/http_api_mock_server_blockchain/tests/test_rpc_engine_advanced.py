import pytest
from eth_utils import to_hex, to_int, to_checksum_address, keccak
from pymockapi.blockchain import BlockchainState
from pymockapi.rpc_engine import JSONRPCEngine


class TestJSONRPCEngineAdvanced:
    @pytest.fixture
    def blockchain(self):
        return BlockchainState(chain_id=1)
        
    @pytest.fixture
    def rpc_engine(self, blockchain):
        return JSONRPCEngine(blockchain)
        
    @pytest.mark.asyncio
    async def test_eth_syncing_response(self, rpc_engine):
        request = {"method": "eth_syncing", "params": [], "id": 1}
        response = await rpc_engine.handle_request(request)
        
        # Should return false when not syncing
        assert response["result"] is False
        
    @pytest.mark.asyncio
    async def test_eth_mining_response(self, rpc_engine):
        request = {"method": "eth_mining", "params": [], "id": 1}
        response = await rpc_engine.handle_request(request)
        
        # Should return mining status
        assert isinstance(response["result"], bool)
        
    @pytest.mark.asyncio
    async def test_eth_hashrate_response(self, rpc_engine):
        request = {"method": "eth_hashrate", "params": [], "id": 1}
        response = await rpc_engine.handle_request(request)
        
        assert response["result"] == "0x0"
        
    @pytest.mark.asyncio
    async def test_eth_accounts_response(self, rpc_engine, blockchain):
        # Add some accounts
        for i in range(3):
            blockchain.set_balance("0x" + str(i) * 40, "0x1")
            
        request = {"method": "eth_accounts", "params": [], "id": 1}
        response = await rpc_engine.handle_request(request)
        
        assert len(response["result"]) == 3
        
    @pytest.mark.asyncio
    async def test_eth_coinbase_response(self, rpc_engine):
        request = {"method": "eth_coinbase", "params": [], "id": 1}
        response = await rpc_engine.handle_request(request)
        
        assert response["result"] == to_checksum_address("0x" + "1" * 40)
        
    @pytest.mark.asyncio
    async def test_net_version_response(self, rpc_engine):
        request = {"method": "net_version", "params": [], "id": 1}
        response = await rpc_engine.handle_request(request)
        
        assert response["result"] == "1"
        
    @pytest.mark.asyncio
    async def test_net_listening_response(self, rpc_engine):
        request = {"method": "net_listening", "params": [], "id": 1}
        response = await rpc_engine.handle_request(request)
        
        assert response["result"] is True
        
    @pytest.mark.asyncio
    async def test_net_peer_count_response(self, rpc_engine):
        request = {"method": "net_peerCount", "params": [], "id": 1}
        response = await rpc_engine.handle_request(request)
        
        assert response["result"] == "0x0"
        
    @pytest.mark.asyncio
    async def test_web3_sha3_response(self, rpc_engine):
        data = "0x68656c6c6f20776f726c64"  # "hello world"
        request = {"method": "web3_sha3", "params": [data], "id": 1}
        response = await rpc_engine.handle_request(request)
        
        # Verify keccak256 hash
        expected = to_hex(keccak(hexstr=data))
        assert response["result"] == expected
        
    @pytest.mark.asyncio
    async def test_eth_max_priority_fee_per_gas(self, rpc_engine):
        request = {"method": "eth_maxPriorityFeePerGas", "params": [], "id": 1}
        response = await rpc_engine.handle_request(request)
        
        assert response["result"] == to_hex(1000000000)  # 1 gwei
        
    @pytest.mark.asyncio
    async def test_eth_get_block_by_number_edge_cases(self, rpc_engine):
        # Test "earliest" block
        request = {"method": "eth_getBlockByNumber", "params": ["earliest", False], "id": 1}
        response = await rpc_engine.handle_request(request)
        
        assert response["result"]["number"] == "0x0"
        
        # Test "pending" block (should be None)
        request = {"method": "eth_getBlockByNumber", "params": ["pending", False], "id": 2}
        response = await rpc_engine.handle_request(request)
        
        assert response["result"] is None
        
        # Test non-existent block
        request = {"method": "eth_getBlockByNumber", "params": ["0x999999", False], "id": 3}
        response = await rpc_engine.handle_request(request)
        
        assert response["result"] is None
        
    @pytest.mark.asyncio
    async def test_eth_get_transaction_by_block_number_and_index(self, rpc_engine, blockchain):
        # Add and mine transaction
        tx_data = {
            "from": "0x" + "1" * 40,
            "to": "0x" + "2" * 40,
            "value": "0x1",
        }
        tx_hash = blockchain.add_transaction(tx_data)
        blockchain._mine_new_block()
        
        # Get transaction by block number and index
        request = {
            "method": "eth_getTransactionByBlockNumberAndIndex",
            "params": ["0x1", "0x0"],
            "id": 1
        }
        response = await rpc_engine.handle_request(request)
        
        # Method not implemented, should return error
        assert "error" in response
        
    @pytest.mark.asyncio
    async def test_eth_send_raw_transaction(self, rpc_engine):
        # Mock raw transaction
        raw_tx = "0xf86c0185..." # Incomplete for mock
        
        request = {"method": "eth_sendRawTransaction", "params": [raw_tx], "id": 1}
        response = await rpc_engine.handle_request(request)
        
        # Should return transaction hash
        assert response["result"].startswith("0x")
        assert len(response["result"]) == 66
        
    @pytest.mark.asyncio
    async def test_eth_call_with_block_parameter(self, rpc_engine, blockchain):
        call_data = {
            "from": "0x" + "1" * 40,
            "to": "0x" + "2" * 40,
            "data": "0x12345678",
        }
        
        # Test with different block parameters
        for block_param in ["latest", "earliest", "0x0"]:
            request = {"method": "eth_call", "params": [call_data, block_param], "id": 1}
            response = await rpc_engine.handle_request(request)
            
            assert response["result"] == "0x"
            
    @pytest.mark.asyncio
    async def test_eth_estimate_gas_edge_cases(self, rpc_engine):
        # Estimate gas for contract creation
        tx_data = {
            "from": "0x" + "1" * 40,
            "data": "0x" + "60" * 1000,  # Large bytecode
        }
        
        request = {"method": "eth_estimateGas", "params": [tx_data], "id": 1}
        response = await rpc_engine.handle_request(request)
        
        gas = to_int(hexstr=response["result"])
        assert gas > 32000  # Should include contract creation cost
        
    @pytest.mark.asyncio
    async def test_eth_get_logs_pagination(self, rpc_engine, blockchain):
        # Add many logs
        from pymockapi.models import Log
        for i in range(20):
            log = Log(
                address=to_checksum_address("0x" + "1" * 40),
                topics=["0x" + "a" * 64],
                data="0x" + str(i).zfill(64),
                block_number=i // 5,
                transaction_hash="0x" + str(i) * 64,
                transaction_index=i % 5,
                block_hash="0x" + "b" * 64,
                log_index=i,
            )
            blockchain.add_log(log)
            
        # Get logs with block range
        request = {
            "method": "eth_getLogs",
            "params": [{
                "fromBlock": "0x0",
                "toBlock": "0x2",
            }],
            "id": 1
        }
        response = await rpc_engine.handle_request(request)
        
        # Should return logs from blocks 0-2
        assert len(response["result"]) <= 15
        
    @pytest.mark.asyncio
    async def test_filter_lifecycle(self, rpc_engine):
        # Create filter
        create_request = {
            "method": "eth_newFilter",
            "params": [{"fromBlock": "0x0"}],
            "id": 1
        }
        create_response = await rpc_engine.handle_request(create_request)
        filter_id = create_response["result"]
        
        # Get logs from filter
        get_logs_request = {
            "method": "eth_getFilterLogs",
            "params": [filter_id],
            "id": 2
        }
        get_logs_response = await rpc_engine.handle_request(get_logs_request)
        assert isinstance(get_logs_response["result"], list)
        
        # Get changes
        get_changes_request = {
            "method": "eth_getFilterChanges",
            "params": [filter_id],
            "id": 3
        }
        get_changes_response = await rpc_engine.handle_request(get_changes_request)
        assert isinstance(get_changes_response["result"], list)
        
        # Uninstall filter
        uninstall_request = {
            "method": "eth_uninstallFilter",
            "params": [filter_id],
            "id": 4
        }
        uninstall_response = await rpc_engine.handle_request(uninstall_request)
        assert uninstall_response["result"] is True
        
        # Try to use uninstalled filter
        get_logs_response2 = await rpc_engine.handle_request(get_logs_request)
        assert get_logs_response2["result"] == []
        
    @pytest.mark.asyncio
    async def test_batch_request_handling(self, rpc_engine):
        # Single request (not a batch)
        single_request = {"method": "eth_blockNumber", "params": [], "id": 1}
        response = await rpc_engine.handle_request(single_request)
        
        assert "result" in response
        assert response["id"] == 1
        
    @pytest.mark.asyncio
    async def test_missing_optional_parameters(self, rpc_engine):
        # eth_getBalance without block parameter
        request = {"method": "eth_getBalance", "params": ["0x" + "1" * 40], "id": 1}
        response = await rpc_engine.handle_request(request)
        
        assert "result" in response
        
        # eth_getCode without block parameter
        request = {"method": "eth_getCode", "params": ["0x" + "1" * 40], "id": 2}
        response = await rpc_engine.handle_request(request)
        
        assert "result" in response
        
    @pytest.mark.asyncio
    async def test_invalid_address_format(self, rpc_engine):
        # Invalid address (not checksummed)
        request = {
            "method": "eth_getBalance",
            "params": ["0x" + "g" * 40, "latest"],  # Invalid hex
            "id": 1
        }
        response = await rpc_engine.handle_request(request)
        
        assert "error" in response
        
    @pytest.mark.asyncio
    async def test_eth_fee_history_edge_cases(self, rpc_engine, blockchain):
        # Request more blocks than exist
        request = {
            "method": "eth_feeHistory",
            "params": [100, "latest", []],
            "id": 1
        }
        response = await rpc_engine.handle_request(request)
        
        result = response["result"]
        assert len(result["baseFeePerGas"]) <= 2  # Only genesis + next
        
    @pytest.mark.asyncio
    async def test_null_id_handling(self, rpc_engine):
        request = {"method": "eth_blockNumber", "params": [], "id": None}
        response = await rpc_engine.handle_request(request)
        
        assert response["id"] is None
        assert "result" in response