"""Exploration agent for discovering game elements."""

from typing import Dict, Any, List
from .base_agent import BaseAgent
from loguru import logger


class ExplorationAgent(BaseAgent):
    """
    Agent responsible for exploring the game interface and discovering
    interactive elements, patterns, and game mechanics.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("ExplorationAgent", config)
        self.max_depth = config.get('max_depth', 5)
        self.timeout = config.get('timeout', 60)
        self.discovered_elements = []
        
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Explore the game page and discover interactive elements.
        
        Args:
            context: Must contain 'dom_analysis' and 'browser'
            
        Returns:
            Dict with discovered elements and patterns
        """
        self.log_action("Starting exploration")
        
        dom_analysis = context.get('dom_analysis', {})
        browser = context.get('browser')
        
        # Extract interactive elements
        interactive_elements = dom_analysis.get('interactive_elements', [])
        game_indicators = dom_analysis.get('game_indicators', [])
        canvas_elements = dom_analysis.get('canvas_elements', [])
        
        # Categorize elements by type
        categorized = self._categorize_elements(interactive_elements)
        
        # Identify potential game controls
        game_controls = self._identify_game_controls(categorized, game_indicators)
        
        # Map the game interface
        interface_map = self._map_interface(categorized, canvas_elements)
        
        result = {
            'success': True,
            'discovered_elements': len(interactive_elements),
            'categorized_elements': categorized,
            'game_controls': game_controls,
            'interface_map': interface_map,
            'game_type': self._infer_game_type(game_indicators, canvas_elements),
        }
        
        self.discovered_elements = interactive_elements
        self.log_action("Exploration complete", {'elements_found': len(interactive_elements)})
        
        return result
        
    def _categorize_elements(self, elements: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize elements by their type and purpose."""
        categories = {
            'buttons': [],
            'inputs': [],
            'links': [],
            'canvas': [],
            'other': []
        }
        
        for elem in elements:
            tag = elem.get('tag', '').lower()
            elem_type = elem.get('type', '').lower()
            
            if tag == 'button' or (tag == 'input' and elem_type == 'button'):
                categories['buttons'].append(elem)
            elif tag == 'input':
                categories['inputs'].append(elem)
            elif tag == 'a':
                categories['links'].append(elem)
            elif tag == 'canvas':
                categories['canvas'].append(elem)
            else:
                categories['other'].append(elem)
                
        return categories
        
    def _identify_game_controls(self, categorized: Dict[str, List], game_indicators: List[str]) -> List[Dict[str, Any]]:
        """Identify elements that are likely game controls."""
        controls = []
        
        # Look for buttons with game-related text
        game_button_keywords = ['start', 'play', 'pause', 'reset', 'submit', 'check', 'next', 'hint']
        
        for button in categorized.get('buttons', []):
            text = button.get('text', '').lower()
            attrs = button.get('attributes', {})
            
            # Check text content
            for keyword in game_button_keywords:
                if keyword in text:
                    controls.append({
                        'element': button,
                        'role': keyword,
                        'confidence': 0.8
                    })
                    break
                    
            # Check attributes
            for attr_value in attrs.values():
                attr_str = str(attr_value).lower()
                for keyword in game_button_keywords:
                    if keyword in attr_str:
                        controls.append({
                            'element': button,
                            'role': keyword,
                            'confidence': 0.6
                        })
                        break
                        
        return controls
        
    def _map_interface(self, categorized: Dict[str, List], canvas_elements: List) -> Dict[str, Any]:
        """Create a map of the game interface."""
        interface_map = {
            'has_canvas': len(canvas_elements) > 0,
            'primary_canvas': canvas_elements[0] if canvas_elements else None,
            'control_count': len(categorized.get('buttons', [])),
            'input_fields': len(categorized.get('inputs', [])),
            'interactive_zones': []
        }
        
        # Identify interactive zones (groups of controls)
        if categorized.get('buttons'):
            interface_map['interactive_zones'].append({
                'type': 'control_panel',
                'elements': categorized['buttons']
            })
            
        if categorized.get('inputs'):
            interface_map['interactive_zones'].append({
                'type': 'input_area',
                'elements': categorized['inputs']
            })
            
        return interface_map
        
    def _infer_game_type(self, indicators: List[str], canvas_elements: List) -> str:
        """Infer the type of game based on indicators."""
        # Check for math game indicators
        if any('math' in ind.lower() for ind in indicators):
            return 'math_game'
            
        # Check for puzzle game indicators
        if any('puzzle' in ind.lower() for ind in indicators):
            return 'puzzle_game'
            
        # Canvas-based game
        if canvas_elements:
            return 'canvas_game'
            
        # Input-based game
        if any('input' in ind.lower() for ind in indicators):
            return 'input_based_game'
            
        return 'unknown'
