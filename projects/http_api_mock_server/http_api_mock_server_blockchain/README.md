# PyMockAPI - Blockchain RPC Mock Server

A specialized HTTP API mock server designed for blockchain developers to mock Web3 RPC endpoints and smart contract interactions. This implementation focuses on simulating blockchain behaviors including transaction mining, event emissions, and gas estimations, enabling comprehensive testing of decentralized application (dApp) frontends.

## Features

- **Complete Ethereum JSON-RPC Implementation**: Supports all standard Ethereum RPC methods with automatic block progression
- **Transaction Lifecycle Simulation**: Realistic mempool behavior, mining delays, and confirmation counts
- **Smart Contract Events**: Event generation with proper log indexing, bloom filters, and topic filtering
- **EIP-1559 Gas Oracle**: Dynamic gas pricing with base fee calculations and priority fee estimation
- **Multi-Chain Support**: Simulate multiple blockchains (Ethereum, Polygon, Arbitrum, Optimism) with different parameters
- **WebSocket Subscriptions**: Real-time updates for new blocks, logs, and pending transactions
- **REST API**: Additional endpoints for test configuration and blockchain manipulation

## Installation

1. Create a virtual environment:
```bash
uv venv
source .venv/bin/activate
```

2. Install the package:
```bash
uv pip install -e ".[dev]"
```

## Usage

### Starting the Server

Run the mock server:
```bash
python -m pymockapi
```

The server will start on `http://localhost:8545` with the following endpoints:
- JSON-RPC: `http://localhost:8545/rpc/{chain_id}`
- WebSocket: `ws://localhost:8545/ws/{chain_id}`
- REST API: `http://localhost:8545/api/`

### Supported Chains

Default chains available:
- Ethereum Mainnet (chain_id: 1)
- Goerli Testnet (chain_id: 5)  
- Polygon (chain_id: 137)
- Arbitrum One (chain_id: 42161)
- Optimism (chain_id: 10)

### Using with Web3.py

```python
from web3 import Web3

# Connect to Ethereum mainnet mock
w3 = Web3(Web3.HTTPProvider("http://localhost:8545/rpc/1"))

# Check connection
print(w3.is_connected())  # True
print(w3.eth.chain_id)    # 1

# Get latest block
block = w3.eth.get_block("latest")
print(f"Block number: {block['number']}")

# Send transaction
tx_hash = w3.eth.send_transaction({
    "from": "0x742d35Cc6634C0532925a3b844Bc9e7595f6aE3",
    "to": "0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed",
    "value": w3.to_wei(1, "ether"),
    "gas": 21000,
    "gasPrice": w3.eth.gas_price
})
```

### REST API Endpoints

#### Fund an Account
```bash
curl -X POST "http://localhost:8545/api/chains/1/fund?address=0x742d35Cc6634C0532925a3b844Bc9e7595f6aE3&amount=0x3635c9adc5dea00000"
```

#### Deploy Contract Code
```bash
curl -X POST "http://localhost:8545/api/chains/1/deploy?address=0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed&code=0x606060"
```

#### Emit Event
```bash
curl -X POST "http://localhost:8545/api/chains/1/emit" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f6aE3",
    "event_signature": "Transfer(address,address,uint256)",
    "indexed_params": ["0x0000000000000000000000000000000000000001", "0x0000000000000000000000000000000000000002"],
    "data_params": [1000000000000000000]
  }'
```

#### Get Gas Estimates
```bash
curl "http://localhost:8545/api/chains/1/gas/estimate"
```

#### Force Mine Block
```bash
curl -X POST "http://localhost:8545/api/chains/1/block/mine"
```

### WebSocket Subscriptions

```javascript
const Web3 = require('web3');
const web3 = new Web3('ws://localhost:8545/ws/1');

// Subscribe to new blocks
web3.eth.subscribe('newBlockHeaders', (error, blockHeader) => {
    if (!error) {
        console.log('New block:', blockHeader.number);
    }
});

// Subscribe to logs
web3.eth.subscribe('logs', {
    address: '0x742d35Cc6634C0532925a3b844Bc9e7595f6aE3',
    topics: []
}, (error, log) => {
    if (!error) {
        console.log('New log:', log);
    }
});
```

## Running Tests

Run all tests with pytest:
```bash
pytest
```

Generate test report:
```bash
pytest --json-report --json-report-file=pytest_results.json
```

Run specific test categories:
```bash
# Unit tests only
pytest tests/test_models.py tests/test_blockchain.py tests/test_rpc_engine.py

# Integration tests
pytest tests/test_server.py tests/test_web3_integration.py
```

## Architecture

The mock server consists of several key components:

1. **BlockchainState**: Manages blockchain state including blocks, transactions, accounts, and contracts
2. **JSONRPCEngine**: Implements all Ethereum JSON-RPC methods
3. **EventEmitter**: Handles smart contract event generation and log filtering
4. **GasOracle**: Simulates dynamic gas pricing with EIP-1559 support
5. **MultiChainRouter**: Routes requests to different blockchain simulations
6. **MockAPIServer**: FastAPI application handling HTTP, WebSocket, and REST endpoints

## Configuration

Each blockchain can be configured with:
- Chain ID
- Block time
- Gas limit
- Base fee
- Native currency symbol

Custom chains can be added programmatically:
```python
from pymockapi.multi_chain import ChainConfig, MultiChainRouter

router = MultiChainRouter()
router.add_chain(ChainConfig(
    chain_id=1337,
    name="Local Testnet",
    native_currency="TEST",
    block_time=1,
    gas_limit=50000000,
    base_fee=1000000000
))
```

## Limitations

- Simplified transaction validation (no signature verification)
- Basic smart contract simulation (no EVM execution)
- Mock gas calculations (not based on actual opcodes)
- No real consensus mechanism
- Limited state persistence (in-memory only)

## License

MIT