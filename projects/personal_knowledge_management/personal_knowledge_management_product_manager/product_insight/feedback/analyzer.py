"""
Feedback analysis module for ProductInsight.

This module provides functionality for analyzing customer feedback, including
sentiment analysis and feature extraction.
"""

import re
from typing import Dict, List, Optional, Tuple

import numpy as np
from nltk.sentiment import SentimentIntensityAnalyzer
from pydantic import BaseModel

from product_insight.models import FeedbackItem, SentimentEnum


class SentimentResult(BaseModel):
    """Result of sentiment analysis."""
    
    sentiment: SentimentEnum
    scores: Dict[str, float]


class FeatureExtraction(BaseModel):
    """Result of feature extraction from feedback."""
    
    features: List[str]
    confidence_scores: List[float]


class FeedbackAnalyzer:
    """Analyzes customer feedback for sentiment and feature extraction."""
    
    def __init__(self):
        """Initialize the feedback analyzer."""
        try:
            import nltk
            nltk.download("vader_lexicon", quiet=True)
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
        except ImportError:
            self.sentiment_analyzer = None
            print("NLTK not available, sentiment analysis will be simulated")
    
    def analyze_sentiment(self, text: str) -> SentimentResult:
        """Analyze sentiment of a text.
        
        Args:
            text: Text to analyze
            
        Returns:
            SentimentResult with sentiment category and scores
        """
        if self.sentiment_analyzer:
            # Use NLTK's VADER for sentiment analysis
            scores = self.sentiment_analyzer.polarity_scores(text)
            
            # Map VADER scores to our sentiment enum
            if scores["compound"] >= 0.5:
                sentiment = SentimentEnum.VERY_POSITIVE
            elif scores["compound"] >= 0.1:
                sentiment = SentimentEnum.POSITIVE
            elif scores["compound"] <= -0.5:
                sentiment = SentimentEnum.VERY_NEGATIVE
            elif scores["compound"] <= -0.1:
                sentiment = SentimentEnum.NEGATIVE
            else:
                sentiment = SentimentEnum.NEUTRAL
            
            return SentimentResult(sentiment=sentiment, scores=scores)
        else:
            # Simulate sentiment analysis with a naive approach
            positive_words = ["love", "great", "excellent", "good", "awesome", "amazing"]
            negative_words = ["hate", "terrible", "bad", "awful", "poor", "horrible"]
            
            text_lower = text.lower()
            pos_count = sum(word in text_lower for word in positive_words)
            neg_count = sum(word in text_lower for word in negative_words)
            
            total = pos_count + neg_count
            if total == 0:
                sentiment = SentimentEnum.NEUTRAL
                scores = {"pos": 0.5, "neg": 0.5, "neu": 0.5, "compound": 0.0}
            else:
                pos_ratio = pos_count / total
                neg_ratio = neg_count / total
                
                if pos_ratio >= 0.8:
                    sentiment = SentimentEnum.VERY_POSITIVE
                    compound = 0.8
                elif pos_ratio >= 0.6:
                    sentiment = SentimentEnum.POSITIVE
                    compound = 0.3
                elif neg_ratio >= 0.8:
                    sentiment = SentimentEnum.VERY_NEGATIVE
                    compound = -0.8
                elif neg_ratio >= 0.6:
                    sentiment = SentimentEnum.NEGATIVE
                    compound = -0.3
                else:
                    sentiment = SentimentEnum.NEUTRAL
                    compound = 0.0
                
                scores = {
                    "pos": pos_ratio,
                    "neg": neg_ratio,
                    "neu": 1 - pos_ratio - neg_ratio,
                    "compound": compound
                }
            
            return SentimentResult(sentiment=sentiment, scores=scores)
    
    def extract_features(self, text: str) -> FeatureExtraction:
        """Extract mentioned features or feature requests from feedback.
        
        Args:
            text: Text to analyze
            
        Returns:
            FeatureExtraction with extracted features and confidence scores
        """
        # Look for common feature request patterns
        # This is a simplified implementation, a production version would use more
        # sophisticated NLP techniques
        feature_patterns = [
            r"wish (?:you |the app |it |there was )?(?:had|would add|could add|added) (.+?)(?:\.|\n|$)",
            r"would (?:like|love|prefer) (?:to see |to have |if you |if there was )(.+?)(?:\.|\n|$)",
            r"need (?:the ability |a way |to be able )?to (.+?)(?:\.|\n|$)",
            r"(?:please |can you |should |could you )?add (.+?)(?:\.|\n|$)",
            r"missing (.+?)(?:\.|\n|$)",
            r"(?:it would be |would be |it's |is )(?:nice|great|helpful) (?:to have |to |if )(.+?)(?:\.|\n|$)",
        ]
        
        features = []
        confidence_scores = []
        
        for pattern in feature_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                feature = match.group(1).strip()
                if len(feature) > 5 and len(feature) < 100:  # Simple filtering
                    features.append(feature)
                    confidence_scores.append(0.7)  # Simple confidence score
        
        return FeatureExtraction(features=features, confidence_scores=confidence_scores)
    
    def calculate_impact_score(self, feedback: FeedbackItem) -> float:
        """Calculate an impact score for a feedback item.
        
        The impact score is based on sentiment, feature requests, and other factors.
        
        Args:
            feedback: Feedback item to analyze
            
        Returns:
            Impact score between 0 and 1
        """
        # Base impact factors
        sentiment_factor = self._get_sentiment_factor(feedback.sentiment)
        feature_factor = min(len(feedback.extracted_features) * 0.2, 1.0)
        
        # Customer segment factor
        segment_factor = 1.0
        if feedback.customer_segment:
            # Higher weight for enterprise or high-value segments
            if "enterprise" in feedback.customer_segment.lower():
                segment_factor = 1.5
            elif "premium" in feedback.customer_segment.lower():
                segment_factor = 1.3
        
        # Source factor
        source_factor = 1.0
        if feedback.source:
            # Higher weight for direct feedback methods
            if feedback.source in ["customer_interview", "support_ticket"]:
                source_factor = 1.4
            elif feedback.source in ["survey", "app_feedback"]:
                source_factor = 1.2
        
        # Calculate overall impact
        impact = (sentiment_factor * 0.3 + feature_factor * 0.4) * segment_factor * source_factor
        
        # Normalize to 0-1 range
        return min(max(impact, 0.0), 1.0)
    
    def _get_sentiment_factor(self, sentiment: Optional[SentimentEnum]) -> float:
        """Get a factor based on sentiment for impact calculation."""
        if sentiment is None:
            return 0.5
        
        # Negative sentiment has higher impact than positive
        # (as it indicates problems that need to be addressed)
        sentiment_factors = {
            SentimentEnum.VERY_NEGATIVE: 1.0,
            SentimentEnum.NEGATIVE: 0.8,
            SentimentEnum.NEUTRAL: 0.5,
            SentimentEnum.POSITIVE: 0.3,
            SentimentEnum.VERY_POSITIVE: 0.2,
        }
        
        return sentiment_factors.get(sentiment, 0.5)
    
    def analyze_feedback_item(self, feedback: FeedbackItem) -> FeedbackItem:
        """Analyze a feedback item for sentiment, features, and impact.
        
        Args:
            feedback: Feedback item to analyze
            
        Returns:
            Updated feedback item with analysis results
        """
        # Analyze sentiment
        sentiment_result = self.analyze_sentiment(feedback.content)
        feedback.sentiment = sentiment_result.sentiment
        
        # Extract features
        feature_result = self.extract_features(feedback.content)
        feedback.extracted_features = feature_result.features
        
        # Calculate impact score
        feedback.impact_score = self.calculate_impact_score(feedback)
        
        # Mark as processed
        feedback.processed = True
        
        return feedback
    
    def batch_analyze_feedback(self, feedback_items: List[FeedbackItem]) -> List[FeedbackItem]:
        """Analyze a batch of feedback items.
        
        Args:
            feedback_items: List of feedback items to analyze
            
        Returns:
            Updated feedback items with analysis results
        """
        return [self.analyze_feedback_item(item) for item in feedback_items]