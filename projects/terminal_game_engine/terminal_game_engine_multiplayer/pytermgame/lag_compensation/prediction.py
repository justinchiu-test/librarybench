"""Client-side prediction for lag compensation"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
import time
from collections import deque


class PredictionState(BaseModel):
    """Predicted client state"""
    sequence_number: int
    timestamp: float
    position: Dict[str, float]
    velocity: Dict[str, float]
    input: Dict[str, Any]
    confirmed: bool = Field(False, description="Whether state is confirmed by server")


class ClientPrediction:
    """Handles client-side prediction"""
    
    def __init__(self, max_predictions: int = 120):
        self.max_predictions = max_predictions
        self.predictions: deque[PredictionState] = deque(maxlen=max_predictions)
        self.last_confirmed_state: Optional[PredictionState] = None
        self.current_sequence = 0
        self.prediction_enabled = True
    
    def predict_movement(self, current_position: Dict[str, float], 
                        current_velocity: Dict[str, float],
                        input_data: Dict[str, Any], 
                        delta_time: float) -> Dict[str, float]:
        """Predict next position based on input"""
        if not self.prediction_enabled:
            return current_position
        
        # Basic physics prediction
        predicted_position = {
            "x": current_position["x"] + current_velocity["x"] * delta_time,
            "y": current_position["y"] + current_velocity["y"] * delta_time
        }
        
        # Apply input to velocity
        if "move_x" in input_data:
            predicted_position["x"] += input_data["move_x"] * delta_time
        if "move_y" in input_data:
            predicted_position["y"] += input_data["move_y"] * delta_time
        
        # Store prediction
        self.current_sequence += 1
        prediction = PredictionState(
            sequence_number=self.current_sequence,
            timestamp=time.time(),
            position=predicted_position,
            velocity=current_velocity,
            input=input_data
        )
        
        self.predictions.append(prediction)
        
        return predicted_position
    
    def confirm_state(self, sequence_number: int, server_position: Dict[str, float], 
                     server_velocity: Dict[str, float]):
        """Confirm a predicted state with server authoritative state"""
        # Find the prediction
        prediction_found = False
        for prediction in self.predictions:
            if prediction.sequence_number == sequence_number:
                prediction.confirmed = True
                prediction.position = server_position
                prediction.velocity = server_velocity
                self.last_confirmed_state = prediction
                prediction_found = True
                break
        
        if prediction_found:
            # Remove old predictions
            while self.predictions and self.predictions[0].sequence_number <= sequence_number:
                self.predictions.popleft()
    
    def get_corrected_position(self) -> Optional[Dict[str, float]]:
        """Get the current position after server reconciliation"""
        if not self.last_confirmed_state:
            return None
        
        # Start from last confirmed state
        position = self.last_confirmed_state.position.copy()
        velocity = self.last_confirmed_state.velocity.copy()
        
        # Replay unconfirmed predictions
        for prediction in self.predictions:
            if prediction.sequence_number > self.last_confirmed_state.sequence_number:
                # Simple replay of prediction
                delta_time = 1/60.0  # Assume 60 FPS
                position["x"] = position["x"] + velocity["x"] * delta_time
                position["y"] = position["y"] + velocity["y"] * delta_time
                
                # Apply input
                if "move_x" in prediction.input:
                    position["x"] += prediction.input["move_x"] * delta_time
                if "move_y" in prediction.input:
                    position["y"] += prediction.input["move_y"] * delta_time
        
        return position
    
    def get_prediction_error(self) -> float:
        """Calculate prediction error for diagnostics"""
        if not self.last_confirmed_state or not self.predictions:
            return 0.0
        
        # Find corresponding prediction
        for prediction in self.predictions:
            if prediction.sequence_number == self.last_confirmed_state.sequence_number:
                # Calculate distance between predicted and actual
                dx = prediction.position["x"] - self.last_confirmed_state.position["x"]
                dy = prediction.position["y"] - self.last_confirmed_state.position["y"]
                return (dx ** 2 + dy ** 2) ** 0.5
        
        return 0.0
    
    def reset(self):
        """Reset prediction state"""
        self.predictions.clear()
        self.last_confirmed_state = None
        self.current_sequence = 0