"""Tests for network module"""

import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock

from pytermgame.network import (
    NetworkManager, NetworkClient, NetworkServer,
    Packet, PacketType, Protocol, ProtocolType,
    TCPProtocol, UDPProtocol
)


class TestPacket:
    """Test Packet class"""
    
    def test_packet_creation(self):
        """Test creating a packet"""
        packet = Packet(
            packet_id="test123",
            packet_type=PacketType.GAME_STATE,
            sender_id="player1",
            data={"position": {"x": 10, "y": 20}}
        )
        
        assert packet.packet_id == "test123"
        assert packet.packet_type == PacketType.GAME_STATE
        assert packet.sender_id == "player1"
        assert packet.data["position"]["x"] == 10
    
    def test_packet_serialization(self):
        """Test packet serialization and deserialization"""
        original = Packet(
            packet_id="test456",
            packet_type=PacketType.PLAYER_INPUT,
            data={"input": "move_left"},
            requires_ack=True
        )
        
        # Serialize and deserialize
        serialized = original.serialize()
        deserialized = Packet.deserialize(serialized)
        
        assert deserialized.packet_id == original.packet_id
        assert deserialized.packet_type == original.packet_type
        assert deserialized.data == original.data
        assert deserialized.requires_ack == original.requires_ack
    
    def test_create_ack(self):
        """Test ACK packet creation"""
        packet = Packet(
            packet_id="test789",
            packet_type=PacketType.CONNECT,
            sender_id="client1",
            recipient_id="server"
        )
        
        ack = packet.create_ack()
        
        assert ack.packet_type == PacketType.ACK
        assert ack.sender_id == "server"
        assert ack.recipient_id == "client1"
        assert ack.data["ack_for"] == "test789"


class TestNetworkManager:
    """Test NetworkManager class"""
    
    @pytest.mark.asyncio
    async def test_manager_initialization(self):
        """Test network manager initialization"""
        manager = NetworkManager(ProtocolType.TCP)
        
        assert manager.protocol_type == ProtocolType.TCP
        assert len(manager.connections) == 0
        assert manager.running is False
    
    @pytest.mark.asyncio
    async def test_start_stop(self):
        """Test starting and stopping manager"""
        manager = NetworkManager()
        
        await manager.start()
        assert manager.running is True
        
        await manager.stop()
        assert manager.running is False
    
    @pytest.mark.asyncio
    async def test_packet_handler_registration(self):
        """Test registering packet handlers"""
        manager = NetworkManager()
        handler = Mock()
        
        manager.register_handler(PacketType.GAME_STATE, handler)
        assert handler in manager.packet_handlers[PacketType.GAME_STATE]
        
        manager.unregister_handler(PacketType.GAME_STATE, handler)
        assert handler not in manager.packet_handlers[PacketType.GAME_STATE]
    
    @pytest.mark.asyncio
    async def test_send_packet(self):
        """Test sending a packet"""
        manager = NetworkManager()
        mock_protocol = AsyncMock()
        mock_protocol.send = AsyncMock(return_value=True)
        
        manager.connections["client1"] = mock_protocol
        
        packet = Packet(
            packet_id="test",
            packet_type=PacketType.GAME_STATE,
            data={"test": "data"}
        )
        
        success = await manager.send_packet(packet, "client1")
        
        assert success is True
        mock_protocol.send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_broadcast_packet(self):
        """Test broadcasting packet"""
        manager = NetworkManager()
        
        # Add mock connections
        for i in range(3):
            mock_protocol = AsyncMock()
            mock_protocol.send = AsyncMock(return_value=True)
            manager.connections[f"client{i}"] = mock_protocol
        
        packet = Packet(
            packet_id="broadcast",
            packet_type=PacketType.LOBBY_UPDATE,
            data={"update": "test"}
        )
        
        results = await manager.broadcast_packet(packet, exclude=["client1"])
        
        assert results["client0"] is True
        assert results["client2"] is True
        assert "client1" not in results


class TestNetworkClient:
    """Test NetworkClient class"""
    
    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test client initialization"""
        client = NetworkClient("player123", ProtocolType.TCP)
        
        assert client.client_id == "player123"
        assert client.connected is False
        assert client.server_id is None
    
    @pytest.mark.asyncio
    async def test_send_input(self):
        """Test sending player input"""
        client = NetworkClient()
        client.connected = True
        client.server_id = "server"
        
        # Mock the manager
        client.manager.send_packet = AsyncMock(return_value=True)
        
        input_data = {"move": "left", "jump": True}
        success = await client.send_input(input_data)
        
        assert success is True
        client.manager.send_packet.assert_called_once()
        
        # Check packet content
        call_args = client.manager.send_packet.call_args
        packet = call_args[0][0]
        assert packet.packet_type == PacketType.PLAYER_INPUT
        assert packet.data["input"] == input_data
    
    @pytest.mark.asyncio
    async def test_send_chat_message(self):
        """Test sending chat message"""
        client = NetworkClient()
        client.connected = True
        client.server_id = "server"
        
        client.manager.send_packet = AsyncMock(return_value=True)
        
        success = await client.send_chat_message("Hello world!", "all")
        
        assert success is True
        
        # Check packet
        call_args = client.manager.send_packet.call_args
        packet = call_args[0][0]
        assert packet.packet_type == PacketType.CHAT_MESSAGE
        assert packet.data["message"] == "Hello world!"
        assert packet.data["channel"] == "all"


class TestNetworkServer:
    """Test NetworkServer class"""
    
    @pytest.mark.asyncio
    async def test_server_initialization(self):
        """Test server initialization"""
        server = NetworkServer("127.0.0.1", 9999, ProtocolType.TCP)
        
        assert server.host == "127.0.0.1"
        assert server.port == 9999
        assert server.protocol_type == ProtocolType.TCP
        assert server.running is False
    
    @pytest.mark.asyncio
    async def test_packet_handling(self):
        """Test packet handling"""
        server = NetworkServer()
        handler = Mock()
        
        server.register_handler(PacketType.PLAYER_INPUT, handler)
        
        # Simulate packet data
        packet = Packet(
            packet_id="test",
            packet_type=PacketType.PLAYER_INPUT,
            data={"input": "test"}
        )
        
        await server._handle_packet_data(packet.serialize(), "client1")
        
        handler.assert_called_once()
        call_args = handler.call_args[0]
        assert call_args[0].packet_type == PacketType.PLAYER_INPUT
        assert call_args[1] == "client1"
    
    @pytest.mark.asyncio
    async def test_client_management(self):
        """Test client connection management"""
        server = NetworkServer()
        
        assert server.get_client_count() == 0
        
        # Add mock client
        mock_protocol = AsyncMock()
        mock_protocol.is_connected = Mock(return_value=True)
        mock_protocol.disconnect = AsyncMock()
        
        server.clients["client1"] = mock_protocol
        server.client_info["client1"] = {"connected_at": time.time()}
        
        assert server.get_client_count() == 1
        assert "client1" in server.get_client_ids()
        
        # Disconnect client
        await server.disconnect_client("client1")
        
        assert server.get_client_count() == 0
        mock_protocol.disconnect.assert_called_once()


class TestProtocols:
    """Test protocol implementations"""
    
    @pytest.mark.asyncio
    async def test_tcp_protocol(self):
        """Test TCP protocol"""
        protocol = TCPProtocol()
        
        assert protocol.is_connected() is False
        assert protocol.get_latency() == 0.0
    
    @pytest.mark.asyncio
    async def test_udp_protocol(self):
        """Test UDP protocol"""
        protocol = UDPProtocol()
        
        assert protocol.is_connected() is False
        assert protocol.get_latency() == 0.0


@pytest.mark.asyncio
async def test_integration_client_server():
    """Test basic client-server integration"""
    # This is a simplified integration test
    # In real scenarios, you'd need actual network connections
    
    client = NetworkClient("player1")
    server = NetworkServer()
    
    # Register a handler
    received_packets = []
    
    def handle_input(packet, client_id):
        received_packets.append((packet, client_id))
    
    server.register_handler(PacketType.PLAYER_INPUT, handle_input)
    
    # Simulate connection
    client.connected = True
    client.server_id = "server"
    
    # Mock the network layer
    async def mock_send(packet, recipient):
        # Simulate server receiving the packet
        await server._handle_packet_data(packet.serialize(), "player1")
        return True
    
    client.manager.send_packet = mock_send
    
    # Send input
    await client.send_input({"move": "forward"})
    
    # Check server received it
    assert len(received_packets) == 1
    packet, client_id = received_packets[0]
    assert packet.packet_type == PacketType.PLAYER_INPUT
    assert packet.data["input"]["move"] == "forward"
    assert client_id == "player1"