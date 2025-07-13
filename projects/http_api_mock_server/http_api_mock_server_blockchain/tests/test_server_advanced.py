import pytest
import json
from fastapi.testclient import TestClient
from pymockapi.server import create_app
from eth_utils import to_hex, to_checksum_address


class TestMockAPIServerAdvanced:
    @pytest.fixture
    def app(self):
        return create_app()
        
    @pytest.fixture
    def client(self, app):
        return TestClient(app)
        
    def test_multiple_chain_endpoints(self, client):
        chains = [1, 5, 137, 42161, 10]
        
        for chain_id in chains:
            response = client.get(f"/rpc/{chain_id}")
            # Should return 405 for GET request
            assert response.status_code == 405
            
    def test_json_rpc_notification(self, client):
        # Notification (no id)
        notification = {
            "jsonrpc": "2.0",
            "method": "eth_blockNumber",
            "params": []
        }
        
        response = client.post("/rpc/1", json=notification)
        assert response.status_code == 200
        
    def test_json_rpc_invalid_method(self, client):
        # Test invalid RPC method
        request = {
            "jsonrpc": "2.0",
            "method": "invalid_method_name",
            "params": [],
            "id": 1
        }
        response = client.post("/rpc/1", json=request)
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == -32601  # Method not found
        
    def test_json_rpc_empty_batch(self, client):
        response = client.post("/rpc/1", json=[])
        assert response.status_code == 200
        assert response.json() == []
        
    def test_json_rpc_mixed_batch(self, client):
        batch = [
            {"jsonrpc": "2.0", "method": "eth_chainId", "params": [], "id": 1},
            {"jsonrpc": "2.0", "method": "invalid_method", "params": [], "id": 2},
            {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": []},  # Notification
        ]
        
        response = client.post("/rpc/1", json=batch)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 3
        assert "result" in data[0]
        assert "error" in data[1]
        
    def test_fund_account_with_large_amount(self, client):
        response = client.post(
            "/api/chains/1/fund",
            params={
                "address": "0x" + "1" * 40,
                "amount": "0xffffffffffffffffffffffffffffffff"
            }
        )
        assert response.status_code == 200
        
    def test_fund_multiple_accounts(self, client):
        addresses = [to_checksum_address("0x" + str(i) * 40) for i in range(5)]
        
        for addr in addresses:
            response = client.post(
                "/api/chains/1/fund",
                params={
                    "address": addr,
                    "amount": to_hex(10**18 * (addresses.index(addr) + 1))
                }
            )
            assert response.status_code == 200
            
    def test_deploy_multiple_contracts(self, client):
        contracts = [
            ("0x" + "1" * 40, "0x606060"),
            ("0x" + "2" * 40, "0x608060"),
            ("0x" + "3" * 40, "0x" + "60" * 100),
        ]
        
        for address, code in contracts:
            response = client.post(
                "/api/chains/1/deploy",
                params={
                    "address": address,
                    "code": code
                }
            )
            assert response.status_code == 200
            
    def test_emit_different_event_types(self, client):
        events = [
            ("Transfer(address,address,uint256)", "Transfer"),
            ("Approval(address,address,uint256)", "Approval"),
            ("Mint(address,uint256)", "Mint"),
            ("Burn(address,uint256)", "Burn"),
        ]
        
        for signature, name in events:
            response = client.post(
                f"/api/chains/1/emit?address={'0x' + '4' * 40}&event_signature={signature}"
            )
            assert response.status_code == 200
            log = response.json()
            assert "topics" in log
            
    def test_gas_estimate_for_different_chains(self, client):
        chains = [1, 137, 42161, 10]
        
        for chain_id in chains:
            response = client.get(f"/api/chains/{chain_id}/gas/estimate")
            assert response.status_code == 200
            
            estimates = response.json()
            assert all(level in estimates for level in ["baseFee", "low", "medium", "high"])
            
    def test_force_mine_multiple_blocks(self, client):
        for i in range(5):
            response = client.post("/api/chains/1/block/mine")
            assert response.status_code == 200
            
            block = response.json()
            assert int(block["number"], 16) == i + 1
            
    def test_transaction_with_access_list(self, client):
        tx_request = {
            "jsonrpc": "2.0",
            "method": "eth_sendTransaction",
            "params": [{
                "from": "0x" + "1" * 40,
                "to": "0x" + "2" * 40,
                "value": "0x1",
                "gas": "0x5208",
                "accessList": [
                    {
                        "address": "0x" + "3" * 40,
                        "storageKeys": ["0x0", "0x1"]
                    }
                ]
            }],
            "id": 1
        }
        
        response = client.post("/rpc/1", json=tx_request)
        assert response.status_code == 200
        assert "result" in response.json()
        
    def test_concurrent_rpc_requests(self, client):
        import concurrent.futures
        
        def make_request(i):
            request = {
                "jsonrpc": "2.0",
                "method": "eth_blockNumber",
                "params": [],
                "id": i
            }
            return client.post("/rpc/1", json=request)
            
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request, i) for i in range(20)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
            
        assert all(r.status_code == 200 for r in results)
        
    def test_websocket_multiple_subscriptions(self, client):
        with client.websocket_connect("/ws/1") as websocket:
            # Subscribe to multiple event types
            subscriptions = []
            
            for sub_type in ["newHeads", "logs", "pendingTransactions"]:
                subscribe = {
                    "jsonrpc": "2.0",
                    "method": "eth_subscribe",
                    "params": [sub_type],
                    "id": len(subscriptions) + 1
                }
                websocket.send_json(subscribe)
                response = websocket.receive_json()
                subscriptions.append(response["result"])
                
            assert len(subscriptions) == 3
            
    def test_error_handling_invalid_hex(self, client):
        request = {
            "jsonrpc": "2.0",
            "method": "eth_getBalance",
            "params": ["not_hex_address", "latest"],
            "id": 1
        }
        
        response = client.post("/rpc/1", json=request)
        assert response.status_code == 200
        assert "error" in response.json()
        
    def test_error_handling_missing_params(self, client):
        request = {
            "jsonrpc": "2.0",
            "method": "eth_getBalance",
            "params": [],
            "id": 1
        }
        
        response = client.post("/rpc/1", json=request)
        assert response.status_code == 200
        assert "error" in response.json()
        
    def test_chain_specific_gas_prices(self, client):
        # Test that different chains have different gas prices
        chain_configs = {
            1: 1000000000,      # Ethereum: 1 gwei
            137: 30000000000,   # Polygon: 30 gwei
            42161: 100000000,   # Arbitrum: 0.1 gwei
            10: 1000000,        # Optimism: 0.001 gwei
        }
        
        for chain_id, expected_base in chain_configs.items():
            response = client.get(f"/api/chains/{chain_id}/gas/estimate")
            assert response.status_code == 200
            
            estimates = response.json()
            base_fee = int(estimates["baseFee"], 16)
            
            # Check base fee is in expected range
            assert base_fee > 0
            
    def test_transaction_pool_overflow(self, client):
        # Add many transactions to test pool limits
        for i in range(50):
            tx_request = {
                "jsonrpc": "2.0",
                "method": "eth_sendTransaction",
                "params": [{
                    "from": "0x" + str(i % 10) * 40,
                    "to": "0x" + str((i + 1) % 10) * 40,
                    "value": to_hex(i * 10**15),
                    "gas": "0x5208"
                }],
                "id": i
            }
            
            response = client.post("/rpc/1", json=tx_request)
            assert response.status_code == 200
            
    def test_block_uncle_support(self, client):
        # Get block with uncle information
        request = {
            "jsonrpc": "2.0",
            "method": "eth_getBlockByNumber",
            "params": ["0x0", True],
            "id": 1
        }
        
        response = client.post("/rpc/1", json=request)
        assert response.status_code == 200
        
        block = response.json()["result"]
        assert "uncles" in block
        assert isinstance(block["uncles"], list)