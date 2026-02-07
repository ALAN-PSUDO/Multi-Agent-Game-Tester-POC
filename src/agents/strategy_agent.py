"""Strategy agent for determining test strategies."""

from typing import Dict, Any, List
from .base_agent import BaseAgent
from loguru import logger
import random


class StrategyAgent(BaseAgent):
    """
    Agent responsible for analyzing exploration results and determining
    optimal testing strategies based on the discovered game structure.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("StrategyAgent", config)
        self.learning_rate = config.get('learning_rate', 0.1)
        self.exploration_factor = config.get('exploration_factor', 0.2)
        self.strategies = []
        
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze game structure and create testing strategy.
        
        Args:
            context: Must contain exploration results
            
        Returns:
            Dict with testing strategy
        """
        self.log_action("Generating testing strategy")
        
        exploration_data = context.get('exploration_results', {})
        game_type = exploration_data.get('game_type', 'unknown')
        game_controls = exploration_data.get('game_controls', [])
        interface_map = exploration_data.get('interface_map', {})
        
        # Generate strategy based on game type
        strategy = self._generate_strategy(game_type, game_controls, interface_map)
        
        # Create test sequence
        test_sequence = self._create_test_sequence(strategy, game_controls)
        
        result = {
            'success': True,
            'game_type': game_type,
            'strategy': strategy,
            'test_sequence': test_sequence,
            'priority_actions': self._prioritize_actions(game_controls)
        }
        
        self.strategies.append(strategy)
        self.log_action("Strategy generated", {'strategy_type': strategy['type']})
        
        return result
        
    def _generate_strategy(self, game_type: str, controls: List, interface_map: Dict) -> Dict[str, Any]:
        """Generate testing strategy based on game characteristics."""
        strategy = {
            'type': game_type,
            'approach': 'exploratory',
            'focus_areas': [],
            'test_patterns': []
        }
        
        if game_type == 'math_game':
            strategy['approach'] = 'systematic'
            strategy['focus_areas'] = ['input_validation', 'calculation_accuracy', 'edge_cases']
            strategy['test_patterns'] = [
                'test_valid_inputs',
                'test_invalid_inputs',
                'test_boundary_values',
                'test_operation_sequence'
            ]
            
        elif game_type == 'puzzle_game':
            strategy['approach'] = 'heuristic'
            strategy['focus_areas'] = ['move_validation', 'win_conditions', 'reset_functionality']
            strategy['test_patterns'] = [
                'test_all_moves',
                'test_win_scenario',
                'test_reset',
                'test_hint_system'
            ]
            
        elif game_type == 'canvas_game':
            strategy['approach'] = 'interaction_based'
            strategy['focus_areas'] = ['click_interactions', 'visual_feedback', 'game_state']
            strategy['test_patterns'] = [
                'test_click_positions',
                'test_drag_actions',
                'test_game_progression'
            ]
            
        else:
            # Default exploratory strategy
            strategy['approach'] = 'exploratory'
            strategy['focus_areas'] = ['basic_interactions', 'navigation', 'functionality']
            strategy['test_patterns'] = [
                'test_all_buttons',
                'test_all_links',
                'test_form_inputs'
            ]
            
        # Add control-specific patterns
        if controls:
            strategy['control_testing'] = [
                {'action': 'click', 'targets': [c['element'] for c in controls if c.get('role') != 'input']},
                {'action': 'input', 'targets': [c['element'] for c in controls if c.get('role') == 'input']}
            ]
            
        return strategy
        
    def _create_test_sequence(self, strategy: Dict, controls: List) -> List[Dict[str, Any]]:
        """Create a sequence of test actions based on strategy."""
        sequence = []
        
        # Start with initialization actions
        for control in controls:
            if control.get('role') in ['start', 'play']:
                sequence.append({
                    'phase': 'initialization',
                    'action': 'click',
                    'target': control['element'],
                    'priority': 1
                })
                
        # Add exploration actions
        for pattern in strategy.get('test_patterns', []):
            if 'input' in pattern:
                sequence.append({
                    'phase': 'testing',
                    'action': 'input_test',
                    'pattern': pattern,
                    'priority': 2
                })
            elif 'click' in pattern or 'button' in pattern:
                sequence.append({
                    'phase': 'testing',
                    'action': 'interaction_test',
                    'pattern': pattern,
                    'priority': 2
                })
                
        # Add validation actions
        sequence.append({
            'phase': 'validation',
            'action': 'verify_state',
            'priority': 3
        })
        
        # Sort by priority
        sequence.sort(key=lambda x: x.get('priority', 99))
        
        return sequence
        
    def _prioritize_actions(self, controls: List) -> List[Dict[str, Any]]:
        """Prioritize actions based on confidence and game logic."""
        prioritized = []
        
        # Sort controls by confidence
        sorted_controls = sorted(controls, key=lambda x: x.get('confidence', 0), reverse=True)
        
        for control in sorted_controls[:10]:  # Top 10 controls
            role = control.get('role', 'unknown')
            priority = self._get_role_priority(role)
            
            prioritized.append({
                'element': control['element'],
                'role': role,
                'priority': priority,
                'confidence': control.get('confidence', 0)
            })
            
        return prioritized
        
    def _get_role_priority(self, role: str) -> int:
        """Get priority level for a control role."""
        priority_map = {
            'start': 1,
            'play': 1,
            'submit': 2,
            'check': 2,
            'next': 3,
            'hint': 4,
            'reset': 5,
            'pause': 6,
        }
        return priority_map.get(role, 10)
        
    def adapt_strategy(self, feedback: Dict[str, Any]):
        """
        Adapt strategy based on execution feedback.
        This implements basic reinforcement learning.
        
        Args:
            feedback: Feedback from execution agent
        """
        self.log_action("Adapting strategy based on feedback")
        
        success_rate = feedback.get('success_rate', 0)
        
        # Adjust exploration factor based on success
        if success_rate < 0.5:
            # Increase exploration if success rate is low
            self.exploration_factor = min(0.5, self.exploration_factor + self.learning_rate)
        else:
            # Decrease exploration if doing well
            self.exploration_factor = max(0.1, self.exploration_factor - self.learning_rate)
            
        self.log_action("Strategy adapted", {
            'new_exploration_factor': self.exploration_factor
        })
