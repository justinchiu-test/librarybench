from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import JSONResponse
import asyncio
import json
from typing import Dict, List, Optional, Set, Any
import logging

from .multi_chain import MultiChainRouter
from .events import EventEmitter
from .gas_oracle import GasOracle

logger = logging.getLogger(__name__)


class MockAPIServer:
    def __init__(self):
        self.app = FastAPI(title="PyMockAPI - Blockchain RPC Mock Server")
        self.router = MultiChainRouter()
        self.websocket_connections: Dict[int, Set[WebSocket]] = {}
        self.event_emitters: Dict[int, EventEmitter] = {}
        self.gas_oracles: Dict[int, GasOracle] = {}
        self._setup_routes()
        self._setup_components()
        
    def _setup_components(self):
        for chain_id, blockchain in self.router.chains.items():
            self.event_emitters[chain_id] = EventEmitter(blockchain)
            self.gas_oracles[chain_id] = GasOracle(blockchain.base_fee_per_gas)
            self.websocket_connections[chain_id] = set()
            
    def _setup_routes(self):
        @self.app.on_event("startup")
        async def startup():
            await self.router.start_all_chains()
            
        @self.app.on_event("shutdown")
        async def shutdown():
            await self.router.stop_all_chains()
            
        @self.app.get("/")
        async def root():
            return {
                "name": "PyMockAPI",
                "version": "0.1.0",
                "chains": self.router.list_chains(),
            }
            
        @self.app.post("/rpc/{chain_id}")
        async def json_rpc(chain_id: int, request: Request):
            rpc_engine = self.router.get_rpc_engine(chain_id)
            if not rpc_engine:
                raise HTTPException(status_code=404, detail=f"Chain {chain_id} not found")
                
            body = await request.json()
            
            # Handle batch requests
            if isinstance(body, list):
                responses = []
                for req in body:
                    response = await rpc_engine.handle_request(req)
                    responses.append(response)
                return JSONResponse(content=responses)
            else:
                response = await rpc_engine.handle_request(body)
                return JSONResponse(content=response)
                
        @self.app.websocket("/ws/{chain_id}")
        async def websocket_endpoint(websocket: WebSocket, chain_id: int):
            blockchain = self.router.get_chain(chain_id)
            if not blockchain:
                await websocket.close(code=4004, reason=f"Chain {chain_id} not found")
                return
                
            await websocket.accept()
            self.websocket_connections[chain_id].add(websocket)
            
            try:
                rpc_engine = self.router.get_rpc_engine(chain_id)
                subscriptions = {}
                
                while True:
                    data = await websocket.receive_text()
                    request = json.loads(data)
                    
                    if request.get("method") == "eth_subscribe":
                        subscription_type = request["params"][0]
                        subscription_id = f"0x{len(subscriptions):x}"
                        subscriptions[subscription_id] = {
                            "type": subscription_type,
                            "params": request["params"][1:] if len(request["params"]) > 1 else [],
                        }
                        
                        response = {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "result": subscription_id,
                        }
                        await websocket.send_json(response)
                        
                        # Start sending updates for this subscription
                        asyncio.create_task(
                            self._handle_subscription(websocket, blockchain, subscription_id, subscriptions[subscription_id])
                        )
                        
                    elif request.get("method") == "eth_unsubscribe":
                        subscription_id = request["params"][0]
                        success = subscription_id in subscriptions
                        if success:
                            del subscriptions[subscription_id]
                            
                        response = {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "result": success,
                        }
                        await websocket.send_json(response)
                        
                    else:
                        # Regular RPC call
                        response = await rpc_engine.handle_request(request)
                        await websocket.send_json(response)
                        
            except WebSocketDisconnect:
                self.websocket_connections[chain_id].discard(websocket)
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                self.websocket_connections[chain_id].discard(websocket)
                
        @self.app.post("/api/chains/{chain_id}/fund")
        async def fund_account(chain_id: int, address: str, amount: str = "0x3635c9adc5dea00000"):
            blockchain = self.router.get_chain(chain_id)
            if not blockchain:
                raise HTTPException(status_code=404, detail=f"Chain {chain_id} not found")
                
            blockchain.set_balance(address, amount)
            return {"address": address, "balance": amount}
            
        @self.app.post("/api/chains/{chain_id}/deploy")
        async def deploy_contract(chain_id: int, address: str, code: str):
            blockchain = self.router.get_chain(chain_id)
            if not blockchain:
                raise HTTPException(status_code=404, detail=f"Chain {chain_id} not found")
                
            blockchain.set_code(address, code)
            return {"address": address, "code": code}
            
        @self.app.post("/api/chains/{chain_id}/emit")
        async def emit_event(
            chain_id: int,
            address: str,
            event_signature: str,
            indexed_params: List[str] = [],
            data_params: List[Any] = [],
        ):
            blockchain = self.router.get_chain(chain_id)
            event_emitter = self.event_emitters.get(chain_id)
            
            if not blockchain or not event_emitter:
                raise HTTPException(status_code=404, detail=f"Chain {chain_id} not found")
                
            # Use current block info
            current_block = blockchain.blocks[blockchain.current_block_number]
            
            log = event_emitter.emit_event(
                address=address,
                event_signature=event_signature,
                indexed_params=indexed_params,
                data_params=data_params,
                tx_hash="0x" + "f" * 64,  # Mock tx hash
                tx_index=0,
                block_number=blockchain.current_block_number,
                block_hash=current_block.hash,
                log_index=len(blockchain.logs),
            )
            
            return log.to_rpc_format()
            
        @self.app.get("/api/chains/{chain_id}/gas/estimate")
        async def get_gas_estimates(chain_id: int):
            gas_oracle = self.gas_oracles.get(chain_id)
            if not gas_oracle:
                raise HTTPException(status_code=404, detail=f"Chain {chain_id} not found")
                
            return gas_oracle.get_eip1559_estimates()
            
        @self.app.post("/api/chains/{chain_id}/block/mine")
        async def force_mine_block(chain_id: int):
            blockchain = self.router.get_chain(chain_id)
            if not blockchain:
                raise HTTPException(status_code=404, detail=f"Chain {chain_id} not found")
                
            blockchain._mine_new_block()
            block = blockchain.blocks[blockchain.current_block_number]
            return block.to_rpc_format(full_transactions=False)
            
    async def _handle_subscription(self, websocket: WebSocket, blockchain, subscription_id: str, subscription: Dict):
        try:
            if subscription["type"] == "newHeads":
                last_block = blockchain.current_block_number
                while websocket in self.websocket_connections[blockchain.chain_id]:
                    await asyncio.sleep(1)
                    if blockchain.current_block_number > last_block:
                        block = blockchain.blocks[blockchain.current_block_number]
                        notification = {
                            "jsonrpc": "2.0",
                            "method": "eth_subscription",
                            "params": {
                                "subscription": subscription_id,
                                "result": block.to_rpc_format(full_transactions=False),
                            },
                        }
                        await websocket.send_json(notification)
                        last_block = blockchain.current_block_number
                        
            elif subscription["type"] == "logs":
                last_log_count = len(blockchain.logs)
                filter_params = subscription["params"][0] if subscription["params"] else {}
                
                while websocket in self.websocket_connections[blockchain.chain_id]:
                    await asyncio.sleep(0.5)
                    if len(blockchain.logs) > last_log_count:
                        new_logs = blockchain.logs[last_log_count:]
                        for log in new_logs:
                            # Apply filter
                            if self._matches_log_filter(log, filter_params):
                                notification = {
                                    "jsonrpc": "2.0",
                                    "method": "eth_subscription",
                                    "params": {
                                        "subscription": subscription_id,
                                        "result": log.to_rpc_format(),
                                    },
                                }
                                await websocket.send_json(notification)
                        last_log_count = len(blockchain.logs)
                        
            elif subscription["type"] == "pendingTransactions":
                seen_txs = set()
                while websocket in self.websocket_connections[blockchain.chain_id]:
                    await asyncio.sleep(0.1)
                    for tx in blockchain.pending_transactions:
                        if tx.hash not in seen_txs:
                            notification = {
                                "jsonrpc": "2.0",
                                "method": "eth_subscription",
                                "params": {
                                    "subscription": subscription_id,
                                    "result": tx.hash,
                                },
                            }
                            await websocket.send_json(notification)
                            seen_txs.add(tx.hash)
                            
        except Exception as e:
            logger.error(f"Subscription error: {e}")
            
    def _matches_log_filter(self, log, filter_params: Dict) -> bool:
        if "address" in filter_params:
            addresses = filter_params["address"]
            if isinstance(addresses, str):
                addresses = [addresses]
            if log.address not in addresses:
                return False
                
        if "topics" in filter_params:
            filter_topics = filter_params["topics"]
            for i, filter_topic in enumerate(filter_topics):
                if filter_topic is None:
                    continue
                if i >= len(log.topics):
                    return False
                if isinstance(filter_topic, str):
                    if log.topics[i] != filter_topic:
                        return False
                elif isinstance(filter_topic, list):
                    if log.topics[i] not in filter_topic:
                        return False
                        
        return True


def create_app() -> FastAPI:
    server = MockAPIServer()
    return server.app