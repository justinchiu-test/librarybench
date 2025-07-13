"""Tests for chat system"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

from pytermgame.chat import (
    ChatManager, ChatMessage, ChatChannel,
    ModerationFilter, FilterResult,
    CommandProcessor, Command, CommandPermission
)


class TestModerationFilter:
    """Test ModerationFilter class"""
    
    def test_filter_creation(self):
        """Test creating moderation filter"""
        filter = ModerationFilter()
        
        assert filter.rate_limit_messages == 10
        assert filter.max_message_length == 500
        assert filter.filter_urls is True
        assert filter.filter_spam is True
    
    def test_profanity_filtering(self):
        """Test profanity filtering"""
        filter = ModerationFilter()
        filter.profanity_list = {"badword", "test123"}
        filter.__init__()  # Reinitialize to compile patterns
        
        # Test profanity detection
        result, message = filter.filter_message("player1", "This is a badword test")
        assert result == FilterResult.MODIFIED
        assert "****" in message
        assert "badword" not in message
        
        # Test clean message
        result, message = filter.filter_message("player1", "This is a clean message")
        assert result == FilterResult.ALLOWED
        assert message == "This is a clean message"
    
    def test_rate_limiting(self):
        """Test rate limiting"""
        filter = ModerationFilter(rate_limit_messages=3, rate_limit_interval=60.0)
        
        # Send messages up to limit
        for i in range(3):
            result, _ = filter.filter_message("player1", f"Message {i}")
            assert result == FilterResult.ALLOWED
        
        # Exceed rate limit
        result, reason = filter.filter_message("player1", "Too many messages")
        assert result == FilterResult.BLOCKED
        assert reason == "Rate limit exceeded"
        
        # Check player was auto-muted
        assert "player1" in filter.muted_players
    
    def test_player_banning(self):
        """Test player banning"""
        filter = ModerationFilter()
        
        # Ban player
        action = filter.ban_player("player1", "Toxic behavior")
        assert action.action_type == "ban"
        assert action.player_id == "player1"
        assert "player1" in filter.banned_players
        
        # Try to send message as banned player
        result, reason = filter.filter_message("player1", "Hello")
        assert result == FilterResult.BLOCKED
        assert reason == "Player is banned"
        
        # Unban player
        success = filter.unban_player("player1")
        assert success is True
        assert "player1" not in filter.banned_players
    
    def test_player_muting(self):
        """Test player muting"""
        filter = ModerationFilter()
        
        # Mute player
        action = filter.mute_player("player1", 60.0, "Spamming")
        assert action.action_type == "mute"
        assert action.duration == 60.0
        
        # Try to send message while muted
        result, reason = filter.filter_message("player1", "Hello")
        assert result == FilterResult.BLOCKED
        assert reason == "Player is muted"
        
        # Unmute player
        success = filter.unmute_player("player1")
        assert success is True
        
        # Can send messages again
        result, _ = filter.filter_message("player1", "Hello again")
        assert result == FilterResult.ALLOWED
    
    def test_url_filtering(self):
        """Test URL filtering"""
        filter = ModerationFilter(filter_urls=True)
        
        # Message with URL
        result, message = filter.filter_message(
            "player1",
            "Check out https://example.com for more info"
        )
        assert result == FilterResult.MODIFIED
        assert "[URL removed]" in message
        assert "https://example.com" not in message
        
        # Disable URL filtering
        filter.filter_urls = False
        result, message = filter.filter_message(
            "player1",
            "Visit http://test.com"
        )
        assert result == FilterResult.ALLOWED
        assert "http://test.com" in message
    
    def test_spam_detection(self):
        """Test spam detection"""
        filter = ModerationFilter(filter_spam=True)
        
        # Repeated characters
        result, reason = filter.filter_message("player1", "AAAAAAAAAAAA")
        assert result == FilterResult.BLOCKED
        
        # All caps (long message)
        result, reason = filter.filter_message("player1", "THIS IS ALL CAPS SPAM")
        assert result == FilterResult.BLOCKED
        
        # Repeated words
        result, reason = filter.filter_message("player1", "spam spam spam spam spam")
        assert result == FilterResult.BLOCKED
    
    def test_warning_system(self):
        """Test warning system"""
        filter = ModerationFilter(max_warnings_before_mute=3)
        filter.profanity_list = {"bad"}
        filter.__init__()
        
        # Get warnings for profanity
        for i in range(2):
            result, _ = filter.filter_message("player1", f"bad word {i}")
            assert result == FilterResult.MODIFIED
            assert filter.warnings.get("player1", 0) == i + 1
        
        # Third warning should trigger auto-mute
        result, _ = filter.filter_message("player1", "bad again")
        assert result == FilterResult.MODIFIED
        assert "player1" in filter.muted_players
        assert filter.warnings["player1"] == 0  # Reset after mute
    
    def test_player_status(self):
        """Test getting player moderation status"""
        filter = ModerationFilter()
        
        # Clean player
        status = filter.get_player_status("player1")
        assert status["banned"] is False
        assert status["muted"] is False
        assert status["warnings"] == 0
        
        # Add warning
        filter.warnings["player1"] = 2
        status = filter.get_player_status("player1")
        assert status["warnings"] == 2
        
        # Mute player
        filter.mute_player("player1", 300.0, "Test")
        status = filter.get_player_status("player1")
        assert status["muted"] is True
        assert status["mute_remaining"] > 0


class TestCommandProcessor:
    """Test CommandProcessor class"""
    
    def test_processor_creation(self):
        """Test creating command processor"""
        processor = CommandProcessor(command_prefix="/")
        
        assert processor.command_prefix == "/"
        assert "help" in processor.commands
        assert "whisper" in processor.commands
        assert "mute" in processor.commands
    
    def test_command_registration(self):
        """Test registering custom commands"""
        processor = CommandProcessor()
        
        def test_handler(player_id, args):
            return {"type": "test", "player": player_id, "args": args}
        
        command = Command(
            name="test",
            description="Test command",
            usage="/test <arg>",
            handler=test_handler
        )
        
        processor.register_command(command)
        assert "test" in processor.commands
        
        # Process command
        result = processor.process_message("player1", "/test hello world")
        assert result["type"] == "test"
        assert result["player"] == "player1"
        assert result["args"] == "hello world"
        
        # Unregister command
        processor.unregister_command("test")
        assert "test" not in processor.commands
    
    def test_command_aliases(self):
        """Test command aliases"""
        processor = CommandProcessor()
        
        # Whisper command has aliases
        assert "whisper" in processor.commands
        assert "w" in processor.commands
        assert "msg" in processor.commands
        
        # All aliases point to same command
        assert processor.commands["w"] == processor.commands["whisper"]
    
    def test_command_permissions(self):
        """Test command permission system"""
        processor = CommandProcessor()
        
        # Regular player can't use admin commands
        result = processor.process_message("player1", "/ban player2 cheating")
        assert result["type"] == "error"
        assert "permission" in result["message"]
        
        # Add player as admin
        processor.add_admin("player1")
        
        # Now can use admin commands
        result = processor.process_message("player1", "/ban player2 cheating")
        assert result["type"] == "ban"
        assert result["target"] == "player2"
        
        # Moderator permissions
        processor.add_moderator("player3")
        
        # Moderator can use mod commands
        result = processor.process_message("player3", "/mute player2 60")
        assert result["type"] == "mute"
        
        # But not admin commands
        result = processor.process_message("player3", "/ban player2 test")
        assert result["type"] == "error"
    
    def test_help_command(self):
        """Test help command"""
        processor = CommandProcessor()
        
        # General help
        result = processor.process_message("player1", "/help")
        assert result["type"] == "help"
        assert "commands" in result
        assert len(result["commands"]) > 0
        
        # Specific command help
        result = processor.process_message("player1", "/help whisper")
        assert result["type"] == "help"
        assert result["command"] == "whisper"
        assert "aliases" in result
    
    def test_whisper_command(self):
        """Test whisper command"""
        processor = CommandProcessor()
        
        # Valid whisper
        result = processor.process_message("player1", "/whisper player2 Hello there!")
        assert result["type"] == "whisper"
        assert result["from"] == "player1"
        assert result["to"] == "player2"
        assert result["message"] == "Hello there!"
        
        # Invalid whisper (no message)
        result = processor.process_message("player1", "/whisper player2")
        assert result["type"] == "error"
    
    def test_moderation_commands(self):
        """Test moderation commands"""
        processor = CommandProcessor()
        processor.add_moderator("mod1")
        processor.add_admin("admin1")
        
        # Mute command
        result = processor.process_message("mod1", "/mute player1 300")
        assert result["type"] == "mute"
        assert result["target"] == "player1"
        assert result["duration"] == 300.0
        
        # Unmute command
        result = processor.process_message("mod1", "/unmute player1")
        assert result["type"] == "unmute"
        assert result["target"] == "player1"
        
        # Ban command (admin only)
        result = processor.process_message("admin1", "/ban player1 Toxic behavior")
        assert result["type"] == "ban"
        assert result["target"] == "player1"
        assert result["reason"] == "Toxic behavior"
        
        # Unban command
        result = processor.process_message("admin1", "/unban player1")
        assert result["type"] == "unban"
        assert result["target"] == "player1"


class TestChatManager:
    """Test ChatManager class"""
    
    def test_manager_creation(self):
        """Test creating chat manager"""
        manager = ChatManager()
        
        assert manager.enable_moderation is True
        assert manager.enable_commands is True
        assert manager.enable_history is True
        assert manager.max_history_size == 1000
    
    def test_process_message(self):
        """Test processing regular messages"""
        manager = ChatManager()
        
        # Process normal message
        message = manager.process_message("player1", "Hello world!", ChatChannel.ALL)
        assert message is not None
        assert message.player_id == "player1"
        assert message.content == "Hello world!"
        assert message.channel == ChatChannel.ALL
    
    def test_command_processing(self):
        """Test command processing through chat"""
        manager = ChatManager()
        
        # Commands don't create regular messages
        message = manager.process_message("player1", "/help")
        assert message is None
    
    def test_moderation_integration(self):
        """Test moderation integration"""
        manager = ChatManager()
        manager.moderation.profanity_list = {"badword"}
        manager.moderation.__init__()
        
        # Message with profanity
        message = manager.process_message("player1", "This badword is filtered")
        assert message is not None
        assert message.filtered_content is not None
        assert "****" in message.filtered_content
        
        # Blocked message
        manager.moderation.ban_player("player2", "Test ban")
        message = manager.process_message("player2", "I'm banned")
        assert message is None
    
    def test_team_chat(self):
        """Test team chat functionality"""
        manager = ChatManager()
        
        # Set up teams
        manager.set_player_team("player1", "team_red")
        manager.set_player_team("player2", "team_red")
        manager.set_player_team("player3", "team_blue")
        
        # Send team message
        message = manager.process_message("player1", "Team message", ChatChannel.TEAM)
        assert message is not None
        assert message.channel == ChatChannel.TEAM
        
        # Only team members should be recipients
        assert "player1" in message.recipients
        assert "player2" in message.recipients
        assert "player3" not in message.recipients
    
    def test_message_history(self):
        """Test message history"""
        manager = ChatManager()
        
        # Send some messages
        for i in range(5):
            manager.process_message(f"player{i}", f"Message {i}")
        
        # Get history
        history = manager.get_message_history(limit=3)
        assert len(history) == 3
        assert history[-1].content == "Message 4"  # Most recent
        
        # Get filtered history
        history = manager.get_message_history(player_id="player2")
        assert all(m.player_id == "player2" for m in history)
    
    def test_callbacks(self):
        """Test message callbacks"""
        manager = ChatManager()
        
        received_messages = []
        
        def on_message(msg):
            received_messages.append(msg)
        
        manager.on_message(on_message)
        
        # Send message
        manager.process_message("player1", "Test message")
        
        assert len(received_messages) == 1
        assert received_messages[0].content == "Test message"
    
    def test_system_messages(self):
        """Test system messages"""
        manager = ChatManager()
        
        received_messages = []
        manager.on_message(lambda m: received_messages.append(m))
        
        # Broadcast system message
        manager.broadcast_system_message("Server will restart in 5 minutes")
        
        assert len(received_messages) == 1
        msg = received_messages[0]
        assert msg.player_id == "SYSTEM"
        assert msg.channel == ChatChannel.SYSTEM
        assert "restart" in msg.content
    
    def test_command_callbacks(self):
        """Test command result callbacks"""
        manager = ChatManager()
        
        mute_events = []
        
        def on_mute(result):
            mute_events.append(result)
        
        manager.on_command("mute", on_mute)
        
        # Make player moderator and execute mute command
        manager.command_processor.add_moderator("mod1")
        manager.process_message("mod1", "/mute player1 60")
        
        assert len(mute_events) == 1
        assert mute_events[0]["target"] == "player1"
    
    def test_private_messages(self):
        """Test private messaging through commands"""
        manager = ChatManager()
        
        received_messages = []
        manager.on_message(lambda m: received_messages.append(m))
        
        # Send whisper
        manager.process_message("player1", "/whisper player2 Secret message")
        
        # Should create a private message
        assert len(received_messages) == 1
        msg = received_messages[0]
        assert msg.channel == ChatChannel.PRIVATE
        assert msg.player_id == "player1"
        assert "player1" in msg.recipients
        assert "player2" in msg.recipients
        assert msg.metadata["to"] == "player2"


@pytest.mark.asyncio
async def test_chat_integration():
    """Test integrated chat functionality"""
    manager = ChatManager()
    
    # Set up some players with teams
    manager.set_player_team("player1", "red")
    manager.set_player_team("player2", "red")
    manager.set_player_team("player3", "blue")
    
    # Track all messages
    all_messages = []
    manager.on_message(lambda m: all_messages.append(m))
    
    # Regular message
    manager.process_message("player1", "Hello everyone!")
    
    # Team message
    manager.process_message("player2", "Go red team!", ChatChannel.TEAM)
    
    # Command (whisper)
    manager.process_message("player3", "/w player1 Good luck!")
    
    # System broadcast
    manager.broadcast_system_message("Match starting in 10 seconds")
    
    # Check messages
    assert len(all_messages) == 4
    
    # Check message types
    public_msg = next(m for m in all_messages if m.content == "Hello everyone!")
    assert public_msg.channel == ChatChannel.ALL
    
    team_msg = next(m for m in all_messages if "red team" in m.content)
    assert team_msg.channel == ChatChannel.TEAM
    assert len(team_msg.recipients) == 2
    
    private_msg = next(m for m in all_messages if m.channel == ChatChannel.PRIVATE)
    assert "Good luck" in private_msg.content
    
    system_msg = next(m for m in all_messages if m.channel == ChatChannel.SYSTEM)
    assert system_msg.player_id == "SYSTEM"