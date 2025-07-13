"""Network client implementation"""

from typing import Optional, Callable, Dict, Any
import asyncio
import uuid
import time

from .manager import NetworkManager
from .packet import Packet, PacketType
from .protocol import ProtocolType


class NetworkClient:
    """Client-side network interface"""
    
    def __init__(self, client_id: Optional[str] = None, protocol_type: ProtocolType = ProtocolType.TCP):
        self.client_id = client_id or str(uuid.uuid4())
        self.manager = NetworkManager(protocol_type)
        self.server_id: Optional[str] = None
        self.connected = False
        self.last_ping_time = 0.0
        self.latency = 0.0
        self._ping_task: Optional[asyncio.Task] = None
    
    async def connect(self, host: str, port: int) -> bool:
        """Connect to game server"""
        await self.manager.start()
        
        self.server_id = await self.manager.connect_client(host, port, "server")
        if self.server_id:
            self.connected = True
            
            # Send connect packet
            connect_packet = Packet(
                packet_id=str(uuid.uuid4()),
                packet_type=PacketType.CONNECT,
                sender_id=self.client_id,
                data={"client_id": self.client_id, "timestamp": time.time()},
                requires_ack=True
            )
            
            success = await self.manager.send_packet(connect_packet, self.server_id)
            if success:
                # Start ping task
                self._ping_task = asyncio.create_task(self._ping_loop())
                return True
        
        self.connected = False
        return False
    
    async def disconnect(self):
        """Disconnect from server"""
        if self.connected and self.server_id:
            # Send disconnect packet
            disconnect_packet = Packet(
                packet_id=str(uuid.uuid4()),
                packet_type=PacketType.DISCONNECT,
                sender_id=self.client_id,
                data={"reason": "client_disconnect"}
            )
            await self.manager.send_packet(disconnect_packet, self.server_id)
            
            # Cancel ping task
            if self._ping_task:
                self._ping_task.cancel()
                try:
                    await self._ping_task
                except asyncio.CancelledError:
                    pass
            
            await self.manager.disconnect_client(self.server_id)
        
        await self.manager.stop()
        self.connected = False
        self.server_id = None
    
    async def send_input(self, input_data: Dict[str, Any]) -> bool:
        """Send player input to server"""
        if not self.connected or not self.server_id:
            return False
        
        input_packet = Packet(
            packet_id=str(uuid.uuid4()),
            packet_type=PacketType.PLAYER_INPUT,
            sender_id=self.client_id,
            data={
                "input": input_data,
                "timestamp": time.time(),
                "sequence": self.manager._packet_counter
            }
        )
        
        return await self.manager.send_packet(input_packet, self.server_id)
    
    async def send_chat_message(self, message: str, channel: str = "all") -> bool:
        """Send chat message"""
        if not self.connected or not self.server_id:
            return False
        
        chat_packet = Packet(
            packet_id=str(uuid.uuid4()),
            packet_type=PacketType.CHAT_MESSAGE,
            sender_id=self.client_id,
            data={
                "message": message,
                "channel": channel,
                "timestamp": time.time()
            }
        )
        
        return await self.manager.send_packet(chat_packet, self.server_id)
    
    def on_game_state(self, handler: Callable):
        """Register game state update handler"""
        self.manager.register_handler(PacketType.GAME_STATE, handler)
    
    def on_chat_message(self, handler: Callable):
        """Register chat message handler"""
        self.manager.register_handler(PacketType.CHAT_MESSAGE, handler)
    
    def on_lobby_update(self, handler: Callable):
        """Register lobby update handler"""
        self.manager.register_handler(PacketType.LOBBY_UPDATE, handler)
    
    def on_error(self, handler: Callable):
        """Register error handler"""
        self.manager.register_handler(PacketType.ERROR, handler)
    
    async def _ping_loop(self):
        """Send periodic ping packets to measure latency"""
        while self.connected:
            try:
                await asyncio.sleep(1.0)  # Ping every second
                
                ping_packet = Packet(
                    packet_id=str(uuid.uuid4()),
                    packet_type=PacketType.PING,
                    sender_id=self.client_id,
                    data={"ping_time": time.time()},
                    requires_ack=False
                )
                
                self.last_ping_time = time.time()
                await self.manager.send_packet(ping_packet, self.server_id)
                
                # Register pong handler
                def handle_pong(packet: Packet):
                    if packet.packet_type == PacketType.PONG:
                        ping_time = packet.data.get("ping_time", 0)
                        self.latency = (time.time() - ping_time) * 1000  # Convert to ms
                
                self.manager.register_handler(PacketType.PONG, handle_pong)
                
            except asyncio.CancelledError:
                break
            except Exception:
                pass
    
    def get_latency(self) -> float:
        """Get current latency in milliseconds"""
        return self.latency
    
    def is_connected(self) -> bool:
        """Check connection status"""
        return self.connected and self.server_id is not None