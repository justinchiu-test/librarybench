"""Packet definitions for network communication"""

from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
import time
import json


class PacketType(Enum):
    """Types of network packets"""
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    GAME_STATE = "game_state"
    PLAYER_INPUT = "player_input"
    CHAT_MESSAGE = "chat_message"
    LOBBY_UPDATE = "lobby_update"
    MATCHMAKING_REQUEST = "matchmaking_request"
    MATCHMAKING_RESULT = "matchmaking_result"
    SPECTATOR_JOIN = "spectator_join"
    SPECTATOR_LEAVE = "spectator_leave"
    PING = "ping"
    PONG = "pong"
    ERROR = "error"
    ACK = "ack"


class Packet(BaseModel):
    """Base packet structure for network communication"""
    packet_id: str = Field(description="Unique packet identifier")
    packet_type: PacketType = Field(description="Type of packet")
    timestamp: float = Field(default_factory=time.time, description="Packet timestamp")
    sender_id: Optional[str] = Field(None, description="ID of the sender")
    recipient_id: Optional[str] = Field(None, description="ID of the recipient")
    data: Dict[str, Any] = Field(default_factory=dict, description="Packet payload")
    sequence_number: int = Field(0, description="Sequence number for ordering")
    requires_ack: bool = Field(False, description="Whether packet requires acknowledgment")
    
    def serialize(self) -> bytes:
        """Serialize packet to bytes"""
        return json.dumps(self.model_dump()).encode('utf-8')
    
    @classmethod
    def deserialize(cls, data: bytes) -> "Packet":
        """Deserialize packet from bytes"""
        return cls(**json.loads(data.decode('utf-8')))
    
    def create_ack(self) -> "Packet":
        """Create acknowledgment packet for this packet"""
        return Packet(
            packet_id=f"ack_{self.packet_id}",
            packet_type=PacketType.ACK,
            sender_id=self.recipient_id,
            recipient_id=self.sender_id,
            data={"ack_for": self.packet_id},
            sequence_number=self.sequence_number
        )