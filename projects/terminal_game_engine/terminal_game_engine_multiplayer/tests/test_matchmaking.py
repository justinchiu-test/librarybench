"""Tests for matchmaking engine"""

import pytest
from pytermgame.matchmaking import MatchmakingEngine, PlayerProfile, MatchResult, MatchmakingMode


class TestPlayerProfile:
    """Test PlayerProfile class"""
    
    def test_profile_creation(self):
        """Test creating player profile"""
        profile = PlayerProfile(
            player_id="player1",
            skill_rating=1200.0,
            games_played=10,
            win_rate=0.6
        )
        
        assert profile.player_id == "player1"
        assert profile.skill_rating == 1200.0
        assert profile.games_played == 10
        assert profile.win_rate == 0.6
        assert profile.region == "default"
    
    def test_update_rating(self):
        """Test updating skill rating"""
        profile = PlayerProfile(player_id="player1", skill_rating=1000.0)
        
        # Increase rating
        profile.update_rating(100.0)
        assert profile.skill_rating == 1100.0
        
        # Decrease rating
        profile.update_rating(-200.0)
        assert profile.skill_rating == 900.0
        
        # Test bounds
        profile.update_rating(-1000.0)
        assert profile.skill_rating == 0.0  # Min bound
        
        profile.update_rating(10000.0)
        assert profile.skill_rating == 5000.0  # Max bound
    
    def test_update_stats(self):
        """Test updating player statistics"""
        profile = PlayerProfile(player_id="player1")
        
        # First game - win
        profile.update_stats(won=True)
        assert profile.games_played == 1
        assert profile.win_rate == 1.0
        
        # Second game - loss
        profile.update_stats(won=False)
        assert profile.games_played == 2
        assert profile.win_rate == 0.5
        
        # More games
        profile.update_stats(won=True)
        profile.update_stats(won=True)
        assert profile.games_played == 4
        assert profile.win_rate == 0.75  # 3 wins out of 4


class TestMatchResult:
    """Test MatchResult class"""
    
    def test_match_result_creation(self):
        """Test creating match result"""
        result = MatchResult(
            match_id="match123",
            teams=[["player1", "player2"], ["player3", "player4"]],
            average_skill=1100.0,
            skill_variance=50.0,
            match_quality=0.85,
            mode=MatchmakingMode.SKILL_BASED
        )
        
        assert result.match_id == "match123"
        assert len(result.teams) == 2
        assert len(result.teams[0]) == 2
        assert result.average_skill == 1100.0
        assert result.match_quality == 0.85
        assert result.mode == MatchmakingMode.SKILL_BASED


class TestMatchmakingEngine:
    """Test MatchmakingEngine class"""
    
    def test_engine_creation(self):
        """Test creating matchmaking engine"""
        engine = MatchmakingEngine()
        
        assert engine.elo_k_factor == 32
        assert engine.team_size == 2
        assert engine.max_skill_difference == 200
        assert engine.new_player_games == 10
    
    def test_register_player(self):
        """Test registering players"""
        engine = MatchmakingEngine()
        
        # Register new player
        profile = engine.register_player("player1", 1500.0)
        assert profile.player_id == "player1"
        assert profile.skill_rating == 1500.0
        assert "player1" in engine.player_profiles
        
        # Register existing player (should return existing)
        profile2 = engine.register_player("player1", 2000.0)
        assert profile2.skill_rating == 1500.0  # Unchanged
    
    def test_update_player_profile(self):
        """Test updating player profiles"""
        engine = MatchmakingEngine()
        engine.register_player("player1")
        
        # Update profile
        success = engine.update_player_profile(
            "player1",
            preferred_modes=["ranked", "quick"],
            region="us-west"
        )
        assert success is True
        
        profile = engine.player_profiles["player1"]
        assert profile.preferred_modes == ["ranked", "quick"]
        assert profile.region == "us-west"
        
        # Update non-existent player
        success = engine.update_player_profile("player99", region="eu")
        assert success is False
    
    def test_create_match(self):
        """Test creating matches"""
        engine = MatchmakingEngine()
        
        # Register players with different skills
        players = []
        for i in range(4):
            player_id = f"player{i}"
            engine.register_player(player_id, 1000 + i * 100)
            players.append(player_id)
        
        # Create match
        match = engine.create_match(players, MatchmakingMode.SKILL_BASED)
        assert match is not None
        assert len(match.teams) == 2
        assert len(match.teams[0]) == 2
        assert len(match.teams[1]) == 2
        assert match.average_skill == 1150.0  # (1000+1100+1200+1300)/4
        
        # Not enough players
        match = engine.create_match(["player1"], MatchmakingMode.QUICK_MATCH)
        assert match is None
    
    def test_balanced_teams(self):
        """Test team balancing algorithm"""
        engine = MatchmakingEngine()
        
        # Create players with varying skills
        # Skills: 2000, 1500, 1200, 1000
        engine.register_player("pro", 2000.0)
        engine.register_player("good", 1500.0)
        engine.register_player("average", 1200.0)
        engine.register_player("newbie", 1000.0)
        
        match = engine.create_match(
            ["pro", "good", "average", "newbie"],
            MatchmakingMode.SKILL_BASED
        )
        
        # Teams should be balanced
        # Expected: [pro, newbie] vs [good, average]
        # Team 1: 2000 + 1000 = 3000
        # Team 2: 1500 + 1200 = 2700
        # Close enough for good balance
        
        team1_total = sum(engine.player_profiles[p].skill_rating for p in match.teams[0])
        team2_total = sum(engine.player_profiles[p].skill_rating for p in match.teams[1])
        
        # Teams should be within reasonable balance
        assert abs(team1_total - team2_total) < 500
    
    def test_match_quality_calculation(self):
        """Test match quality metrics"""
        engine = MatchmakingEngine()
        
        # Similar skill players
        similar_players = []
        for i in range(4):
            player_id = f"similar{i}"
            engine.register_player(player_id, 1000 + i * 10)  # Small differences
            similar_players.append(player_id)
        
        match = engine.create_match(similar_players)
        assert match.match_quality > 0.8  # High quality due to similar skills
        
        # Very different skill players
        different_players = []
        for i in range(4):
            player_id = f"different{i}"
            engine.register_player(player_id, 500 + i * 500)  # Large differences
            different_players.append(player_id)
        
        match = engine.create_match(different_players)
        assert match.match_quality < 0.5  # Low quality due to skill variance
    
    def test_update_ratings(self):
        """Test ELO rating updates after match"""
        engine = MatchmakingEngine()
        
        # Create players
        for i in range(4):
            engine.register_player(f"player{i}", 1000.0)
        
        # Create match
        match = engine.create_match(
            ["player0", "player1", "player2", "player3"]
        )
        
        # Team 0 wins
        engine.update_ratings(match, winning_team_index=0)
        
        # Winners should gain rating
        for player_id in match.teams[0]:
            assert engine.player_profiles[player_id].skill_rating > 1000.0
            assert engine.player_profiles[player_id].win_rate == 1.0
        
        # Losers should lose rating
        for player_id in match.teams[1]:
            assert engine.player_profiles[player_id].skill_rating < 1000.0
            assert engine.player_profiles[player_id].win_rate == 0.0
    
    def test_k_factor_adjustment(self):
        """Test K-factor adjustments based on experience"""
        engine = MatchmakingEngine()
        
        # New player (high K-factor)
        new_player = engine.register_player("newbie", 1000.0)
        new_player.games_played = 5
        k_factor = engine._get_k_factor(new_player)
        assert k_factor == 64  # Double the base K-factor
        
        # Experienced player (normal K-factor)
        exp_player = engine.register_player("veteran", 1500.0)
        exp_player.games_played = 50
        k_factor = engine._get_k_factor(exp_player)
        assert k_factor == 32  # Base K-factor
        
        # High-rated player (low K-factor)
        pro_player = engine.register_player("pro", 2500.0)
        pro_player.games_played = 100
        k_factor = engine._get_k_factor(pro_player)
        assert k_factor == 16  # Half the base K-factor
    
    def test_find_suitable_opponents(self):
        """Test finding suitable opponents"""
        engine = MatchmakingEngine()
        
        # Create players with various attributes
        engine.register_player("player1", 1000.0)
        engine.player_profiles["player1"].region = "us-west"
        
        candidates = []
        for i in range(10):
            player_id = f"candidate{i}"
            rating = 800 + i * 50
            profile = engine.register_player(player_id, rating)
            profile.region = "us-west" if i % 2 == 0 else "eu"
            profile.games_played = i * 10
            candidates.append(player_id)
        
        # Find suitable opponents
        suitable = engine.find_suitable_opponents("player1", candidates, max_results=5)
        
        assert len(suitable) == 5
        
        # Should prefer similar skill and same region
        top_match = suitable[0]
        top_profile = engine.player_profiles[top_match]
        assert abs(top_profile.skill_rating - 1000.0) <= 200  # Within skill range
    
    def test_match_scoring(self):
        """Test match scoring between players"""
        engine = MatchmakingEngine()
        
        player1 = engine.register_player("player1", 1000.0)
        player1.games_played = 50
        player1.region = "us"
        
        # Perfect match
        player2 = engine.register_player("player2", 1050.0)
        player2.games_played = 45
        player2.region = "us"
        
        score = engine._calculate_match_score(player1, player2)
        assert score > 0.8  # High score for good match
        
        # Poor match
        player3 = engine.register_player("player3", 2000.0)
        player3.games_played = 200
        player3.region = "eu"
        
        score = engine._calculate_match_score(player1, player3)
        assert score < 0.3  # Low score for poor match
    
    def test_leaderboard(self):
        """Test getting leaderboard"""
        engine = MatchmakingEngine()
        
        # Create players with different ratings
        ratings = [2000, 1500, 1800, 1200, 2200, 900]
        for i, rating in enumerate(ratings):
            engine.register_player(f"player{i}", rating)
        
        # Get top 3
        leaderboard = engine.get_leaderboard(limit=3)
        
        assert len(leaderboard) == 3
        assert leaderboard[0].skill_rating == 2200
        assert leaderboard[1].skill_rating == 2000
        assert leaderboard[2].skill_rating == 1800


def test_matchmaking_scenarios():
    """Test various matchmaking scenarios"""
    engine = MatchmakingEngine()
    
    # Scenario 1: Odd number of players
    players = []
    for i in range(5):
        player_id = f"player{i}"
        engine.register_player(player_id, 1000 + i * 50)
        players.append(player_id)
    
    # Should create match with 4 players
    match = engine.create_match(players)
    assert match is not None
    total_players = sum(len(team) for team in match.teams)
    assert total_players == 4
    
    # Scenario 2: Large skill differences
    engine.register_player("grandmaster", 3000.0)
    engine.register_player("bronze", 500.0)
    engine.register_player("silver", 800.0)
    engine.register_player("gold", 1200.0)
    
    match = engine.create_match(
        ["grandmaster", "bronze", "silver", "gold"]
    )
    
    # Should still create match but with low quality
    assert match is not None
    assert match.match_quality < 0.5
    
    # Scenario 3: Regional preferences
    us_players = []
    eu_players = []
    
    for i in range(4):
        us_id = f"us_player{i}"
        eu_id = f"eu_player{i}"
        
        us_profile = engine.register_player(us_id, 1000.0)
        us_profile.region = "us"
        us_players.append(us_id)
        
        eu_profile = engine.register_player(eu_id, 1000.0)
        eu_profile.region = "eu"
        eu_players.append(eu_id)
    
    # Find opponents for US player
    suitable = engine.find_suitable_opponents(
        us_players[0],
        us_players[1:] + eu_players
    )
    
    # Should prefer US players
    us_count = sum(1 for p in suitable[:3] if p.startswith("us_"))
    assert us_count >= 2