"""Chat command processing"""

from typing import Dict, List, Optional, Callable, Any, Set
from pydantic import BaseModel, Field
from enum import Enum


class CommandPermission(Enum):
    """Command permission levels"""
    ALL = "all"
    ADMIN = "admin"
    MODERATOR = "moderator"


class Command(BaseModel):
    """Chat command definition"""
    name: str
    description: str
    usage: str
    permission: CommandPermission = Field(CommandPermission.ALL)
    handler: Optional[Callable] = Field(None)
    aliases: List[str] = Field(default_factory=list)
    
    class Config:
        arbitrary_types_allowed = True


class CommandProcessor:
    """Processes chat commands"""
    
    def __init__(self, command_prefix: str = "/"):
        self.command_prefix = command_prefix
        self.commands: Dict[str, Command] = {}
        self.admin_players: Set[str] = set()
        self.moderator_players: Set[str] = set()
        
        # Register default commands
        self._register_default_commands()
    
    def _register_default_commands(self):
        """Register built-in commands"""
        # Help command
        self.register_command(Command(
            name="help",
            description="Show available commands",
            usage="/help [command]",
            permission=CommandPermission.ALL,
            handler=self._handle_help
        ))
        
        # Player commands
        self.register_command(Command(
            name="whisper",
            description="Send private message",
            usage="/whisper <player> <message>",
            permission=CommandPermission.ALL,
            aliases=["w", "msg"],
            handler=self._handle_whisper
        ))
        
        # Moderator commands
        self.register_command(Command(
            name="mute",
            description="Mute a player",
            usage="/mute <player> <duration>",
            permission=CommandPermission.MODERATOR,
            handler=self._handle_mute
        ))
        
        self.register_command(Command(
            name="unmute",
            description="Unmute a player",
            usage="/unmute <player>",
            permission=CommandPermission.MODERATOR,
            handler=self._handle_unmute
        ))
        
        # Admin commands
        self.register_command(Command(
            name="ban",
            description="Ban a player",
            usage="/ban <player> <reason>",
            permission=CommandPermission.ADMIN,
            handler=self._handle_ban
        ))
        
        self.register_command(Command(
            name="unban",
            description="Unban a player",
            usage="/unban <player>",
            permission=CommandPermission.ADMIN,
            handler=self._handle_unban
        ))
    
    def register_command(self, command: Command):
        """Register a command"""
        self.commands[command.name] = command
        
        # Register aliases
        for alias in command.aliases:
            self.commands[alias] = command
    
    def unregister_command(self, name: str):
        """Unregister a command"""
        if name in self.commands:
            command = self.commands[name]
            
            # Remove command and aliases
            del self.commands[name]
            for alias in command.aliases:
                if alias in self.commands:
                    del self.commands[alias]
    
    def process_message(self, player_id: str, message: str) -> Optional[Dict[str, Any]]:
        """Process a message for commands"""
        if not message.startswith(self.command_prefix):
            return None
        
        # Parse command
        parts = message[len(self.command_prefix):].split(maxsplit=1)
        if not parts:
            return None
        
        command_name = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        # Find command
        if command_name not in self.commands:
            return {
                "type": "error",
                "message": f"Unknown command: {command_name}"
            }
        
        command = self.commands[command_name]
        
        # Check permission
        if not self._check_permission(player_id, command.permission):
            return {
                "type": "error",
                "message": "You don't have permission to use this command"
            }
        
        # Execute command
        if command.handler:
            try:
                return command.handler(player_id, args)
            except Exception as e:
                return {
                    "type": "error",
                    "message": f"Command error: {str(e)}"
                }
        
        return None
    
    def _check_permission(self, player_id: str, permission: CommandPermission) -> bool:
        """Check if player has permission"""
        if permission == CommandPermission.ALL:
            return True
        elif permission == CommandPermission.MODERATOR:
            return player_id in self.moderator_players or player_id in self.admin_players
        elif permission == CommandPermission.ADMIN:
            return player_id in self.admin_players
        return False
    
    def add_admin(self, player_id: str):
        """Add admin player"""
        self.admin_players.add(player_id)
    
    def remove_admin(self, player_id: str):
        """Remove admin player"""
        self.admin_players.discard(player_id)
    
    def add_moderator(self, player_id: str):
        """Add moderator player"""
        self.moderator_players.add(player_id)
    
    def remove_moderator(self, player_id: str):
        """Remove moderator player"""
        self.moderator_players.discard(player_id)
    
    def _handle_help(self, player_id: str, args: str) -> Dict[str, Any]:
        """Handle help command"""
        if args:
            # Show help for specific command
            if args in self.commands:
                command = self.commands[args]
                return {
                    "type": "help",
                    "command": command.name,
                    "description": command.description,
                    "usage": command.usage,
                    "aliases": command.aliases
                }
            else:
                return {
                    "type": "error",
                    "message": f"Unknown command: {args}"
                }
        
        # Show all available commands
        available_commands = []
        for name, command in self.commands.items():
            # Skip aliases
            if name != command.name:
                continue
            
            # Check permission
            if self._check_permission(player_id, command.permission):
                available_commands.append({
                    "name": command.name,
                    "description": command.description
                })
        
        return {
            "type": "help",
            "commands": available_commands
        }
    
    def _handle_whisper(self, player_id: str, args: str) -> Dict[str, Any]:
        """Handle whisper command"""
        parts = args.split(maxsplit=1)
        if len(parts) < 2:
            return {
                "type": "error",
                "message": "Usage: /whisper <player> <message>"
            }
        
        target_player = parts[0]
        message = parts[1]
        
        return {
            "type": "whisper",
            "from": player_id,
            "to": target_player,
            "message": message
        }
    
    def _handle_mute(self, player_id: str, args: str) -> Dict[str, Any]:
        """Handle mute command"""
        parts = args.split()
        if len(parts) < 2:
            return {
                "type": "error",
                "message": "Usage: /mute <player> <duration>"
            }
        
        target_player = parts[0]
        try:
            duration = float(parts[1])
        except ValueError:
            return {
                "type": "error",
                "message": "Duration must be a number (in seconds)"
            }
        
        return {
            "type": "mute",
            "moderator": player_id,
            "target": target_player,
            "duration": duration
        }
    
    def _handle_unmute(self, player_id: str, args: str) -> Dict[str, Any]:
        """Handle unmute command"""
        if not args:
            return {
                "type": "error",
                "message": "Usage: /unmute <player>"
            }
        
        return {
            "type": "unmute",
            "moderator": player_id,
            "target": args.strip()
        }
    
    def _handle_ban(self, player_id: str, args: str) -> Dict[str, Any]:
        """Handle ban command"""
        parts = args.split(maxsplit=1)
        if not parts:
            return {
                "type": "error",
                "message": "Usage: /ban <player> <reason>"
            }
        
        target_player = parts[0]
        reason = parts[1] if len(parts) > 1 else "No reason provided"
        
        return {
            "type": "ban",
            "admin": player_id,
            "target": target_player,
            "reason": reason
        }
    
    def _handle_unban(self, player_id: str, args: str) -> Dict[str, Any]:
        """Handle unban command"""
        if not args:
            return {
                "type": "error",
                "message": "Usage: /unban <player>"
            }
        
        return {
            "type": "unban",
            "admin": player_id,
            "target": args.strip()
        }