import pytest
from eth_utils import to_hex, to_int, to_checksum_address
from pymockapi.blockchain import BlockchainState
from pymockapi.rpc_engine import JSONRPCEngine


class TestJSONRPCEngine:
    @pytest.fixture
    def blockchain(self):
        return BlockchainState(chain_id=1)
        
    @pytest.fixture
    def rpc_engine(self, blockchain):
        return JSONRPCEngine(blockchain)
        
    @pytest.mark.asyncio
    async def test_eth_chain_id(self, rpc_engine):
        request = {"method": "eth_chainId", "params": [], "id": 1}
        response = await rpc_engine.handle_request(request)
        
        assert response["result"] == "0x1"
        assert response["id"] == 1
        
    @pytest.mark.asyncio
    async def test_eth_block_number(self, rpc_engine, blockchain):
        request = {"method": "eth_blockNumber", "params": [], "id": 1}
        response = await rpc_engine.handle_request(request)
        
        assert response["result"] == "0x0"
        
        # Mine a block
        blockchain._mine_new_block()
        response = await rpc_engine.handle_request(request)
        assert response["result"] == "0x1"
        
    @pytest.mark.asyncio
    async def test_eth_get_block_by_number(self, rpc_engine, blockchain):
        # Get genesis block
        request = {"method": "eth_getBlockByNumber", "params": ["0x0", False], "id": 1}
        response = await rpc_engine.handle_request(request)
        
        block = response["result"]
        assert block["number"] == "0x0"
        assert block["parentHash"] == "0x" + "0" * 64
        
        # Test with full transactions
        request["params"][1] = True
        response = await rpc_engine.handle_request(request)
        assert isinstance(response["result"]["transactions"], list)
        
    @pytest.mark.asyncio
    async def test_eth_get_block_by_hash(self, rpc_engine, blockchain):
        genesis_hash = blockchain.blocks[0].hash
        
        request = {"method": "eth_getBlockByHash", "params": [genesis_hash, False], "id": 1}
        response = await rpc_engine.handle_request(request)
        
        block = response["result"]
        assert block["hash"] == genesis_hash
        assert block["number"] == "0x0"
        
    @pytest.mark.asyncio
    async def test_eth_send_transaction(self, rpc_engine, blockchain):
        tx_data = {
            "from": "0x" + "1" * 40,
            "to": "0x" + "2" * 40,
            "value": "0x1",
            "gas": "0x5208",
        }
        
        request = {"method": "eth_sendTransaction", "params": [tx_data], "id": 1}
        response = await rpc_engine.handle_request(request)
        
        tx_hash = response["result"]
        assert tx_hash.startswith("0x")
        assert tx_hash in blockchain.transactions
        
    @pytest.mark.asyncio
    async def test_eth_get_transaction_by_hash(self, rpc_engine, blockchain):
        # Add a transaction
        tx_data = {
            "from": "0x" + "1" * 40,
            "to": "0x" + "2" * 40,
            "value": "0x1",
        }
        tx_hash = blockchain.add_transaction(tx_data)
        
        request = {"method": "eth_getTransactionByHash", "params": [tx_hash], "id": 1}
        response = await rpc_engine.handle_request(request)
        
        tx = response["result"]
        assert tx["hash"] == tx_hash
        assert tx["from"] == to_checksum_address("0x" + "1" * 40)
        assert tx["to"] == to_checksum_address("0x" + "2" * 40)
        
    @pytest.mark.asyncio
    async def test_eth_get_transaction_receipt(self, rpc_engine, blockchain):
        # Add and mine a transaction
        tx_data = {
            "from": "0x" + "1" * 40,
            "to": "0x" + "2" * 40,
            "value": "0x1",
        }
        tx_hash = blockchain.add_transaction(tx_data)
        blockchain._mine_new_block()
        
        request = {"method": "eth_getTransactionReceipt", "params": [tx_hash], "id": 1}
        response = await rpc_engine.handle_request(request)
        
        receipt = response["result"]
        assert receipt["transactionHash"] == tx_hash
        assert receipt["status"] == "0x1"
        assert receipt["blockNumber"] == "0x1"
        
    @pytest.mark.asyncio
    async def test_eth_estimate_gas(self, rpc_engine):
        # Simple transfer
        tx_data = {
            "from": "0x" + "1" * 40,
            "to": "0x" + "2" * 40,
            "value": "0x1",
        }
        
        request = {"method": "eth_estimateGas", "params": [tx_data], "id": 1}
        response = await rpc_engine.handle_request(request)
        
        gas = to_int(hexstr=response["result"])
        assert gas >= 21000
        
        # Contract interaction
        tx_data["data"] = "0x" + "a" * 100
        response = await rpc_engine.handle_request(request)
        gas_with_data = to_int(hexstr=response["result"])
        assert gas_with_data > gas
        
    @pytest.mark.asyncio
    async def test_eth_gas_price(self, rpc_engine, blockchain):
        request = {"method": "eth_gasPrice", "params": [], "id": 1}
        response = await rpc_engine.handle_request(request)
        
        assert response["result"] == to_hex(blockchain.base_fee_per_gas)
        
    @pytest.mark.asyncio
    async def test_eth_get_balance(self, rpc_engine, blockchain):
        address = "0x" + "1" * 40
        blockchain.set_balance(address, "0x1234")
        
        request = {"method": "eth_getBalance", "params": [address, "latest"], "id": 1}
        response = await rpc_engine.handle_request(request)
        
        assert response["result"] == "0x1234"
        
    @pytest.mark.asyncio
    async def test_eth_get_code(self, rpc_engine, blockchain):
        address = "0x" + "1" * 40
        code = "0x606060"
        blockchain.set_code(address, code)
        
        request = {"method": "eth_getCode", "params": [address, "latest"], "id": 1}
        response = await rpc_engine.handle_request(request)
        
        assert response["result"] == code
        
    @pytest.mark.asyncio
    async def test_eth_get_storage_at(self, rpc_engine, blockchain):
        address = "0x" + "1" * 40
        position = "0x0"
        value = "0x" + "f" * 64
        blockchain.set_storage_at(address, position, value)
        
        request = {"method": "eth_getStorageAt", "params": [address, position, "latest"], "id": 1}
        response = await rpc_engine.handle_request(request)
        
        assert response["result"] == value
        
    @pytest.mark.asyncio
    async def test_eth_get_transaction_count(self, rpc_engine, blockchain):
        address = "0x" + "1" * 40
        
        request = {"method": "eth_getTransactionCount", "params": [address, "latest"], "id": 1}
        response = await rpc_engine.handle_request(request)
        
        assert response["result"] == "0x0"
        
        # Add transaction
        tx_data = {"from": address, "to": "0x" + "2" * 40, "value": "0x0"}
        blockchain.add_transaction(tx_data)
        
        response = await rpc_engine.handle_request(request)
        assert response["result"] == "0x1"
        
    @pytest.mark.asyncio
    async def test_filter_operations(self, rpc_engine):
        # New filter
        request = {"method": "eth_newFilter", "params": [{"fromBlock": "0x0"}], "id": 1}
        response = await rpc_engine.handle_request(request)
        
        filter_id = response["result"]
        assert filter_id.startswith("0x")
        
        # Get filter changes
        request = {"method": "eth_getFilterChanges", "params": [filter_id], "id": 2}
        response = await rpc_engine.handle_request(request)
        assert isinstance(response["result"], list)
        
        # Uninstall filter
        request = {"method": "eth_uninstallFilter", "params": [filter_id], "id": 3}
        response = await rpc_engine.handle_request(request)
        assert response["result"] is True
        
    @pytest.mark.asyncio
    async def test_eth_fee_history(self, rpc_engine, blockchain):
        # Mine some blocks
        for _ in range(3):
            blockchain._mine_new_block()
            
        request = {
            "method": "eth_feeHistory",
            "params": [3, "latest", [25, 50, 75]],
            "id": 1
        }
        response = await rpc_engine.handle_request(request)
        
        result = response["result"]
        assert "baseFeePerGas" in result
        assert "gasUsedRatio" in result
        assert "reward" in result
        assert len(result["baseFeePerGas"]) == 4  # 3 blocks + next
        assert len(result["gasUsedRatio"]) == 3
        assert len(result["reward"]) == 3
        
    @pytest.mark.asyncio
    async def test_web3_client_version(self, rpc_engine):
        request = {"method": "web3_clientVersion", "params": [], "id": 1}
        response = await rpc_engine.handle_request(request)
        
        assert "PyMockAPI" in response["result"]
        
    @pytest.mark.asyncio
    async def test_error_handling(self, rpc_engine):
        # Unknown method
        request = {"method": "unknown_method", "params": [], "id": 1}
        response = await rpc_engine.handle_request(request)
        
        assert "error" in response
        assert response["error"]["code"] == -32601
        assert "Method not found" in response["error"]["message"]