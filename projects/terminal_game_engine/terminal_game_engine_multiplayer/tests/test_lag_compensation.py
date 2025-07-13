"""Tests for lag compensation"""

import pytest
import time
from unittest.mock import Mock

from pytermgame.lag_compensation import (
    LagCompensator,
    ClientPrediction, PredictionState,
    ServerReconciliation, PlayerSnapshot,
    Interpolator, InterpolationSnapshot
)


class TestClientPrediction:
    """Test ClientPrediction class"""
    
    def test_prediction_creation(self):
        """Test creating client prediction"""
        prediction = ClientPrediction(max_predictions=100)
        
        assert prediction.max_predictions == 100
        assert prediction.current_sequence == 0
        assert prediction.prediction_enabled is True
        assert len(prediction.predictions) == 0
    
    def test_predict_movement(self):
        """Test movement prediction"""
        prediction = ClientPrediction()
        
        current_pos = {"x": 100.0, "y": 200.0}
        current_vel = {"x": 10.0, "y": 0.0}
        input_data = {"move_x": 5.0, "move_y": -2.0}
        delta_time = 0.1
        
        # Predict next position
        new_pos = prediction.predict_movement(
            current_pos, current_vel, input_data, delta_time
        )
        
        # Check prediction
        assert new_pos["x"] == 101.5  # 100 + 10*0.1 + 5*0.1
        assert new_pos["y"] == 199.8  # 200 + 0*0.1 + (-2)*0.1
        
        # Check stored prediction
        assert len(prediction.predictions) == 1
        assert prediction.predictions[0].sequence_number == 1
        assert prediction.predictions[0].position == new_pos
    
    def test_confirm_state(self):
        """Test confirming predicted state"""
        prediction = ClientPrediction()
        
        # Make some predictions
        for i in range(5):
            prediction.predict_movement(
                {"x": i * 10, "y": 0},
                {"x": 1, "y": 0},
                {},
                0.1
            )
        
        # Confirm state from server
        server_pos = {"x": 25.0, "y": 0.0}
        server_vel = {"x": 1.0, "y": 0.0}
        prediction.confirm_state(3, server_pos, server_vel)
        
        # Check confirmation
        assert prediction.last_confirmed_state is not None
        assert prediction.last_confirmed_state.sequence_number == 3
        assert prediction.last_confirmed_state.position == server_pos
        
        # Old predictions should be removed
        assert all(p.sequence_number > 3 for p in prediction.predictions)
    
    def test_corrected_position(self):
        """Test getting corrected position after reconciliation"""
        prediction = ClientPrediction()
        
        # Make initial prediction
        prediction.predict_movement(
            {"x": 0, "y": 0},
            {"x": 10, "y": 0},
            {},
            0.1
        )
        
        # Confirm with different position
        prediction.confirm_state(1, {"x": 0.5, "y": 0}, {"x": 10, "y": 0})
        
        # Make more predictions
        prediction.predict_movement(
            {"x": 1, "y": 0},
            {"x": 10, "y": 0},
            {"move_x": 5},
            0.1
        )
        
        # Get corrected position
        corrected = prediction.get_corrected_position()
        assert corrected is not None
        # Position should be replayed from confirmed state
        assert corrected["x"] > 0.5
    
    def test_prediction_error(self):
        """Test calculating prediction error"""
        prediction = ClientPrediction()
        
        # No predictions yet
        error = prediction.get_prediction_error()
        assert error == 0.0
        
        # Make prediction
        prediction.predictions.append(PredictionState(
            sequence_number=1,
            timestamp=time.time(),
            position={"x": 10, "y": 20},
            velocity={"x": 0, "y": 0},
            input={}
        ))
        
        # Confirm with different position
        prediction.last_confirmed_state = PredictionState(
            sequence_number=1,
            timestamp=time.time(),
            position={"x": 12, "y": 19},
            velocity={"x": 0, "y": 0},
            input={},
            confirmed=True
        )
        
        # Calculate error
        error = prediction.get_prediction_error()
        assert error > 0  # Should have some error
        assert error == pytest.approx(2.236, rel=0.01)  # sqrt(4 + 1)
    
    def test_disable_prediction(self):
        """Test disabling prediction"""
        prediction = ClientPrediction()
        prediction.prediction_enabled = False
        
        current_pos = {"x": 100, "y": 200}
        result = prediction.predict_movement(
            current_pos, {"x": 10, "y": 0}, {}, 0.1
        )
        
        # Should return current position unchanged
        assert result == current_pos
        assert len(prediction.predictions) == 0


class TestServerReconciliation:
    """Test ServerReconciliation class"""
    
    def test_reconciliation_creation(self):
        """Test creating server reconciliation"""
        recon = ServerReconciliation(history_duration=2.0)
        
        assert recon.history_duration == 2.0
        assert recon.max_rewind_time == 0.5
        assert len(recon.player_history) == 0
    
    def test_record_player_state(self):
        """Test recording player states"""
        recon = ServerReconciliation()
        
        # Record states
        for i in range(3):
            recon.record_player_state(
                "player1",
                i,
                {"x": i * 10, "y": 0},
                {"x": 10, "y": 0}
            )
        
        assert "player1" in recon.player_history
        assert len(recon.player_history["player1"]) == 3
        
        # Check snapshots
        snapshots = list(recon.player_history["player1"])
        assert snapshots[0].sequence_number == 0
        assert snapshots[2].position["x"] == 20
    
    def test_get_player_at_time(self):
        """Test getting player state at specific time"""
        recon = ServerReconciliation()
        
        # Record states with specific timestamps
        base_time = time.time()
        for i in range(3):
            snapshot = PlayerSnapshot(
                player_id="player1",
                timestamp=base_time + i * 0.1,
                sequence_number=i,
                position={"x": i * 10, "y": 0},
                velocity={"x": 10, "y": 0}
            )
            recon.player_history["player1"].append(snapshot)
        
        # Get exact timestamp
        state = recon.get_player_at_time("player1", base_time + 0.1)
        assert state is not None
        assert state.position["x"] == 10
        
        # Get interpolated timestamp
        state = recon.get_player_at_time("player1", base_time + 0.15)
        assert state is not None
        assert state.position["x"] == 15  # Interpolated between 10 and 20
    
    def test_verify_hit(self):
        """Test hit verification with lag compensation"""
        recon = ServerReconciliation()
        
        # Record player positions
        current_time = time.time()
        recon.record_player_state(
            "target",
            1,
            {"x": 100, "y": 100},
            {"x": 0, "y": 0},
            {"width": 20, "height": 20}
        )
        
        # Verify hit at recorded position
        hit, position = recon.verify_hit(
            "shooter",
            "target",
            {"x": 100, "y": 100},
            current_time
        )
        assert hit is True
        assert position == {"x": 100, "y": 100}
        
        # Verify miss
        hit, position = recon.verify_hit(
            "shooter",
            "target",
            {"x": 200, "y": 200},
            current_time
        )
        assert hit is False
        assert position is None
    
    def test_rewind_limit(self):
        """Test maximum rewind time limit"""
        recon = ServerReconciliation()
        
        # Record state
        current_time = time.time()
        recon.record_player_state("player1", 1, {"x": 0, "y": 0}, {"x": 0, "y": 0})
        
        # Try to verify hit too far in the past
        old_time = current_time - 1.0  # 1 second ago (exceeds max_rewind_time)
        hit, _ = recon.verify_hit(
            "shooter",
            "player1",
            {"x": 0, "y": 0},
            old_time
        )
        assert hit is False
    
    def test_validate_player_input(self):
        """Test validating player input"""
        recon = ServerReconciliation()
        
        # Record player position
        recon.record_player_state(
            "player1",
            1,
            {"x": 100, "y": 100},
            {"x": 10, "y": 0}
        )
        
        # Valid input (reasonable position)
        valid = recon.validate_player_input(
            "player1",
            2,
            time.time(),
            {"x": 101, "y": 100}
        )
        assert valid is True
        
        # Invalid input (too far from recorded position)
        valid = recon.validate_player_input(
            "player1",
            3,
            time.time(),
            {"x": 200, "y": 100}  # 100 units away
        )
        assert valid is False
    
    def test_world_state_at_time(self):
        """Test getting world state at specific time"""
        recon = ServerReconciliation()
        
        # Record multiple players
        timestamp = time.time()
        recon.record_player_state("player1", 1, {"x": 10, "y": 10}, {"x": 0, "y": 0})
        recon.record_player_state("player2", 1, {"x": 20, "y": 20}, {"x": 0, "y": 0})
        
        # Get world state
        world_state = recon.get_world_state_at_time(timestamp)
        
        assert len(world_state) == 2
        assert "player1" in world_state
        assert "player2" in world_state
        assert world_state["player1"].position["x"] == 10


class TestInterpolator:
    """Test Interpolator class"""
    
    def test_interpolator_creation(self):
        """Test creating interpolator"""
        interp = Interpolator(default_delay=0.15)
        
        assert interp.default_delay == 0.15
        assert interp.smoothing_enabled is True
        assert len(interp.entity_buffers) == 0
    
    def test_update_entity(self):
        """Test updating entity state"""
        interp = Interpolator()
        
        # Update entity
        interp.update_entity(
            "entity1",
            {"x": 100, "y": 200},
            {"x": 10, "y": 0},
            rotation=45.0,
            data={"health": 100}
        )
        
        assert "entity1" in interp.entity_buffers
        buffer = interp.entity_buffers["entity1"]
        assert len(buffer.snapshots) == 1
        assert buffer.snapshots[0].position["x"] == 100
        assert buffer.snapshots[0].rotation == 45.0
    
    def test_interpolated_position(self):
        """Test getting interpolated position"""
        interp = Interpolator(default_delay=0.1)
        
        # Add multiple snapshots
        base_time = time.time() - 0.2  # Start in the past
        for i in range(3):
            snapshot = InterpolationSnapshot(
                timestamp=base_time + i * 0.1,
                position={"x": i * 100, "y": 0},
                velocity={"x": 100, "y": 0},
                rotation=0
            )
            if "entity1" not in interp.entity_buffers:
                from pytermgame.lag_compensation.interpolation import EntityBuffer
                interp.entity_buffers["entity1"] = EntityBuffer(
                    entity_id="entity1",
                    interpolation_delay=0.1
                )
            interp.entity_buffers["entity1"].snapshots.append(snapshot)
        
        # Get interpolated position
        pos = interp.get_interpolated_position("entity1")
        assert pos is not None
        # Position should be interpolated based on delay
        assert 0 <= pos["x"] <= 200
    
    def test_smoothing_disabled(self):
        """Test with smoothing disabled"""
        interp = Interpolator()
        interp.enable_smoothing(False)
        
        # Update entity
        interp.update_entity("entity1", {"x": 100, "y": 200}, {"x": 0, "y": 0})
        
        # Should return latest position without interpolation
        pos = interp.get_interpolated_position("entity1")
        assert pos == {"x": 100, "y": 200}
    
    def test_custom_delay(self):
        """Test custom interpolation delay"""
        interp = Interpolator(default_delay=0.1)
        
        # Create entity with custom delay
        interp.update_entity("entity1", {"x": 0, "y": 0}, {"x": 0, "y": 0})
        interp.set_interpolation_delay("entity1", 0.2)
        
        buffer = interp.entity_buffers["entity1"]
        assert buffer.interpolation_delay == 0.2
    
    def test_remove_entity(self):
        """Test removing entity"""
        interp = Interpolator()
        
        interp.update_entity("entity1", {"x": 0, "y": 0}, {"x": 0, "y": 0})
        assert "entity1" in interp.entity_buffers
        
        interp.remove_entity("entity1")
        assert "entity1" not in interp.entity_buffers


class TestLagCompensator:
    """Test LagCompensator class"""
    
    def test_compensator_creation(self):
        """Test creating lag compensator"""
        comp = LagCompensator()
        
        assert comp.enable_prediction is True
        assert comp.enable_interpolation is True
        assert comp.enable_lag_compensation is True
        assert comp.max_extrapolation_time == 0.2
    
    def test_client_prediction_integration(self):
        """Test client-side prediction integration"""
        comp = LagCompensator()
        
        # Predict movement
        pos = comp.predict_client_movement(
            "player1",
            {"x": 0, "y": 0},
            {"x": 10, "y": 0},
            {"move_x": 5},
            0.1
        )
        
        assert pos["x"] == 1.5  # 0 + 10*0.1 + 5*0.1
        assert "player1" in comp.client_predictions
        
        # Confirm state
        comp.confirm_client_state("player1", 1, {"x": 1.0, "y": 0}, {"x": 10, "y": 0})
        
        # Get corrected position
        corrected = comp.get_corrected_client_position("player1")
        assert corrected is not None
    
    def test_server_reconciliation_integration(self):
        """Test server-side reconciliation integration"""
        comp = LagCompensator()
        
        # Record server state
        comp.record_server_state(
            "player1",
            1,
            {"x": 100, "y": 100},
            {"x": 0, "y": 0},
            {"width": 20, "height": 20}
        )
        
        # Verify hit
        hit, pos = comp.verify_hit(
            "shooter",
            "player1",
            {"x": 100, "y": 100},
            time.time()
        )
        
        assert hit is True
        assert comp.metrics["hit_verifications"]["valid"] == 1
        
        # Validate input
        valid = comp.validate_player_input(
            "player1",
            2,
            time.time(),
            {"x": 105, "y": 100}
        )
        assert valid is True
    
    def test_interpolation_integration(self):
        """Test interpolation integration"""
        comp = LagCompensator()
        
        # Update entities
        for i in range(3):
            comp.update_entity_for_interpolation(
                f"entity{i}",
                {"x": i * 100, "y": 0},
                {"x": 10, "y": 0},
                rotation=i * 45
            )
        
        # Get interpolated positions
        positions = comp.get_all_interpolated_positions()
        assert len(positions) <= 3
        
        # Get single entity
        pos = comp.get_interpolated_position("entity1")
        if pos:  # May be None due to interpolation delay
            assert "x" in pos and "y" in pos
    
    def test_extrapolation(self):
        """Test position extrapolation"""
        comp = LagCompensator()
        
        position = {"x": 100, "y": 200}
        velocity = {"x": 50, "y": -25}
        latency = 0.1  # 100ms
        
        extrapolated = comp.extrapolate_position(position, velocity, latency)
        
        assert extrapolated["x"] == 105  # 100 + 50 * 0.1
        assert extrapolated["y"] == 197.5  # 200 + (-25) * 0.1
        
        # Test max extrapolation limit
        extrapolated = comp.extrapolate_position(position, velocity, 1.0)
        assert extrapolated["x"] == 110  # Limited to 0.2s: 100 + 50 * 0.2
    
    def test_metrics(self):
        """Test lag compensation metrics"""
        comp = LagCompensator()
        
        # Generate some activity
        comp.predict_client_movement("player1", {"x": 0, "y": 0}, {"x": 10, "y": 0}, {}, 0.1)
        comp.confirm_client_state("player1", 1, {"x": 0.5, "y": 0}, {"x": 10, "y": 0})
        
        comp.record_server_state("target", 1, {"x": 0, "y": 0}, {"x": 0, "y": 0})
        comp.verify_hit("shooter", "target", {"x": 0, "y": 0}, time.time())
        comp.verify_hit("shooter", "target", {"x": 100, "y": 0}, time.time())
        
        # Get metrics
        metrics = comp.get_metrics()
        
        assert metrics["average_prediction_error"] > 0
        assert metrics["hit_verification_rate"] == 0.5  # 1 hit, 1 miss
        assert metrics["total_hit_checks"] == 2
        assert metrics["prediction_enabled"] is True
    
    def test_reset_player(self):
        """Test resetting player state"""
        comp = LagCompensator()
        
        # Add player data
        comp.predict_client_movement("player1", {"x": 0, "y": 0}, {"x": 10, "y": 0}, {}, 0.1)
        comp.update_entity_for_interpolation("player1", {"x": 0, "y": 0}, {"x": 0, "y": 0})
        
        # Reset player
        comp.reset_player("player1")
        
        # Check data cleared
        if "player1" in comp.client_predictions:
            assert len(comp.client_predictions["player1"].predictions) == 0
        assert "player1" not in comp.interpolator.entity_buffers
    
    def test_disable_features(self):
        """Test disabling lag compensation features"""
        comp = LagCompensator()
        
        # Disable prediction
        comp.enable_prediction = False
        pos = comp.predict_client_movement("player1", {"x": 0, "y": 0}, {"x": 10, "y": 0}, {}, 0.1)
        assert pos == {"x": 0, "y": 0}  # No prediction
        
        # Disable interpolation
        comp.enable_interpolation = False
        comp.update_entity_for_interpolation("entity1", {"x": 100, "y": 0}, {"x": 0, "y": 0})
        pos = comp.get_interpolated_position("entity1")
        assert pos is None
        
        # Disable lag compensation
        comp.enable_lag_compensation = False
        hit, _ = comp.verify_hit("shooter", "target", {"x": 0, "y": 0}, time.time())
        assert hit is False


@pytest.mark.asyncio
async def test_lag_compensation_integration():
    """Test integrated lag compensation system"""
    comp = LagCompensator()
    
    # Simulate client prediction
    player_id = "player1"
    positions = []
    
    for i in range(10):
        pos = comp.predict_client_movement(
            player_id,
            {"x": i * 10, "y": 0},
            {"x": 10, "y": 0},
            {"move_x": 2},
            0.1
        )
        positions.append(pos)
        
        # Server confirms some states with slight differences
        if i % 3 == 0:
            comp.confirm_client_state(
                player_id,
                i + 1,
                {"x": pos["x"] - 0.5, "y": 0},  # Small correction
                {"x": 10, "y": 0}
            )
    
    # Record server states for hit detection
    comp.record_server_state("target", 1, {"x": 50, "y": 50}, {"x": 0, "y": 0}, {"width": 10, "height": 10})
    
    # Verify hits
    hit1, _ = comp.verify_hit("player1", "target", {"x": 50, "y": 50}, time.time())
    hit2, _ = comp.verify_hit("player1", "target", {"x": 100, "y": 100}, time.time())
    
    assert hit1 is True
    assert hit2 is False
    
    # Update entities for interpolation
    for i in range(5):
        comp.update_entity_for_interpolation(
            f"enemy{i}",
            {"x": i * 20, "y": i * 10},
            {"x": 5, "y": 2}
        )
    
    # Get final metrics
    metrics = comp.get_metrics()
    assert metrics["total_hit_checks"] == 2
    assert metrics["hit_verification_rate"] == 0.5