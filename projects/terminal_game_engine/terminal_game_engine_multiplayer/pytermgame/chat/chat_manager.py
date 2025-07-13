"""Main chat management system"""

from typing import Dict, List, Optional, Set, Callable, Any
from pydantic import BaseModel, Field
from enum import Enum
import time
import asyncio

from .moderation import ModerationFilter, FilterResult
from .commands import CommandProcessor


class ChatChannel(Enum):
    """Chat channel types"""
    ALL = "all"
    TEAM = "team"
    PRIVATE = "private"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """Chat message structure"""
    message_id: str
    player_id: str
    channel: ChatChannel
    content: str
    timestamp: float = Field(default_factory=time.time)
    filtered_content: Optional[str] = Field(None)
    recipients: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChatManager:
    """Manages chat system with moderation and commands"""
    
    def __init__(self):
        self.moderation = ModerationFilter()
        self.command_processor = CommandProcessor()
        
        # Message history
        self.message_history: List[ChatMessage] = []
        self.max_history_size = 1000
        
        # Player teams for team chat
        self.player_teams: Dict[str, str] = {}  # player_id -> team_id
        
        # Callbacks
        self.message_callbacks: List[Callable] = []
        self.command_callbacks: Dict[str, List[Callable]] = {}
        
        # Settings
        self.enable_moderation = True
        self.enable_commands = True
        self.enable_history = True
        
        self._message_counter = 0
    
    def process_message(self, player_id: str, content: str, channel: ChatChannel = ChatChannel.ALL) -> Optional[ChatMessage]:
        """Process incoming chat message"""
        # Check for commands first
        if self.enable_commands and content.startswith(self.command_processor.command_prefix):
            command_result = self.command_processor.process_message(player_id, content)
            if command_result:
                self._handle_command_result(player_id, command_result)
                return None  # Commands don't create regular messages
        
        # Apply moderation
        if self.enable_moderation:
            filter_result, filtered_content = self.moderation.filter_message(player_id, content)
            
            if filter_result == FilterResult.BLOCKED:
                # Notify player their message was blocked
                self._send_system_message(
                    player_id,
                    f"Your message was blocked: {filtered_content}"
                )
                return None
        else:
            filter_result = FilterResult.ALLOWED
            filtered_content = content
        
        # Create message
        self._message_counter += 1
        message = ChatMessage(
            message_id=f"msg_{self._message_counter}",
            player_id=player_id,
            channel=channel,
            content=content,
            filtered_content=filtered_content if filter_result == FilterResult.MODIFIED else None
        )
        
        # Determine recipients
        message.recipients = self._get_recipients(player_id, channel)
        
        # Add to history
        if self.enable_history:
            self._add_to_history(message)
        
        # Notify callbacks
        for callback in self.message_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(message))
                else:
                    callback(message)
            except Exception:
                pass
        
        return message
    
    def _get_recipients(self, player_id: str, channel: ChatChannel) -> List[str]:
        """Get recipients for a message based on channel"""
        if channel == ChatChannel.ALL:
            # All players receive
            return []  # Empty list means all
        elif channel == ChatChannel.TEAM:
            # Only team members
            player_team = self.player_teams.get(player_id)
            if player_team:
                return [
                    pid for pid, team in self.player_teams.items()
                    if team == player_team
                ]
            return [player_id]  # Only sender if no team
        elif channel == ChatChannel.PRIVATE:
            # Handled separately by whisper command
            return [player_id]
        elif channel == ChatChannel.SYSTEM:
            # System messages
            return []
        
        return []
    
    def _handle_command_result(self, player_id: str, result: Dict[str, Any]):
        """Handle command execution result"""
        command_type = result.get("type")
        
        if command_type == "error":
            self._send_system_message(player_id, result["message"])
        
        elif command_type == "help":
            if "commands" in result:
                # List of commands
                help_text = "Available commands:\n"
                for cmd in result["commands"]:
                    help_text += f"  {cmd['name']}: {cmd['description']}\n"
                self._send_system_message(player_id, help_text)
            else:
                # Specific command help
                help_text = f"Command: {result['command']}\n"
                help_text += f"Description: {result['description']}\n"
                help_text += f"Usage: {result['usage']}\n"
                if result.get("aliases"):
                    help_text += f"Aliases: {', '.join(result['aliases'])}"
                self._send_system_message(player_id, help_text)
        
        elif command_type == "whisper":
            # Handle private message
            self._send_private_message(
                result["from"],
                result["to"],
                result["message"]
            )
        
        elif command_type in ["mute", "unmute", "ban", "unban"]:
            # Notify command callbacks
            if command_type in self.command_callbacks:
                for callback in self.command_callbacks[command_type]:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            asyncio.create_task(callback(result))
                        else:
                            callback(result)
                    except Exception:
                        pass
    
    def _send_system_message(self, player_id: str, content: str):
        """Send system message to player"""
        self._message_counter += 1
        message = ChatMessage(
            message_id=f"sys_{self._message_counter}",
            player_id="SYSTEM",
            channel=ChatChannel.SYSTEM,
            content=content,
            recipients=[player_id]
        )
        
        if self.enable_history:
            self._add_to_history(message)
        
        # Notify callbacks
        for callback in self.message_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(message))
                else:
                    callback(message)
            except Exception:
                pass
    
    def _send_private_message(self, from_player: str, to_player: str, content: str):
        """Send private message between players"""
        # Apply moderation to private messages too
        if self.enable_moderation:
            filter_result, filtered_content = self.moderation.filter_message(from_player, content)
            if filter_result == FilterResult.BLOCKED:
                self._send_system_message(
                    from_player,
                    "Your private message was blocked"
                )
                return
        else:
            filtered_content = content
        
        self._message_counter += 1
        message = ChatMessage(
            message_id=f"pm_{self._message_counter}",
            player_id=from_player,
            channel=ChatChannel.PRIVATE,
            content=content,
            filtered_content=filtered_content if filter_result == FilterResult.MODIFIED else None,
            recipients=[from_player, to_player],
            metadata={"to": to_player}
        )
        
        if self.enable_history:
            self._add_to_history(message)
        
        # Notify callbacks
        for callback in self.message_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(message))
                else:
                    callback(message)
            except Exception:
                pass
    
    def _add_to_history(self, message: ChatMessage):
        """Add message to history"""
        self.message_history.append(message)
        
        # Limit history size
        if len(self.message_history) > self.max_history_size:
            self.message_history = self.message_history[-self.max_history_size:]
    
    def set_player_team(self, player_id: str, team_id: str):
        """Set player's team for team chat"""
        self.player_teams[player_id] = team_id
    
    def remove_player(self, player_id: str):
        """Remove player from chat system"""
        if player_id in self.player_teams:
            del self.player_teams[player_id]
        
        # Clean up moderation tracking
        if player_id in self.moderation.player_message_times:
            del self.moderation.player_message_times[player_id]
    
    def get_message_history(self, channel: Optional[ChatChannel] = None, 
                          player_id: Optional[str] = None, limit: int = 50) -> List[ChatMessage]:
        """Get message history"""
        messages = self.message_history
        
        # Filter by channel
        if channel:
            messages = [m for m in messages if m.channel == channel]
        
        # Filter by player
        if player_id:
            messages = [
                m for m in messages
                if m.player_id == player_id or player_id in m.recipients or not m.recipients
            ]
        
        # Return last N messages
        return messages[-limit:]
    
    def on_message(self, callback: Callable):
        """Register message callback"""
        self.message_callbacks.append(callback)
    
    def on_command(self, command_type: str, callback: Callable):
        """Register command callback"""
        if command_type not in self.command_callbacks:
            self.command_callbacks[command_type] = []
        self.command_callbacks[command_type].append(callback)
    
    def broadcast_system_message(self, content: str):
        """Broadcast system message to all players"""
        self._message_counter += 1
        message = ChatMessage(
            message_id=f"broadcast_{self._message_counter}",
            player_id="SYSTEM",
            channel=ChatChannel.SYSTEM,
            content=content,
            recipients=[]  # Empty means all
        )
        
        if self.enable_history:
            self._add_to_history(message)
        
        # Notify callbacks
        for callback in self.message_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(message))
                else:
                    callback(message)
            except Exception:
                pass