"""Queue management for matchmaking"""

from typing import List, Dict, Optional, Set, Tuple, Any
from pydantic import BaseModel, Field
import time
import uuid
from collections import defaultdict


class QueuedPlayer(BaseModel):
    """Player in matchmaking queue"""
    player_id: str
    skill_rating: float = Field(1000.0)
    queue_time: float = Field(default_factory=time.time)
    preferences: Dict[str, Any] = Field(default_factory=dict)
    
    def wait_time(self) -> float:
        """Get time spent in queue"""
        return time.time() - self.queue_time


class MatchGroup(BaseModel):
    """Group of players matched together"""
    group_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    players: List[QueuedPlayer] = Field(default_factory=list)
    average_skill: float = Field(0.0)
    skill_range: float = Field(0.0)
    created_at: float = Field(default_factory=time.time)
    
    def calculate_stats(self):
        """Calculate group statistics"""
        if not self.players:
            self.average_skill = 0.0
            self.skill_range = 0.0
            return
        
        skills = [p.skill_rating for p in self.players]
        self.average_skill = sum(skills) / len(skills)
        self.skill_range = max(skills) - min(skills)


class QueueManager(BaseModel):
    """Manages matchmaking queues"""
    queues: Dict[str, List[QueuedPlayer]] = Field(default_factory=lambda: defaultdict(list))
    skill_tolerance: float = Field(100.0, description="Initial skill rating tolerance")
    tolerance_growth_rate: float = Field(50.0, description="Tolerance growth per 10 seconds")
    max_wait_time: float = Field(300.0, description="Maximum wait time in seconds")
    team_size: int = Field(2, description="Players per team")
    
    class Config:
        arbitrary_types_allowed = True
    
    def add_player(self, player_id: str, skill_rating: float, 
                   queue_type: str = "default", preferences: Optional[Dict[str, Any]] = None) -> bool:
        """Add player to queue"""
        # Check if already in queue
        for queue_players in self.queues.values():
            if any(p.player_id == player_id for p in queue_players):
                return False
        
        player = QueuedPlayer(
            player_id=player_id,
            skill_rating=skill_rating,
            preferences=preferences or {}
        )
        
        self.queues[queue_type].append(player)
        return True
    
    def remove_player(self, player_id: str) -> bool:
        """Remove player from all queues"""
        removed = False
        for queue_type, queue_players in self.queues.items():
            for i, player in enumerate(queue_players):
                if player.player_id == player_id:
                    queue_players.pop(i)
                    removed = True
                    break
        return removed
    
    def find_match(self, queue_type: str = "default") -> Optional[MatchGroup]:
        """Find a match for players in queue"""
        if queue_type not in self.queues:
            return None
        
        queue = self.queues[queue_type]
        if len(queue) < self.team_size * 2:  # Need at least 2 teams
            return None
        
        # Sort by skill rating
        queue.sort(key=lambda p: p.skill_rating)
        
        # Try to find compatible players
        for i in range(len(queue) - self.team_size * 2 + 1):
            players = []
            base_player = queue[i]
            
            # Calculate dynamic tolerance based on wait time
            wait_time = base_player.wait_time()
            tolerance = self.skill_tolerance + (wait_time / 10) * self.tolerance_growth_rate
            
            # Find players within skill tolerance
            for j in range(i, len(queue)):
                player = queue[j]
                if abs(player.skill_rating - base_player.skill_rating) <= tolerance:
                    players.append(player)
                    
                    if len(players) >= self.team_size * 2:
                        # Create match group
                        match_group = MatchGroup(players=players[:self.team_size * 2])
                        match_group.calculate_stats()
                        
                        # Remove matched players from queue
                        for p in match_group.players:
                            self.queues[queue_type].remove(p)
                        
                        return match_group
        
        # Force match for players waiting too long
        for player in queue:
            if player.wait_time() > self.max_wait_time:
                # Take the first available players
                players = queue[:self.team_size * 2]
                match_group = MatchGroup(players=players)
                match_group.calculate_stats()
                
                # Remove matched players
                for p in players:
                    self.queues[queue_type].remove(p)
                
                return match_group
        
        return None
    
    def create_balanced_teams(self, match_group: MatchGroup) -> Tuple[List[str], List[str]]:
        """Create balanced teams from a match group"""
        players = sorted(match_group.players, key=lambda p: p.skill_rating, reverse=True)
        
        team1 = []
        team2 = []
        team1_skill = 0.0
        team2_skill = 0.0
        
        # Distribute players to balance skill
        for player in players:
            if team1_skill <= team2_skill and len(team1) < self.team_size:
                team1.append(player.player_id)
                team1_skill += player.skill_rating
            else:
                team2.append(player.player_id)
                team2_skill += player.skill_rating
        
        return team1, team2
    
    def get_queue_stats(self, queue_type: str = "default") -> Dict[str, Any]:
        """Get queue statistics"""
        if queue_type not in self.queues:
            return {"players_in_queue": 0}
        
        queue = self.queues[queue_type]
        if not queue:
            return {"players_in_queue": 0}
        
        wait_times = [p.wait_time() for p in queue]
        skill_ratings = [p.skill_rating for p in queue]
        
        return {
            "players_in_queue": len(queue),
            "average_wait_time": sum(wait_times) / len(wait_times),
            "max_wait_time": max(wait_times),
            "average_skill_rating": sum(skill_ratings) / len(skill_ratings),
            "skill_range": max(skill_ratings) - min(skill_ratings) if skill_ratings else 0
        }
    
    def get_player_position(self, player_id: str, queue_type: str = "default") -> Optional[int]:
        """Get player's position in queue"""
        if queue_type not in self.queues:
            return None
        
        for i, player in enumerate(self.queues[queue_type]):
            if player.player_id == player_id:
                return i + 1
        
        return None