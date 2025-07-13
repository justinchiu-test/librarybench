import pytest
import json
import asyncio
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect
from pymockapi.server import create_app


class TestMockAPIServer:
    @pytest.fixture
    def app(self):
        return create_app()
        
    @pytest.fixture
    def client(self, app):
        return TestClient(app)
        
    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "PyMockAPI"
        assert "chains" in data
        assert len(data["chains"]) >= 5
        
    def test_json_rpc_endpoint(self, client):
        # Test eth_chainId
        request = {
            "jsonrpc": "2.0",
            "method": "eth_chainId",
            "params": [],
            "id": 1
        }
        
        response = client.post("/rpc/1", json=request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["result"] == "0x1"
        
    def test_json_rpc_batch_request(self, client):
        batch = [
            {"jsonrpc": "2.0", "method": "eth_chainId", "params": [], "id": 1},
            {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 2},
        ]
        
        response = client.post("/rpc/1", json=batch)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
        assert data[0]["id"] == 1
        assert data[1]["id"] == 2
        
    def test_invalid_chain_id(self, client):
        request = {
            "jsonrpc": "2.0",
            "method": "eth_chainId",
            "params": [],
            "id": 1
        }
        
        response = client.post("/rpc/99999", json=request)
        assert response.status_code == 404
        
    def test_fund_account_endpoint(self, client):
        response = client.post(
            "/api/chains/1/fund",
            params={
                "address": "0x" + "1" * 40,
                "amount": "0x1234"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["balance"] == "0x1234"
        
        # Verify balance was set
        request = {
            "jsonrpc": "2.0",
            "method": "eth_getBalance",
            "params": ["0x" + "1" * 40, "latest"],
            "id": 1
        }
        response = client.post("/rpc/1", json=request)
        data = response.json()
        assert data["result"] == "0x1234"
        
    def test_deploy_contract_endpoint(self, client):
        response = client.post(
            "/api/chains/1/deploy",
            params={
                "address": "0x" + "2" * 40,
                "code": "0x606060"
            }
        )
        assert response.status_code == 200
        
        # Verify code was set
        request = {
            "jsonrpc": "2.0",
            "method": "eth_getCode",
            "params": ["0x" + "2" * 40, "latest"],
            "id": 1
        }
        response = client.post("/rpc/1", json=request)
        data = response.json()
        assert data["result"] == "0x606060"
        
    def test_emit_event_endpoint(self, client):
        response = client.post(
            f"/api/chains/1/emit?address={'0x' + '3' * 40}&event_signature=Transfer(address,address,uint256)"
        )
        assert response.status_code == 200
        
        log = response.json()
        assert log["address"] == "0x" + "3" * 40
        # Without indexed params, should have only event signature topic
        assert len(log["topics"]) == 1
        
    def test_gas_estimate_endpoint(self, client):
        response = client.get("/api/chains/1/gas/estimate")
        assert response.status_code == 200
        
        estimates = response.json()
        assert "baseFee" in estimates
        assert "low" in estimates
        assert "medium" in estimates
        assert "high" in estimates
        
    def test_force_mine_block_endpoint(self, client):
        # Get current block number
        request = {
            "jsonrpc": "2.0",
            "method": "eth_blockNumber",
            "params": [],
            "id": 1
        }
        response = client.post("/rpc/1", json=request)
        initial_block = int(response.json()["result"], 16)
        
        # Force mine a block
        response = client.post("/api/chains/1/block/mine")
        assert response.status_code == 200
        
        block = response.json()
        assert int(block["number"], 16) == initial_block + 1
        
    def test_websocket_subscription(self, client):
        with client.websocket_connect("/ws/1") as websocket:
            # Subscribe to new heads
            subscribe = {
                "jsonrpc": "2.0",
                "method": "eth_subscribe",
                "params": ["newHeads"],
                "id": 1
            }
            websocket.send_json(subscribe)
            
            response = websocket.receive_json()
            assert "result" in response
            subscription_id = response["result"]
            
            # Unsubscribe
            unsubscribe = {
                "jsonrpc": "2.0",
                "method": "eth_unsubscribe",
                "params": [subscription_id],
                "id": 2
            }
            websocket.send_json(unsubscribe)
            
            response = websocket.receive_json()
            assert response["result"] is True
                
    def test_websocket_invalid_chain(self, client):
        with pytest.raises(WebSocketDisconnect) as exc_info:
            with client.websocket_connect("/ws/99999") as websocket:
                pass
                
    def test_transaction_lifecycle(self, client):
        # Send transaction
        tx_request = {
            "jsonrpc": "2.0",
            "method": "eth_sendTransaction",
            "params": [{
                "from": "0x" + "1" * 40,
                "to": "0x" + "2" * 40,
                "value": "0x1",
                "gas": "0x5208"
            }],
            "id": 1
        }
        
        response = client.post("/rpc/1", json=tx_request)
        tx_hash = response.json()["result"]
        
        # Check transaction is pending
        get_tx_request = {
            "jsonrpc": "2.0",
            "method": "eth_getTransactionByHash",
            "params": [tx_hash],
            "id": 2
        }
        
        response = client.post("/rpc/1", json=get_tx_request)
        tx = response.json()["result"]
        assert tx["hash"] == tx_hash
        assert tx["blockNumber"] is None  # Still pending
        
        # Mine a block
        client.post("/api/chains/1/block/mine")
        
        # Check transaction receipt
        receipt_request = {
            "jsonrpc": "2.0",
            "method": "eth_getTransactionReceipt",
            "params": [tx_hash],
            "id": 3
        }
        
        response = client.post("/rpc/1", json=receipt_request)
        receipt = response.json()["result"]
        assert receipt["transactionHash"] == tx_hash
        assert receipt["status"] == "0x1"  # Success