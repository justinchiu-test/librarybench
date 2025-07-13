"""Tests for spectator mode"""

import pytest
import asyncio
import time
from unittest.mock import Mock

from pytermgame.spectator import (
    SpectatorMode, SpectatorView, ViewMode,
    ReplayRecorder, ReplayFrame
)


class TestSpectatorView:
    """Test SpectatorView class"""
    
    def test_view_creation(self):
        """Test creating spectator view"""
        view = SpectatorView(
            spectator_id="spectator1",
            delay_seconds=5.0
        )
        
        assert view.spectator_id == "spectator1"
        assert view.view_mode == ViewMode.FREE_CAMERA
        assert view.delay_seconds == 5.0
        assert view.zoom_level == 1.0
    
    def test_view_mode_switching(self):
        """Test switching view modes"""
        view = SpectatorView(spectator_id="spec1")
        
        # Switch to follow player
        view.follow_player("player1")
        assert view.view_mode == ViewMode.FOLLOW_PLAYER
        assert view.target_player_id == "player1"
        
        # Switch back to free camera
        view.free_camera()
        assert view.view_mode == ViewMode.FREE_CAMERA
        assert view.target_player_id is None
    
    def test_camera_position(self):
        """Test camera position updates"""
        view = SpectatorView(spectator_id="spec1")
        
        new_position = {"x": 100.0, "y": 200.0}
        view.update_position(new_position)
        
        assert view.camera_position == new_position


class TestSpectatorMode:
    """Test SpectatorMode class"""
    
    @pytest.mark.asyncio
    async def test_spectator_mode_creation(self):
        """Test creating spectator mode"""
        spectator_mode = SpectatorMode("game123", enable_replay=True)
        
        assert spectator_mode.game_id == "game123"
        assert spectator_mode.enable_replay is True
        assert spectator_mode.replay_recorder is not None
        assert spectator_mode.max_spectators == 100
    
    def test_add_remove_spectators(self):
        """Test adding and removing spectators"""
        spectator_mode = SpectatorMode("game123")
        
        # Add spectator
        success = spectator_mode.add_spectator("spec1", delay_seconds=3.0)
        assert success is True
        assert "spec1" in spectator_mode.spectators
        assert spectator_mode.get_spectator_count() == 1
        
        # Try to add same spectator again
        success = spectator_mode.add_spectator("spec1")
        assert success is False
        
        # Remove spectator
        success = spectator_mode.remove_spectator("spec1")
        assert success is True
        assert spectator_mode.get_spectator_count() == 0
    
    def test_max_spectators(self):
        """Test maximum spectator limit"""
        spectator_mode = SpectatorMode("game123")
        spectator_mode.max_spectators = 2
        
        # Add spectators up to limit
        assert spectator_mode.add_spectator("spec1") is True
        assert spectator_mode.add_spectator("spec2") is True
        assert spectator_mode.add_spectator("spec3") is False
    
    def test_game_state_update(self):
        """Test updating game state for spectators"""
        spectator_mode = SpectatorMode("game123", enable_replay=True)
        
        game_state = {
            "players": {
                "player1": {"position": {"x": 10, "y": 20}},
                "player2": {"position": {"x": 30, "y": 40}}
            },
            "tick": 100
        }
        
        events = [{"type": "player_move", "player_id": "player1"}]
        
        spectator_mode.update_game_state(100, game_state, events)
        
        # Check buffer
        assert len(spectator_mode.game_state_buffer) == 1
        assert spectator_mode.game_state_buffer[0]["tick"] == 100
        
        # Check replay recording
        if spectator_mode.replay_recorder:
            assert len(spectator_mode.replay_recorder.frames) == 1
    
    def test_delayed_state(self):
        """Test getting delayed state for spectators"""
        spectator_mode = SpectatorMode("game123")
        spectator_mode.add_spectator("spec1", delay_seconds=1.0)
        
        # Add some states with different timestamps
        current_time = time.time()
        
        # Old state (should be returned)
        old_state = {
            "timestamp": current_time - 2.0,
            "tick": 1,
            "state": {"data": "old"},
            "events": []
        }
        spectator_mode.game_state_buffer.append(old_state)
        
        # Recent state (too new for delayed view)
        new_state = {
            "timestamp": current_time - 0.5,
            "tick": 2,
            "state": {"data": "new"},
            "events": []
        }
        spectator_mode.game_state_buffer.append(new_state)
        
        # Get delayed state
        delayed = spectator_mode.get_delayed_state("spec1")
        assert delayed is not None
        assert delayed["state"]["data"] == "old"
        assert "spectator_info" in delayed
    
    def test_view_mode_management(self):
        """Test managing spectator view modes"""
        spectator_mode = SpectatorMode("game123")
        spectator_mode.add_spectator("spec1")
        
        # Set follow player mode
        success = spectator_mode.set_view_mode(
            "spec1", ViewMode.FOLLOW_PLAYER, "player1"
        )
        assert success is True
        
        spectator = spectator_mode.spectators["spec1"]
        assert spectator.view_mode == ViewMode.FOLLOW_PLAYER
        assert spectator.target_player_id == "player1"
    
    def test_camera_updates(self):
        """Test updating spectator camera"""
        spectator_mode = SpectatorMode("game123")
        spectator_mode.add_spectator("spec1")
        
        success = spectator_mode.update_camera(
            "spec1",
            {"x": 150.0, "y": 250.0},
            zoom=1.5
        )
        assert success is True
        
        spectator = spectator_mode.spectators["spec1"]
        assert spectator.camera_position["x"] == 150.0
        assert spectator.zoom_level == 1.5
    
    def test_spectator_list(self):
        """Test getting spectator list"""
        spectator_mode = SpectatorMode("game123")
        
        spectator_mode.add_spectator("spec1")
        spectator_mode.add_spectator("spec2")
        spectator_mode.set_view_mode("spec2", ViewMode.FOLLOW_PLAYER, "player1")
        
        spectator_list = spectator_mode.get_spectator_list()
        assert len(spectator_list) == 2
        
        # Check spectator info
        spec2_info = next(s for s in spectator_list if s["spectator_id"] == "spec2")
        assert spec2_info["view_mode"] == ViewMode.FOLLOW_PLAYER.value
        assert spec2_info["target_player"] == "player1"
    
    def test_callbacks(self):
        """Test spectator callbacks"""
        spectator_mode = SpectatorMode("game123")
        
        join_events = []
        leave_events = []
        
        spectator_mode.on_spectator_join(lambda sid: join_events.append(sid))
        spectator_mode.on_spectator_leave(lambda sid: leave_events.append(sid))
        
        # Add spectator
        spectator_mode.add_spectator("spec1")
        assert len(join_events) == 1
        assert join_events[0] == "spec1"
        
        # Remove spectator
        spectator_mode.remove_spectator("spec1")
        assert len(leave_events) == 1
        assert leave_events[0] == "spec1"


class TestReplayRecorder:
    """Test ReplayRecorder class"""
    
    def test_replay_creation(self):
        """Test creating replay recorder"""
        recorder = ReplayRecorder(game_id="game123")
        
        assert recorder.game_id == "game123"
        assert recorder.recording is True
        assert len(recorder.frames) == 0
        assert recorder.max_frames == 10000
    
    def test_record_frames(self):
        """Test recording frames"""
        recorder = ReplayRecorder(game_id="game123")
        
        # Record frames
        for i in range(3):
            game_state = {"tick": i, "data": f"state{i}"}
            events = [{"type": "test_event", "tick": i}]
            recorder.record_frame(i, game_state, events)
        
        assert len(recorder.frames) == 3
        assert recorder.frames[0].tick == 0
        assert recorder.frames[2].tick == 2
    
    def test_max_frames_limit(self):
        """Test frame limit enforcement"""
        recorder = ReplayRecorder(game_id="game123", max_frames=5)
        
        # Record more than max frames
        for i in range(10):
            recorder.record_frame(i, {"tick": i}, [])
        
        # Should only keep last 5 frames
        assert len(recorder.frames) == 5
        assert recorder.frames[0].tick == 5  # Oldest frame
        assert recorder.frames[4].tick == 9  # Newest frame
    
    def test_stop_recording(self):
        """Test stopping recording"""
        recorder = ReplayRecorder(game_id="game123")
        
        recorder.record_frame(1, {"data": "test"}, [])
        recorder.stop_recording()
        
        assert recorder.recording is False
        assert "ended_at" in recorder.metadata
        assert "duration" in recorder.metadata
        assert recorder.metadata["total_frames"] == 1
        
        # Try to record after stopping
        recorder.record_frame(2, {"data": "test2"}, [])
        assert len(recorder.frames) == 1  # No new frame added
    
    def test_get_frame(self):
        """Test getting specific frames"""
        recorder = ReplayRecorder(game_id="game123")
        
        for i in range(5):
            recorder.record_frame(i, {"tick": i}, [])
        
        # Get valid frame
        frame = recorder.get_frame(2)
        assert frame is not None
        assert frame.tick == 2
        
        # Get invalid frame
        frame = recorder.get_frame(10)
        assert frame is None
    
    def test_get_frame_at_time(self):
        """Test getting frame by timestamp"""
        recorder = ReplayRecorder(game_id="game123")
        
        # Record frames with specific timestamps
        base_time = time.time()
        for i in range(3):
            frame = ReplayFrame(
                frame_number=i,
                timestamp=base_time + i,
                tick=i,
                game_state={"tick": i},
                events=[]
            )
            recorder.frames.append(frame)
        
        # Get frame at exact timestamp
        frame = recorder.get_frame_at_time(base_time + 1)
        assert frame is not None
        assert frame.tick == 1
        
        # Get frame between timestamps (should return closest)
        frame = recorder.get_frame_at_time(base_time + 1.4)
        assert frame is not None
        assert frame.tick == 1  # Closer to frame 1 than frame 2
    
    def test_frame_compression(self):
        """Test frame compression"""
        frame = ReplayFrame(
            frame_number=0,
            timestamp=time.time(),
            tick=100,
            game_state={"test": "data" * 100},  # Some data to compress
            events=[{"event": i} for i in range(10)]
        )
        
        # Compress and decompress
        compressed = frame.compress()
        decompressed = ReplayFrame.decompress(compressed)
        
        assert decompressed.tick == frame.tick
        assert decompressed.game_state == frame.game_state
        assert decompressed.events == frame.events
    
    def test_replay_save_load(self):
        """Test saving and loading replays"""
        # Create and populate recorder
        recorder = ReplayRecorder(game_id="game123")
        
        for i in range(3):
            recorder.record_frame(i, {"tick": i, "data": f"state{i}"}, [])
        
        recorder.stop_recording()
        
        # Save replay
        replay_data = recorder.save_to_bytes()
        assert replay_data is not None
        assert len(replay_data) > 0
        
        # Load replay
        loaded_recorder = ReplayRecorder.load_from_bytes(replay_data)
        
        assert loaded_recorder.game_id == recorder.game_id
        assert len(loaded_recorder.frames) == len(recorder.frames)
        assert loaded_recorder.recording is False
        
        # Verify frame data
        for i in range(3):
            assert loaded_recorder.frames[i].tick == i
            assert loaded_recorder.frames[i].game_state["data"] == f"state{i}"
    
    def test_get_summary(self):
        """Test getting replay summary"""
        recorder = ReplayRecorder(game_id="game123")
        
        for i in range(5):
            recorder.record_frame(i, {"tick": i}, [])
        
        summary = recorder.get_summary()
        
        assert summary["game_id"] == "game123"
        assert summary["total_frames"] == 5
        assert summary["recording"] is True
        assert "duration" in summary


@pytest.mark.asyncio
async def test_spectator_mode_integration():
    """Test integrated spectator mode functionality"""
    spectator_mode = SpectatorMode("game123", enable_replay=True)
    await spectator_mode.start()
    
    # Add spectators with different delays
    spectator_mode.add_spectator("spec1", delay_seconds=0.5)
    spectator_mode.add_spectator("spec2", delay_seconds=1.0)
    
    # Set one spectator to follow a player
    spectator_mode.set_view_mode("spec2", ViewMode.FOLLOW_PLAYER, "player1")
    
    # Simulate game updates
    for i in range(5):
        game_state = {
            "tick": i,
            "players": {
                "player1": {"position": {"x": i * 10, "y": i * 20}},
                "player2": {"position": {"x": i * 5, "y": i * 15}}
            }
        }
        spectator_mode.update_game_state(i, game_state, [])
        await asyncio.sleep(0.3)
    
    # Check delayed states
    delayed1 = spectator_mode.get_delayed_state("spec1")
    delayed2 = spectator_mode.get_delayed_state("spec2")
    
    # spec2 has longer delay, should see older state
    if delayed1 and delayed2:
        assert delayed2["tick"] <= delayed1["tick"]
    
    # Check replay
    if spectator_mode.replay_recorder:
        assert len(spectator_mode.replay_recorder.frames) == 5
        
        # Save replay
        replay_data = spectator_mode.save_replay()
        assert replay_data is not None
    
    await spectator_mode.stop()