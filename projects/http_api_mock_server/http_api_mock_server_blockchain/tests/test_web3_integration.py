import pytest
import asyncio
from web3 import Web3
from web3.providers import HTTPProvider
from eth_account import Account
import multiprocessing
import time
import uvicorn
from pymockapi.server import create_app


def run_server():
    app = create_app()
    uvicorn.run(app, host="127.0.0.1", port=8545)


@pytest.fixture(scope="module")
def server():
    # Start server in a separate process
    process = multiprocessing.Process(target=run_server)
    process.start()
    
    # Wait for server to start
    time.sleep(2)
    
    yield
    
    # Cleanup
    process.terminate()
    process.join()


@pytest.fixture
def w3(server):
    return Web3(HTTPProvider("http://127.0.0.1:8545/rpc/1"))


class TestWeb3Integration:
    def test_web3_connection(self, w3):
        assert w3.is_connected()
        assert w3.eth.chain_id == 1
        
    def test_get_block(self, w3):
        block = w3.eth.get_block("latest")
        assert block["number"] >= 0
        assert "hash" in block
        assert "parentHash" in block
        
    def test_get_balance(self, w3):
        address = "0x" + "1" * 40
        balance = w3.eth.get_balance(address)
        assert balance == 10**18  # Default balance
        
    def test_send_transaction(self, w3):
        # Create account
        account = Account.create()
        
        # Fund the account first
        import requests
        requests.post(
            "http://127.0.0.1:8545/api/chains/1/fund",
            params={
                "address": account.address,
                "amount": Web3.to_hex(10**20)  # 100 ETH
            }
        )
        
        # Send transaction
        tx = {
            "from": account.address,
            "to": "0x" + "2" * 40,
            "value": Web3.to_wei(1, "ether"),
            "gas": 21000,
            "gasPrice": w3.eth.gas_price,
        }
        
        tx_hash = w3.eth.send_transaction(tx)
        assert isinstance(tx_hash, bytes)
        
        # Get transaction
        tx_data = w3.eth.get_transaction(tx_hash)
        assert tx_data["from"] == account.address
        assert tx_data["to"] == Web3.to_checksum_address("0x" + "2" * 40)
        
    def test_estimate_gas(self, w3):
        tx = {
            "from": "0x" + "1" * 40,
            "to": "0x" + "2" * 40,
            "value": Web3.to_wei(1, "ether"),
        }
        
        gas = w3.eth.estimate_gas(tx)
        assert gas >= 21000
        
    def test_get_code(self, w3):
        contract_address = "0x" + "3" * 40
        
        # Deploy contract code
        import requests
        requests.post(
            "http://127.0.0.1:8545/api/chains/1/deploy",
            params={
                "address": contract_address,
                "code": "0x606060"
            }
        )
        
        code = w3.eth.get_code(contract_address)
        assert code == b"\x60\x60\x60"
        
    def test_get_transaction_count(self, w3):
        address = "0x" + "1" * 40
        nonce = w3.eth.get_transaction_count(address)
        assert nonce >= 0
        
    def test_filter_logs(self, w3):
        # Create a filter
        filter_params = {
            "fromBlock": 0,
            "toBlock": "latest",
            "address": "0x" + "4" * 40,
        }
        
        logs = w3.eth.get_logs(filter_params)
        assert isinstance(logs, list)
        
    def test_gas_price(self, w3):
        gas_price = w3.eth.gas_price
        assert gas_price > 0
        assert isinstance(gas_price, int)
        
    def test_block_number(self, w3):
        block_number = w3.eth.block_number
        assert isinstance(block_number, int)
        assert block_number >= 0
        
    def test_get_storage_at(self, w3):
        address = "0x" + "5" * 40
        position = 0
        
        value = w3.eth.get_storage_at(address, position)
        assert value == b"\x00" * 32  # Default empty storage
        
    def test_multi_chain_support(self, server):
        # Test different chains
        chains = [1, 5, 137, 42161, 10]
        
        for chain_id in chains:
            w3_chain = Web3(HTTPProvider(f"http://127.0.0.1:8545/rpc/{chain_id}"))
            assert w3_chain.is_connected()
            assert w3_chain.eth.chain_id == chain_id