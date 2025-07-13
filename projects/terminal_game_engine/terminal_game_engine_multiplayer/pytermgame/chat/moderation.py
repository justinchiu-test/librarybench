"""Chat moderation functionality"""

from typing import List, Set, Dict, Optional, Pattern, Any
from pydantic import BaseModel, Field
from enum import Enum
import re
import time


class FilterResult(Enum):
    """Result of content filtering"""
    ALLOWED = "allowed"
    BLOCKED = "blocked"
    MODIFIED = "modified"


class ModerationAction(BaseModel):
    """Action taken by moderation system"""
    player_id: str
    action_type: str  # "warning", "mute", "ban"
    reason: str
    timestamp: float = Field(default_factory=time.time)
    duration: Optional[float] = Field(None, description="Duration in seconds")


class ModerationFilter(BaseModel):
    """Chat moderation and filtering"""
    
    # Profanity filter
    profanity_list: Set[str] = Field(default_factory=lambda: {
        "profanity1", "profanity2", "badword"  # Placeholder words
    })
    profanity_patterns: List[Pattern] = Field(default_factory=list)
    
    # Rate limiting
    rate_limit_messages: int = Field(10, description="Max messages per interval")
    rate_limit_interval: float = Field(60.0, description="Rate limit interval in seconds")
    player_message_times: Dict[str, List[float]] = Field(default_factory=dict)
    
    # Player moderation state
    muted_players: Dict[str, float] = Field(default_factory=dict)  # player_id -> unmute_time
    banned_players: Set[str] = Field(default_factory=set)
    warnings: Dict[str, int] = Field(default_factory=dict)  # player_id -> warning_count
    
    # Settings
    max_message_length: int = Field(500)
    max_warnings_before_mute: int = Field(3)
    auto_mute_duration: float = Field(300.0, description="5 minutes")
    filter_urls: bool = Field(True)
    filter_spam: bool = Field(True)
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        super().__init__(**data)
        # Compile profanity patterns
        for word in self.profanity_list:
            # Create pattern that catches variations
            pattern = re.compile(
                r'\b' + re.escape(word).replace(r'\*', r'.*') + r'\b',
                re.IGNORECASE
            )
            self.profanity_patterns.append(pattern)
    
    def filter_message(self, player_id: str, message: str) -> tuple[FilterResult, str]:
        """Filter a chat message"""
        # Check if player is banned
        if player_id in self.banned_players:
            return FilterResult.BLOCKED, "Player is banned"
        
        # Check if player is muted
        if player_id in self.muted_players:
            if time.time() < self.muted_players[player_id]:
                return FilterResult.BLOCKED, "Player is muted"
            else:
                # Unmute player
                del self.muted_players[player_id]
        
        # Check message length
        if len(message) > self.max_message_length:
            return FilterResult.BLOCKED, "Message too long"
        
        # Check rate limit
        if not self._check_rate_limit(player_id):
            self._apply_auto_mute(player_id)
            return FilterResult.BLOCKED, "Rate limit exceeded"
        
        # Filter profanity
        filtered_message = self._filter_profanity(message)
        if filtered_message != message:
            self._add_warning(player_id)
            return FilterResult.MODIFIED, filtered_message
        
        # Filter URLs if enabled
        if self.filter_urls:
            filtered_message = self._filter_urls(filtered_message)
            if filtered_message != message:
                return FilterResult.MODIFIED, filtered_message
        
        # Check for spam
        if self.filter_spam and self._is_spam(message):
            self._add_warning(player_id)
            return FilterResult.BLOCKED, "Spam detected"
        
        return FilterResult.ALLOWED, message
    
    def _check_rate_limit(self, player_id: str) -> bool:
        """Check if player is within rate limit"""
        current_time = time.time()
        
        if player_id not in self.player_message_times:
            self.player_message_times[player_id] = []
        
        # Remove old message times
        cutoff_time = current_time - self.rate_limit_interval
        self.player_message_times[player_id] = [
            t for t in self.player_message_times[player_id]
            if t > cutoff_time
        ]
        
        # Check limit
        if len(self.player_message_times[player_id]) >= self.rate_limit_messages:
            return False
        
        # Add current message time
        self.player_message_times[player_id].append(current_time)
        return True
    
    def _filter_profanity(self, message: str) -> str:
        """Filter profanity from message"""
        filtered = message
        
        for pattern in self.profanity_patterns:
            filtered = pattern.sub(lambda m: "*" * len(m.group()), filtered)
        
        return filtered
    
    def _filter_urls(self, message: str) -> str:
        """Filter URLs from message"""
        url_pattern = re.compile(
            r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b'
            r'(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)'
        )
        return url_pattern.sub("[URL removed]", message)
    
    def _is_spam(self, message: str) -> bool:
        """Check if message is spam"""
        # Check for repeated characters
        if re.search(r'(.)\1{5,}', message):
            return True
        
        # Check for all caps (if message is long enough)
        if len(message) > 10 and message.isupper():
            return True
        
        # Check for repeated words
        words = message.lower().split()
        if len(words) > 3:
            unique_words = set(words)
            if len(unique_words) < len(words) / 3:
                return True
        
        return False
    
    def _add_warning(self, player_id: str):
        """Add warning to player"""
        if player_id not in self.warnings:
            self.warnings[player_id] = 0
        
        self.warnings[player_id] += 1
        
        if self.warnings[player_id] >= self.max_warnings_before_mute:
            self._apply_auto_mute(player_id)
            self.warnings[player_id] = 0
    
    def _apply_auto_mute(self, player_id: str):
        """Apply automatic mute to player"""
        self.muted_players[player_id] = time.time() + self.auto_mute_duration
    
    def mute_player(self, player_id: str, duration: float, reason: str) -> ModerationAction:
        """Manually mute a player"""
        self.muted_players[player_id] = time.time() + duration
        
        return ModerationAction(
            player_id=player_id,
            action_type="mute",
            reason=reason,
            duration=duration
        )
    
    def unmute_player(self, player_id: str) -> bool:
        """Unmute a player"""
        if player_id in self.muted_players:
            del self.muted_players[player_id]
            return True
        return False
    
    def ban_player(self, player_id: str, reason: str) -> ModerationAction:
        """Ban a player"""
        self.banned_players.add(player_id)
        
        return ModerationAction(
            player_id=player_id,
            action_type="ban",
            reason=reason
        )
    
    def unban_player(self, player_id: str) -> bool:
        """Unban a player"""
        if player_id in self.banned_players:
            self.banned_players.remove(player_id)
            return True
        return False
    
    def get_player_status(self, player_id: str) -> Dict[str, Any]:
        """Get moderation status for a player"""
        status = {
            "banned": player_id in self.banned_players,
            "muted": False,
            "mute_remaining": 0.0,
            "warnings": self.warnings.get(player_id, 0)
        }
        
        if player_id in self.muted_players:
            remaining = self.muted_players[player_id] - time.time()
            if remaining > 0:
                status["muted"] = True
                status["mute_remaining"] = remaining
        
        return status