"""Matchmaking engine implementation"""

from typing import List, Dict, Optional, Tuple, Any
from pydantic import BaseModel, Field
import time
import math
from enum import Enum


class MatchmakingMode(Enum):
    """Matchmaking modes"""
    SKILL_BASED = "skill_based"
    QUICK_MATCH = "quick_match"
    RANKED = "ranked"
    CUSTOM = "custom"


class PlayerProfile(BaseModel):
    """Player profile for matchmaking"""
    player_id: str
    skill_rating: float = Field(1000.0, ge=0, le=5000)
    games_played: int = Field(0, ge=0)
    win_rate: float = Field(0.5, ge=0, le=1)
    preferred_modes: List[str] = Field(default_factory=list)
    region: str = Field("default")
    latency_tolerance: float = Field(150.0, description="Max acceptable latency in ms")
    
    def update_rating(self, rating_change: float):
        """Update skill rating"""
        self.skill_rating = max(0, min(5000, self.skill_rating + rating_change))
    
    def update_stats(self, won: bool):
        """Update player statistics"""
        self.games_played += 1
        if self.games_played == 1:
            self.win_rate = 1.0 if won else 0.0
        else:
            # Update win rate with new result
            total_wins = int(self.win_rate * (self.games_played - 1))
            if won:
                total_wins += 1
            self.win_rate = total_wins / self.games_played


class MatchResult(BaseModel):
    """Result of matchmaking"""
    match_id: str
    teams: List[List[str]] = Field(description="List of teams with player IDs")
    average_skill: float
    skill_variance: float
    match_quality: float = Field(ge=0, le=1, description="Quality of the match (0-1)")
    mode: MatchmakingMode
    created_at: float = Field(default_factory=time.time)


class MatchmakingEngine:
    """Handles skill-based matchmaking"""
    
    def __init__(self):
        self.player_profiles: Dict[str, PlayerProfile] = {}
        self.elo_k_factor = 32  # ELO K-factor for rating updates
        self.team_size = 2  # Players per team
        self.max_skill_difference = 200  # Maximum skill difference in a match
        self.new_player_games = 10  # Games considered "new player"
        
    def register_player(self, player_id: str, initial_rating: float = 1000.0) -> PlayerProfile:
        """Register a new player"""
        if player_id not in self.player_profiles:
            profile = PlayerProfile(
                player_id=player_id,
                skill_rating=initial_rating
            )
            self.player_profiles[player_id] = profile
            return profile
        return self.player_profiles[player_id]
    
    def update_player_profile(self, player_id: str, **kwargs) -> bool:
        """Update player profile attributes"""
        if player_id not in self.player_profiles:
            return False
        
        profile = self.player_profiles[player_id]
        for key, value in kwargs.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        return True
    
    def create_match(self, players: List[str], mode: MatchmakingMode = MatchmakingMode.SKILL_BASED) -> Optional[MatchResult]:
        """Create a match from a list of players"""
        if len(players) < self.team_size * 2:
            return None
        
        # Get player profiles
        profiles = []
        for player_id in players:
            if player_id in self.player_profiles:
                profiles.append(self.player_profiles[player_id])
            else:
                # Create default profile for unknown players
                profiles.append(self.register_player(player_id))
        
        # Create balanced teams
        teams = self._create_balanced_teams(profiles)
        
        # Calculate match quality
        average_skill, skill_variance, match_quality = self._calculate_match_quality(teams)
        
        return MatchResult(
            match_id=f"match_{int(time.time() * 1000)}",
            teams=teams,
            average_skill=average_skill,
            skill_variance=skill_variance,
            match_quality=match_quality,
            mode=mode
        )
    
    def _create_balanced_teams(self, profiles: List[PlayerProfile]) -> List[List[str]]:
        """Create balanced teams from player profiles"""
        # Sort by skill rating
        sorted_profiles = sorted(profiles, key=lambda p: p.skill_rating, reverse=True)
        
        team1 = []
        team2 = []
        team1_skill = 0.0
        team2_skill = 0.0
        
        # Snake draft: 1-2-2-1-1-2...
        for i, profile in enumerate(sorted_profiles):
            if i % 4 in [0, 3]:  # Team 1 gets 1st, 4th, 5th, 8th...
                team1.append(profile.player_id)
                team1_skill += profile.skill_rating
            else:  # Team 2 gets 2nd, 3rd, 6th, 7th...
                team2.append(profile.player_id)
                team2_skill += profile.skill_rating
        
        return [team1, team2]
    
    def _calculate_match_quality(self, teams: List[List[str]]) -> Tuple[float, float, float]:
        """Calculate match quality metrics"""
        all_ratings = []
        team_averages = []
        
        for team in teams:
            team_ratings = []
            for player_id in team:
                if player_id in self.player_profiles:
                    rating = self.player_profiles[player_id].skill_rating
                    team_ratings.append(rating)
                    all_ratings.append(rating)
            
            if team_ratings:
                team_averages.append(sum(team_ratings) / len(team_ratings))
        
        # Calculate average skill
        average_skill = sum(all_ratings) / len(all_ratings) if all_ratings else 0
        
        # Calculate skill variance
        if len(all_ratings) > 1:
            variance = sum((r - average_skill) ** 2 for r in all_ratings) / len(all_ratings)
            skill_variance = math.sqrt(variance)
        else:
            skill_variance = 0
        
        # Calculate match quality (0-1)
        # Based on team balance and skill variance
        team_balance = 1.0
        if len(team_averages) >= 2:
            avg_diff = abs(team_averages[0] - team_averages[1])
            team_balance = max(0, 1 - avg_diff / 500)  # 500 point difference = 0 quality
        
        variance_factor = max(0, 1 - skill_variance / 1000)  # 1000 variance = 0 quality
        
        match_quality = (team_balance * 0.7 + variance_factor * 0.3)
        
        return average_skill, skill_variance, match_quality
    
    def update_ratings(self, match_result: MatchResult, winning_team_index: int):
        """Update player ratings after a match"""
        if winning_team_index >= len(match_result.teams):
            return
        
        winning_team = match_result.teams[winning_team_index]
        losing_team = match_result.teams[1 - winning_team_index]
        
        # Calculate team ratings
        winning_team_rating = self._get_team_rating(winning_team)
        losing_team_rating = self._get_team_rating(losing_team)
        
        # Calculate expected scores
        expected_win = 1 / (1 + 10 ** ((losing_team_rating - winning_team_rating) / 400))
        expected_loss = 1 - expected_win
        
        # Update ratings
        for player_id in winning_team:
            if player_id in self.player_profiles:
                profile = self.player_profiles[player_id]
                k_factor = self._get_k_factor(profile)
                rating_change = k_factor * (1 - expected_win)
                profile.update_rating(rating_change)
                profile.update_stats(won=True)
        
        for player_id in losing_team:
            if player_id in self.player_profiles:
                profile = self.player_profiles[player_id]
                k_factor = self._get_k_factor(profile)
                rating_change = k_factor * (0 - expected_loss)
                profile.update_rating(rating_change)
                profile.update_stats(won=False)
    
    def _get_team_rating(self, team: List[str]) -> float:
        """Calculate average team rating"""
        ratings = []
        for player_id in team:
            if player_id in self.player_profiles:
                ratings.append(self.player_profiles[player_id].skill_rating)
        
        return sum(ratings) / len(ratings) if ratings else 1000.0
    
    def _get_k_factor(self, profile: PlayerProfile) -> float:
        """Get K-factor for rating update based on player experience"""
        if profile.games_played < self.new_player_games:
            # New players have higher K-factor for faster convergence
            return self.elo_k_factor * 2
        elif profile.skill_rating > 2400:
            # High-rated players have lower K-factor
            return self.elo_k_factor * 0.5
        else:
            return self.elo_k_factor
    
    def find_suitable_opponents(self, player_id: str, candidates: List[str], 
                               max_results: int = 10) -> List[str]:
        """Find suitable opponents for a player"""
        if player_id not in self.player_profiles:
            return candidates[:max_results]
        
        player_profile = self.player_profiles[player_id]
        
        # Score each candidate
        scored_candidates = []
        for candidate_id in candidates:
            if candidate_id == player_id:
                continue
            
            if candidate_id in self.player_profiles:
                candidate_profile = self.player_profiles[candidate_id]
                score = self._calculate_match_score(player_profile, candidate_profile)
                scored_candidates.append((candidate_id, score))
        
        # Sort by score (higher is better)
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        return [candidate_id for candidate_id, _ in scored_candidates[:max_results]]
    
    def _calculate_match_score(self, player1: PlayerProfile, player2: PlayerProfile) -> float:
        """Calculate match score between two players"""
        # Skill difference factor
        skill_diff = abs(player1.skill_rating - player2.skill_rating)
        skill_score = max(0, 1 - skill_diff / self.max_skill_difference)
        
        # Experience difference factor
        exp_diff = abs(player1.games_played - player2.games_played)
        exp_score = max(0, 1 - exp_diff / 100)  # 100 games difference = 0 score
        
        # Region match factor
        region_score = 1.0 if player1.region == player2.region else 0.5
        
        # Combined score
        return skill_score * 0.6 + exp_score * 0.2 + region_score * 0.2
    
    def get_leaderboard(self, limit: int = 10) -> List[PlayerProfile]:
        """Get top players by rating"""
        sorted_profiles = sorted(
            self.player_profiles.values(),
            key=lambda p: p.skill_rating,
            reverse=True
        )
        return sorted_profiles[:limit]