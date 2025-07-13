"""Network manager for handling connections and packet flow"""

from typing import Dict, Optional, Callable, Any, List
import asyncio
import uuid
import time
from collections import defaultdict

from .packet import Packet, PacketType
from .protocol import Protocol, TCPProtocol, UDPProtocol, ProtocolType


class NetworkManager:
    """Manages network connections and packet routing"""
    
    def __init__(self, protocol_type: ProtocolType = ProtocolType.TCP):
        self.protocol_type = protocol_type
        self.connections: Dict[str, Protocol] = {}
        self.packet_handlers: Dict[PacketType, List[Callable]] = defaultdict(list)
        self.pending_acks: Dict[str, Packet] = {}
        self.packet_queue: asyncio.Queue = asyncio.Queue()
        self.running = False
        self._packet_counter = 0
        self._latency_tracker: Dict[str, List[float]] = defaultdict(list)
    
    def create_protocol(self) -> Protocol:
        """Create protocol instance based on type"""
        if self.protocol_type == ProtocolType.TCP:
            return TCPProtocol()
        elif self.protocol_type == ProtocolType.UDP:
            return UDPProtocol()
        else:
            raise ValueError(f"Unknown protocol type: {self.protocol_type}")
    
    async def start(self):
        """Start the network manager"""
        self.running = True
        asyncio.create_task(self._process_packets())
        asyncio.create_task(self._handle_timeouts())
    
    async def stop(self):
        """Stop the network manager"""
        self.running = False
        for conn_id in list(self.connections.keys()):
            await self.disconnect_client(conn_id)
    
    async def connect_client(self, host: str, port: int, client_id: Optional[str] = None) -> Optional[str]:
        """Connect a new client"""
        client_id = client_id or str(uuid.uuid4())
        protocol = self.create_protocol()
        
        if await protocol.connect(host, port):
            self.connections[client_id] = protocol
            return client_id
        return None
    
    async def disconnect_client(self, client_id: str) -> bool:
        """Disconnect a client"""
        if client_id in self.connections:
            await self.connections[client_id].disconnect()
            del self.connections[client_id]
            return True
        return False
    
    def register_handler(self, packet_type: PacketType, handler: Callable):
        """Register a packet handler"""
        self.packet_handlers[packet_type].append(handler)
    
    def unregister_handler(self, packet_type: PacketType, handler: Callable):
        """Unregister a packet handler"""
        if handler in self.packet_handlers[packet_type]:
            self.packet_handlers[packet_type].remove(handler)
    
    async def send_packet(self, packet: Packet, client_id: str) -> bool:
        """Send a packet to a specific client"""
        if client_id not in self.connections:
            return False
        
        packet.sequence_number = self._packet_counter
        self._packet_counter += 1
        
        protocol = self.connections[client_id]
        success = await protocol.send(packet.serialize())
        
        if success and packet.requires_ack:
            self.pending_acks[packet.packet_id] = packet
        
        return success
    
    async def broadcast_packet(self, packet: Packet, exclude: Optional[List[str]] = None) -> Dict[str, bool]:
        """Broadcast packet to all connected clients"""
        exclude = exclude or []
        results = {}
        
        for client_id in self.connections:
            if client_id not in exclude:
                results[client_id] = await self.send_packet(packet, client_id)
        
        return results
    
    async def _process_packets(self):
        """Process incoming packets"""
        while self.running:
            tasks = []
            for client_id, protocol in list(self.connections.items()):
                if protocol.is_connected():
                    tasks.append(self._receive_from_client(client_id, protocol))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(0.001)  # Small delay to prevent CPU spinning
    
    async def _receive_from_client(self, client_id: str, protocol: Protocol):
        """Receive packets from a specific client"""
        data = await protocol.receive()
        if data:
            try:
                packet = Packet.deserialize(data)
                packet.sender_id = client_id
                
                # Handle ACK packets
                if packet.packet_type == PacketType.ACK:
                    ack_for = packet.data.get("ack_for")
                    if ack_for in self.pending_acks:
                        del self.pending_acks[ack_for]
                    return
                
                # Send ACK if required
                if packet.requires_ack:
                    ack_packet = packet.create_ack()
                    await self.send_packet(ack_packet, client_id)
                
                # Handle packet
                await self._handle_packet(packet)
                
            except Exception:
                pass  # Invalid packet, ignore
    
    async def _handle_packet(self, packet: Packet):
        """Handle a received packet"""
        handlers = self.packet_handlers.get(packet.packet_type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(packet)
                else:
                    handler(packet)
            except Exception:
                pass  # Handler error, continue with other handlers
    
    async def _handle_timeouts(self):
        """Handle packet timeouts for acknowledgments"""
        while self.running:
            current_time = time.time()
            timeout_packets = []
            
            for packet_id, packet in list(self.pending_acks.items()):
                if current_time - packet.timestamp > 5.0:  # 5 second timeout
                    timeout_packets.append(packet_id)
            
            for packet_id in timeout_packets:
                del self.pending_acks[packet_id]
            
            await asyncio.sleep(1.0)
    
    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.connections)
    
    def get_connection_ids(self) -> List[str]:
        """Get list of connected client IDs"""
        return list(self.connections.keys())
    
    def is_client_connected(self, client_id: str) -> bool:
        """Check if a client is connected"""
        return client_id in self.connections and self.connections[client_id].is_connected()
    
    def get_client_latency(self, client_id: str) -> float:
        """Get client latency"""
        if client_id in self.connections:
            return self.connections[client_id].get_latency()
        return -1.0