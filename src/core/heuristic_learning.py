"""Heuristic learning module for adaptive game testing."""

from typing import Dict, Any, List, Optional
import json
import os
from pathlib import Path
from loguru import logger
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np


class HeuristicLearning:
    """
    Implements heuristic learning to adapt testing strategies based on
    observed patterns and game characteristics.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize heuristic learning system.
        
        Args:
            config: Heuristics configuration
        """
        self.config = config
        self.enabled = config.get('enabled', True)
        self.save_patterns = config.get('save_patterns', True)
        self.pattern_storage = config.get('pattern_storage', 'heuristics.json')
        self.min_confidence = config.get('min_confidence', 0.6)
        
        self.patterns = []
        self.game_profiles = {}
        
        # Load existing patterns
        self._load_patterns()
        
    def learn_from_execution(self, execution_data: Dict[str, Any], validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Learn patterns from execution and validation data.
        
        Args:
            execution_data: Results from ExecutionAgent
            validation_data: Results from ValidationAgent
            
        Returns:
            Dict with learned patterns
        """
        if not self.enabled:
            return {'learning_enabled': False}
            
        logger.info("Learning from execution data...")
        
        # Extract features
        features = self._extract_features(execution_data, validation_data)
        
        # Identify patterns
        new_patterns = self._identify_patterns(features)
        
        # Update pattern database
        self.patterns.extend(new_patterns)
        
        # Save if configured
        if self.save_patterns and new_patterns:
            self._save_patterns()
            
        return {
            'patterns_learned': len(new_patterns),
            'total_patterns': len(self.patterns),
            'features_extracted': len(features)
        }
        
    def get_recommendations(self, game_type: str, exploration_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get recommendations based on learned patterns.
        
        Args:
            game_type: Type of game being tested
            exploration_data: Data from exploration phase
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Find similar game profiles
        similar_profiles = self._find_similar_profiles(game_type, exploration_data)
        
        for profile in similar_profiles:
            # Extract successful strategies from similar games
            if profile.get('success_rate', 0) > 0.7:
                recommendations.append({
                    'strategy': profile.get('strategy'),
                    'confidence': profile.get('success_rate'),
                    'source': 'historical_data'
                })
                
        # Add pattern-based recommendations
        pattern_recs = self._get_pattern_recommendations(game_type)
        recommendations.extend(pattern_recs)
        
        # Filter by minimum confidence
        recommendations = [r for r in recommendations if r.get('confidence', 0) >= self.min_confidence]
        
        # Sort by confidence
        recommendations.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        return recommendations[:5]  # Top 5 recommendations
        
    def update_game_profile(self, game_url: str, game_data: Dict[str, Any]):
        """
        Update or create a game profile.
        
        Args:
            game_url: URL of the game
            game_data: Comprehensive game data
        """
        profile_key = self._normalize_url(game_url)
        
        if profile_key in self.game_profiles:
            # Update existing profile
            existing = self.game_profiles[profile_key]
            existing['test_count'] = existing.get('test_count', 0) + 1
            existing['last_tested'] = game_data.get('timestamp')
            
            # Update success metrics
            if 'success_rate' in game_data:
                old_rate = existing.get('success_rate', 0)
                new_rate = game_data['success_rate']
                # Weighted average
                existing['success_rate'] = (old_rate + new_rate) / 2
        else:
            # Create new profile
            self.game_profiles[profile_key] = {
                'url': game_url,
                'game_type': game_data.get('game_type'),
                'test_count': 1,
                'first_tested': game_data.get('timestamp'),
                'last_tested': game_data.get('timestamp'),
                'success_rate': game_data.get('success_rate', 0),
                'strategy': game_data.get('strategy'),
                'characteristics': game_data.get('characteristics', {})
            }
            
        if self.save_patterns:
            self._save_patterns()
            
    def _extract_features(self, execution_data: Dict[str, Any], validation_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract features from execution and validation data."""
        features = []
        
        # Success/failure patterns
        success_rate = execution_data.get('success_rate', 0)
        features.append({
            'type': 'success_rate',
            'value': success_rate,
            'category': 'performance'
        })
        
        # Action patterns
        results = execution_data.get('results', [])
        for result in results:
            action_type = result.get('action')
            success = result.get('success', False)
            
            features.append({
                'type': 'action_result',
                'action': action_type,
                'success': success,
                'category': 'behavior'
            })
            
        # Anomaly patterns
        anomalies = validation_data.get('anomalies', [])
        for anomaly in anomalies:
            features.append({
                'type': 'anomaly',
                'anomaly_type': anomaly.get('type'),
                'severity': anomaly.get('severity'),
                'category': 'issues'
            })
            
        return features
        
    def _identify_patterns(self, features: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify patterns from features."""
        patterns = []
        
        # Group features by category
        by_category = {}
        for feature in features:
            category = feature.get('category', 'other')
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(feature)
            
        # Analyze each category
        for category, category_features in by_category.items():
            if category == 'behavior':
                # Find action success patterns
                action_stats = {}
                for f in category_features:
                    action = f.get('action')
                    success = f.get('success', False)
                    
                    if action not in action_stats:
                        action_stats[action] = {'total': 0, 'success': 0}
                    
                    action_stats[action]['total'] += 1
                    if success:
                        action_stats[action]['success'] += 1
                        
                for action, stats in action_stats.items():
                    if stats['total'] > 0:
                        success_rate = stats['success'] / stats['total']
                        patterns.append({
                            'type': 'action_success_pattern',
                            'action': action,
                            'success_rate': success_rate,
                            'sample_size': stats['total'],
                            'confidence': min(1.0, stats['total'] / 10)  # Higher confidence with more samples
                        })
                        
        return patterns
        
    def _find_similar_profiles(self, game_type: str, exploration_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find similar game profiles."""
        similar = []
        
        for profile_key, profile in self.game_profiles.items():
            if profile.get('game_type') == game_type:
                # Calculate similarity score
                similarity = self._calculate_similarity(exploration_data, profile.get('characteristics', {}))
                
                if similarity > 0.5:
                    profile_copy = profile.copy()
                    profile_copy['similarity'] = similarity
                    similar.append(profile_copy)
                    
        # Sort by similarity
        similar.sort(key=lambda x: x.get('similarity', 0), reverse=True)
        
        return similar[:3]  # Top 3 similar profiles
        
    def _calculate_similarity(self, data1: Dict[str, Any], data2: Dict[str, Any]) -> float:
        """Calculate similarity between two game data sets."""
        # Simple similarity based on common keys and values
        common_keys = set(data1.keys()) & set(data2.keys())
        
        if not common_keys:
            return 0.0
            
        matches = 0
        for key in common_keys:
            if data1[key] == data2[key]:
                matches += 1
                
        return matches / len(common_keys)
        
    def _get_pattern_recommendations(self, game_type: str) -> List[Dict[str, Any]]:
        """Get recommendations based on patterns."""
        recommendations = []
        
        # Find patterns relevant to this game type
        relevant_patterns = [p for p in self.patterns if p.get('confidence', 0) > self.min_confidence]
        
        for pattern in relevant_patterns:
            if pattern.get('type') == 'action_success_pattern':
                action = pattern.get('action')
                success_rate = pattern.get('success_rate', 0)
                
                if success_rate > 0.7:
                    recommendations.append({
                        'strategy': f"prioritize_{action}",
                        'confidence': pattern.get('confidence', 0),
                        'source': 'pattern_analysis',
                        'details': pattern
                    })
                    
        return recommendations
        
    def _normalize_url(self, url: str) -> str:
        """Normalize URL for use as profile key."""
        # Remove protocol and www
        normalized = url.lower()
        normalized = normalized.replace('https://', '').replace('http://', '')
        normalized = normalized.replace('www.', '')
        # Remove trailing slash
        if normalized.endswith('/'):
            normalized = normalized[:-1]
        return normalized
        
    def _load_patterns(self):
        """Load patterns from storage."""
        if not self.save_patterns:
            return
            
        if os.path.exists(self.pattern_storage):
            try:
                with open(self.pattern_storage, 'r') as f:
                    data = json.load(f)
                    self.patterns = data.get('patterns', [])
                    self.game_profiles = data.get('game_profiles', {})
                logger.info(f"Loaded {len(self.patterns)} patterns and {len(self.game_profiles)} profiles")
            except Exception as e:
                logger.error(f"Failed to load patterns: {e}")
                
    def _save_patterns(self):
        """Save patterns to storage."""
        if not self.save_patterns:
            return
            
        try:
            data = {
                'patterns': self.patterns,
                'game_profiles': self.game_profiles
            }
            
            with open(self.pattern_storage, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.info(f"Saved {len(self.patterns)} patterns and {len(self.game_profiles)} profiles")
        except Exception as e:
            logger.error(f"Failed to save patterns: {e}")
