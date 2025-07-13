"""Main game server implementation"""

from typing import Dict, Optional, Set, Callable, Any, List
import asyncio
import uuid
import time
from collections import defaultdict

from ..network import NetworkServer, Packet, PacketType, ProtocolType
from .game_state import GameState, PlayerStatus
from .tick_manager import TickManager


class GameServer:
    """Authoritative game server"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8888, 
                 tick_rate: int = 60, protocol_type: ProtocolType = ProtocolType.TCP):
        self.network_server = NetworkServer(host, port, protocol_type)
        self.game_state = GameState()
        self.tick_manager = TickManager(target_tick_rate=tick_rate)
        
        # Player management
        self.client_to_player: Dict[str, str] = {}
        self.player_to_client: Dict[str, str] = {}
        
        # Input buffer for lag compensation
        self.input_buffer: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # Callbacks
        self.player_join_callbacks: List[Callable] = []
        self.player_leave_callbacks: List[Callable] = []
        self.game_update_callbacks: List[Callable] = []
        
        # Server state
        self.running = False
        self.max_players = 100
        self.require_auth = False
    
    async def start(self):
        """Start the game server"""
        self.running = True
        
        # Register network handlers
        self.network_server.register_handler(PacketType.PLAYER_INPUT, self._handle_player_input)
        self.network_server.register_handler(PacketType.CHAT_MESSAGE, self._handle_chat_message)
        
        # Start network server
        await self.network_server.start()
        
        # Add tick callback
        self.tick_manager.add_callback(self._game_tick)
        
        # Start tick manager
        await self.tick_manager.start()
        
        # Start state broadcast loop
        asyncio.create_task(self._broadcast_state_loop())
    
    async def stop(self):
        """Stop the game server"""
        self.running = False
        
        # Stop tick manager
        await self.tick_manager.stop()
        
        # Stop network server
        await self.network_server.stop()
    
    async def _game_tick(self, tick: int, delta_time: float):
        """Process a game tick"""
        # Apply physics
        self.game_state.apply_physics(delta_time)
        
        # Process input buffer
        await self._process_input_buffer()
        
        # Update game state
        self.game_state.advance_tick()
        
        # Call update callbacks
        for callback in self.game_update_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(self.game_state, delta_time)
                else:
                    callback(self.game_state, delta_time)
            except Exception:
                pass
    
    async def _broadcast_state_loop(self):
        """Broadcast game state to all clients"""
        while self.running:
            # Create state packet
            state_packet = Packet(
                packet_id=str(uuid.uuid4()),
                packet_type=PacketType.GAME_STATE,
                data=self.game_state.serialize_for_client()
            )
            
            # Broadcast to all players
            await self.network_server.broadcast_packet(state_packet)
            
            # Wait for next broadcast (10 Hz by default)
            await asyncio.sleep(0.1)
    
    async def _handle_player_input(self, packet: Packet, client_id: str):
        """Handle player input packet"""
        if client_id not in self.client_to_player:
            return
        
        player_id = self.client_to_player[client_id]
        input_data = packet.data.get("input", {})
        sequence = packet.data.get("sequence", 0)
        
        # Validate input
        if self.game_state.validate_player_input(player_id, input_data, sequence):
            # Add to input buffer
            self.input_buffer[player_id].append({
                "input": input_data,
                "timestamp": packet.timestamp,
                "sequence": sequence
            })
            
            # Keep buffer size reasonable
            if len(self.input_buffer[player_id]) > 120:  # 2 seconds at 60 Hz
                self.input_buffer[player_id] = self.input_buffer[player_id][-120:]
    
    async def _process_input_buffer(self):
        """Process buffered player inputs"""
        for player_id, inputs in self.input_buffer.items():
            if not inputs or player_id not in self.game_state.players:
                continue
            
            # Process latest input
            latest_input = inputs[-1]
            input_data = latest_input["input"]
            
            # Apply input to game state
            if "position" in input_data:
                self.game_state.update_player_position(
                    player_id,
                    input_data["position"],
                    input_data.get("velocity")
                )
            
            # Clear processed inputs
            self.input_buffer[player_id].clear()
    
    async def _handle_chat_message(self, packet: Packet, client_id: str):
        """Handle chat message"""
        if client_id not in self.client_to_player:
            return
        
        player_id = self.client_to_player[client_id]
        message = packet.data.get("message", "")
        channel = packet.data.get("channel", "all")
        
        # Create chat broadcast packet
        chat_packet = Packet(
            packet_id=str(uuid.uuid4()),
            packet_type=PacketType.CHAT_MESSAGE,
            data={
                "player_id": player_id,
                "message": message,
                "channel": channel,
                "timestamp": time.time()
            }
        )
        
        # Broadcast to appropriate recipients
        if channel == "all":
            await self.network_server.broadcast_packet(chat_packet)
        else:
            # Handle team/private channels
            pass
    
    def on_player_join(self, callback: Callable):
        """Register player join callback"""
        self.player_join_callbacks.append(callback)
    
    def on_player_leave(self, callback: Callable):
        """Register player leave callback"""
        self.player_leave_callbacks.append(callback)
    
    def on_game_update(self, callback: Callable):
        """Register game update callback"""
        self.game_update_callbacks.append(callback)
    
    async def add_player(self, player_id: str, client_id: str) -> bool:
        """Add a player to the game"""
        if self.game_state.get_active_players() >= self.max_players:
            return False
        
        # Add to game state
        player = self.game_state.add_player(player_id)
        player.status = PlayerStatus.PLAYING
        
        # Map client to player
        self.client_to_player[client_id] = player_id
        self.player_to_client[player_id] = client_id
        
        # Call join callbacks
        for callback in self.player_join_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(player_id)
                else:
                    callback(player_id)
            except Exception:
                pass
        
        return True
    
    async def remove_player(self, player_id: str):
        """Remove a player from the game"""
        if player_id in self.player_to_client:
            client_id = self.player_to_client[player_id]
            del self.client_to_player[client_id]
            del self.player_to_client[player_id]
        
        # Remove from game state
        self.game_state.remove_player(player_id)
        
        # Clear input buffer
        if player_id in self.input_buffer:
            del self.input_buffer[player_id]
        
        # Call leave callbacks
        for callback in self.player_leave_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(player_id)
                else:
                    callback(player_id)
            except Exception:
                pass
    
    def get_player_count(self) -> int:
        """Get number of active players"""
        return len(self.game_state.get_active_players())
    
    def get_server_stats(self) -> Dict[str, Any]:
        """Get server statistics"""
        return {
            "player_count": self.get_player_count(),
            "spectator_count": len(self.game_state.get_spectators()),
            "tick_stats": self.tick_manager.get_tick_stats(),
            "game_id": self.game_state.game_id,
            "uptime": time.time() - self.game_state.timestamp,
            "max_players": self.max_players
        }