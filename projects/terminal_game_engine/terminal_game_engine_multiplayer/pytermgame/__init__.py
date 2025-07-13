"""PyTermGame - Multiplayer Terminal Game Engine"""

__version__ = "0.1.0"

from .network import NetworkManager, NetworkClient, NetworkServer
from .server import GameServer
from .lobby import LobbySystem, GameRoom
from .spectator import SpectatorMode
from .chat import ChatManager
from .lag_compensation import LagCompensator
from .matchmaking import MatchmakingEngine

__all__ = [
    "NetworkManager",
    "NetworkClient", 
    "NetworkServer",
    "GameServer",
    "LobbySystem",
    "GameRoom",
    "SpectatorMode",
    "ChatManager",
    "LagCompensator",
    "MatchmakingEngine",
]