"""Main lag compensation system"""

from typing import Dict, Optional, Any, Tuple
import time

from .prediction import ClientPrediction
from .reconciliation import ServerReconciliation
from .interpolation import Interpolator


class LagCompensator:
    """Comprehensive lag compensation system"""
    
    def __init__(self):
        # Client-side components
        self.client_predictions: Dict[str, ClientPrediction] = {}
        self.interpolator = Interpolator()
        
        # Server-side components
        self.server_reconciliation = ServerReconciliation()
        
        # Settings
        self.enable_prediction = True
        self.enable_interpolation = True
        self.enable_lag_compensation = True
        self.max_extrapolation_time = 0.2  # 200ms max extrapolation
        
        # Metrics
        self.metrics = {
            "prediction_errors": [],
            "interpolation_delays": [],
            "hit_verifications": {"valid": 0, "invalid": 0}
        }
    
    # Client-side methods
    
    def create_client_predictor(self, player_id: str) -> ClientPrediction:
        """Create a client predictor for a player"""
        if player_id not in self.client_predictions:
            self.client_predictions[player_id] = ClientPrediction()
        return self.client_predictions[player_id]
    
    def predict_client_movement(self, player_id: str, current_position: Dict[str, float],
                               current_velocity: Dict[str, float], input_data: Dict[str, Any],
                               delta_time: float) -> Dict[str, float]:
        """Predict client movement"""
        if not self.enable_prediction:
            return current_position
        
        predictor = self.create_client_predictor(player_id)
        return predictor.predict_movement(current_position, current_velocity, input_data, delta_time)
    
    def confirm_client_state(self, player_id: str, sequence_number: int,
                           server_position: Dict[str, float], server_velocity: Dict[str, float]):
        """Confirm predicted state with server state"""
        if player_id in self.client_predictions:
            predictor = self.client_predictions[player_id]
            predictor.confirm_state(sequence_number, server_position, server_velocity)
            
            # Track prediction error
            error = predictor.get_prediction_error()
            self.metrics["prediction_errors"].append(error)
            if len(self.metrics["prediction_errors"]) > 100:
                self.metrics["prediction_errors"].pop(0)
    
    def get_corrected_client_position(self, player_id: str) -> Optional[Dict[str, float]]:
        """Get corrected position after reconciliation"""
        if player_id in self.client_predictions:
            return self.client_predictions[player_id].get_corrected_position()
        return None
    
    # Server-side methods
    
    def record_server_state(self, player_id: str, sequence_number: int,
                           position: Dict[str, float], velocity: Dict[str, float],
                           hitbox: Optional[Dict[str, float]] = None):
        """Record player state on server"""
        if self.enable_lag_compensation:
            self.server_reconciliation.record_player_state(
                player_id, sequence_number, position, velocity, hitbox
            )
    
    def verify_hit(self, shooter_id: str, target_id: str, shot_position: Dict[str, float],
                   shot_timestamp: float) -> Tuple[bool, Optional[Dict[str, float]]]:
        """Verify hit with lag compensation"""
        if not self.enable_lag_compensation:
            return False, None
        
        hit, position = self.server_reconciliation.verify_hit(
            shooter_id, target_id, shot_position, shot_timestamp
        )
        
        # Track metrics
        if hit:
            self.metrics["hit_verifications"]["valid"] += 1
        else:
            self.metrics["hit_verifications"]["invalid"] += 1
        
        return hit, position
    
    def validate_player_input(self, player_id: str, input_sequence: int,
                            input_timestamp: float, claimed_position: Dict[str, float]) -> bool:
        """Validate player input against history"""
        if not self.enable_lag_compensation:
            return True
        
        return self.server_reconciliation.validate_player_input(
            player_id, input_sequence, input_timestamp, claimed_position
        )
    
    # Interpolation methods
    
    def update_entity_for_interpolation(self, entity_id: str, position: Dict[str, float],
                                      velocity: Dict[str, float], rotation: float = 0.0,
                                      data: Optional[Dict[str, Any]] = None):
        """Update entity for interpolation"""
        if self.enable_interpolation:
            self.interpolator.update_entity(entity_id, position, velocity, rotation, data)
    
    def get_interpolated_position(self, entity_id: str) -> Optional[Dict[str, float]]:
        """Get interpolated position for smooth rendering"""
        if not self.enable_interpolation:
            return None
        
        return self.interpolator.get_interpolated_position(entity_id)
    
    def get_all_interpolated_positions(self) -> Dict[str, Dict[str, float]]:
        """Get all interpolated positions"""
        if not self.enable_interpolation:
            return {}
        
        positions = {}
        states = self.interpolator.get_all_interpolated_states()
        
        for entity_id, state in states.items():
            positions[entity_id] = state.position
        
        return positions
    
    # Extrapolation for high latency
    
    def extrapolate_position(self, position: Dict[str, float], velocity: Dict[str, float],
                            latency: float) -> Dict[str, float]:
        """Extrapolate position based on latency"""
        # Limit extrapolation time
        extrapolation_time = min(latency, self.max_extrapolation_time)
        
        return {
            "x": position["x"] + velocity["x"] * extrapolation_time,
            "y": position["y"] + velocity["y"] * extrapolation_time
        }
    
    # Utility methods
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get lag compensation metrics"""
        avg_prediction_error = 0.0
        if self.metrics["prediction_errors"]:
            avg_prediction_error = sum(self.metrics["prediction_errors"]) / len(self.metrics["prediction_errors"])
        
        total_hits = (self.metrics["hit_verifications"]["valid"] + 
                     self.metrics["hit_verifications"]["invalid"])
        hit_rate = 0.0
        if total_hits > 0:
            hit_rate = self.metrics["hit_verifications"]["valid"] / total_hits
        
        return {
            "average_prediction_error": avg_prediction_error,
            "hit_verification_rate": hit_rate,
            "total_hit_checks": total_hits,
            "prediction_enabled": self.enable_prediction,
            "interpolation_enabled": self.enable_interpolation,
            "lag_compensation_enabled": self.enable_lag_compensation
        }
    
    def reset_player(self, player_id: str):
        """Reset player's lag compensation state"""
        if player_id in self.client_predictions:
            self.client_predictions[player_id].reset()
        
        self.interpolator.remove_entity(player_id)
    
    def clear(self):
        """Clear all lag compensation data"""
        self.client_predictions.clear()
        self.interpolator.clear()
        self.server_reconciliation.player_history.clear()
        
        # Reset metrics
        self.metrics["prediction_errors"].clear()
        self.metrics["interpolation_delays"].clear()
        self.metrics["hit_verifications"] = {"valid": 0, "invalid": 0}