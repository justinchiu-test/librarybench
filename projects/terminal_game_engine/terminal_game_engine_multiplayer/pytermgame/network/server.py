"""Network server implementation"""

from typing import Dict, Optional, Set, Callable, Any
import asyncio
import uuid
import time

from .packet import Packet, PacketType
from .protocol import Protocol, TCPProtocol, UDPProtocol, ProtocolType


class NetworkServer:
    """Server-side network interface"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8888, protocol_type: ProtocolType = ProtocolType.TCP):
        self.host = host
        self.port = port
        self.protocol_type = protocol_type
        self.clients: Dict[str, Protocol] = {}
        self.client_info: Dict[str, Dict[str, Any]] = {}
        self.running = False
        self.server: Optional[asyncio.Server] = None
        self.packet_handlers: Dict[PacketType, Callable] = {}
        self._packet_counter = 0
    
    async def start(self):
        """Start the server"""
        self.running = True
        
        if self.protocol_type == ProtocolType.TCP:
            self.server = await asyncio.start_server(
                self._handle_tcp_client, self.host, self.port
            )
        else:
            # UDP server setup
            loop = asyncio.get_event_loop()
            transport, protocol = await loop.create_datagram_endpoint(
                lambda: UDPServerProtocol(self),
                local_addr=(self.host, self.port)
            )
            self.server = transport
        
        asyncio.create_task(self._process_loop())
    
    async def stop(self):
        """Stop the server"""
        self.running = False
        
        # Disconnect all clients
        for client_id in list(self.clients.keys()):
            await self.disconnect_client(client_id)
        
        if self.server:
            if self.protocol_type == ProtocolType.TCP:
                self.server.close()
                await self.server.wait_closed()
            else:
                self.server.close()
    
    async def _handle_tcp_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle new TCP client connection"""
        client_id = str(uuid.uuid4())
        protocol = TCPProtocol()
        protocol.reader = reader
        protocol.writer = writer
        protocol._connected = True
        
        self.clients[client_id] = protocol
        self.client_info[client_id] = {
            "connected_at": time.time(),
            "address": writer.get_extra_info('peername')
        }
        
        try:
            while self.running and protocol.is_connected():
                data = await protocol.receive()
                if data:
                    await self._handle_packet_data(data, client_id)
                else:
                    break
        finally:
            await self.disconnect_client(client_id)
    
    async def _handle_packet_data(self, data: bytes, client_id: str):
        """Handle incoming packet data"""
        try:
            packet = Packet.deserialize(data)
            packet.sender_id = client_id
            
            # Handle different packet types
            if packet.packet_type == PacketType.CONNECT:
                await self._handle_connect(packet, client_id)
            elif packet.packet_type == PacketType.DISCONNECT:
                await self._handle_disconnect(packet, client_id)
            elif packet.packet_type == PacketType.PING:
                await self._handle_ping(packet, client_id)
            elif packet.packet_type == PacketType.ACK:
                pass  # ACK packets are handled by the manager
            else:
                # Call registered handlers
                handler = self.packet_handlers.get(packet.packet_type)
                if handler:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(packet, client_id)
                    else:
                        handler(packet, client_id)
            
            # Send ACK if required
            if packet.requires_ack:
                ack_packet = packet.create_ack()
                await self.send_packet(ack_packet, client_id)
                
        except Exception:
            pass  # Invalid packet
    
    async def _handle_connect(self, packet: Packet, client_id: str):
        """Handle client connection"""
        self.client_info[client_id]["player_id"] = packet.data.get("client_id")
        self.client_info[client_id]["connected"] = True
        
        # Send acknowledgment
        ack_packet = Packet(
            packet_id=str(uuid.uuid4()),
            packet_type=PacketType.CONNECT,
            recipient_id=packet.sender_id,
            data={"status": "connected", "server_time": time.time()}
        )
        await self.send_packet(ack_packet, client_id)
    
    async def _handle_disconnect(self, packet: Packet, client_id: str):
        """Handle client disconnection"""
        await self.disconnect_client(client_id)
    
    async def _handle_ping(self, packet: Packet, client_id: str):
        """Handle ping packet"""
        pong_packet = Packet(
            packet_id=str(uuid.uuid4()),
            packet_type=PacketType.PONG,
            recipient_id=packet.sender_id,
            data=packet.data
        )
        await self.send_packet(pong_packet, client_id)
    
    async def send_packet(self, packet: Packet, client_id: str) -> bool:
        """Send packet to specific client"""
        if client_id not in self.clients:
            return False
        
        packet.sequence_number = self._packet_counter
        self._packet_counter += 1
        
        protocol = self.clients[client_id]
        return await protocol.send(packet.serialize())
    
    async def broadcast_packet(self, packet: Packet, exclude: Optional[Set[str]] = None) -> Dict[str, bool]:
        """Broadcast packet to all clients"""
        exclude = exclude or set()
        results = {}
        
        for client_id in self.clients:
            if client_id not in exclude:
                results[client_id] = await self.send_packet(packet, client_id)
        
        return results
    
    async def disconnect_client(self, client_id: str):
        """Disconnect a client"""
        if client_id in self.clients:
            protocol = self.clients[client_id]
            await protocol.disconnect()
            del self.clients[client_id]
            del self.client_info[client_id]
    
    def register_handler(self, packet_type: PacketType, handler: Callable):
        """Register packet handler"""
        self.packet_handlers[packet_type] = handler
    
    async def _process_loop(self):
        """Main server processing loop"""
        while self.running:
            # Check for disconnected clients
            disconnected = []
            for client_id, protocol in self.clients.items():
                if not protocol.is_connected():
                    disconnected.append(client_id)
            
            for client_id in disconnected:
                await self.disconnect_client(client_id)
            
            await asyncio.sleep(0.1)
    
    def get_client_count(self) -> int:
        """Get number of connected clients"""
        return len(self.clients)
    
    def get_client_ids(self) -> Set[str]:
        """Get set of connected client IDs"""
        return set(self.clients.keys())
    
    def get_client_info(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get client information"""
        return self.client_info.get(client_id)


class UDPServerProtocol(asyncio.DatagramProtocol):
    """UDP server protocol handler"""
    
    def __init__(self, server: NetworkServer):
        self.server = server
        self.addr_to_client: Dict[tuple, str] = {}
    
    def datagram_received(self, data: bytes, addr: tuple):
        """Handle incoming UDP datagram"""
        # Map address to client ID
        if addr not in self.addr_to_client:
            client_id = str(uuid.uuid4())
            self.addr_to_client[addr] = client_id
            
            # Create UDP protocol for this client
            protocol = UDPProtocol()
            protocol._connected = True
            protocol._remote_addr = addr
            protocol.transport = self.transport
            
            self.server.clients[client_id] = protocol
            self.server.client_info[client_id] = {
                "connected_at": time.time(),
                "address": addr
            }
        else:
            client_id = self.addr_to_client[addr]
        
        # Handle packet
        asyncio.create_task(self.server._handle_packet_data(data, client_id))