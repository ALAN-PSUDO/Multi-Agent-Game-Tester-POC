"""Integration tests for the full system."""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestSystemIntegration:
    """Test full system integration."""
    
    @pytest.mark.skip(reason="Requires actual browser and game URL")
    def test_full_workflow(self):
        """Test complete testing workflow."""
        from src.orchestrator import GameTesterOrchestrator
        
        # This would require actual browser setup
        orchestrator = GameTesterOrchestrator("config.yaml")
        
        # Test with a simple HTML page
        test_url = "about:blank"
        
        result = orchestrator.test_game(test_url)
        
        # Basic validation
        assert 'success' in result
        assert 'phases' in result
        
    def test_orchestrator_initialization(self):
        """Test orchestrator can be initialized."""
        from src.orchestrator import GameTesterOrchestrator
        import tempfile
        import yaml
        
        # Create a temporary config
        config = {
            'browser': {'type': 'chrome', 'headless': True},
            'agents': {
                'exploration': {'enabled': True},
                'strategy': {'enabled': True},
                'execution': {'enabled': True},
                'validation': {'enabled': True}
            },
            'heuristics': {'enabled': False, 'save_patterns': False}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            config_path = f.name
            
        try:
            orchestrator = GameTesterOrchestrator(config_path)
            
            assert orchestrator.exploration_agent is not None
            assert orchestrator.strategy_agent is not None
            assert orchestrator.execution_agent is not None
            assert orchestrator.validation_agent is not None
        finally:
            import os
            os.unlink(config_path)
            
    def test_agent_coordination(self):
        """Test that agents can be coordinated."""
        from src.agents.exploration_agent import ExplorationAgent
        from src.agents.strategy_agent import StrategyAgent
        
        # Initialize agents
        exploration_agent = ExplorationAgent({})
        strategy_agent = StrategyAgent({})
        
        # Simulate exploration results
        exploration_results = {
            'success': True,
            'game_type': 'math_game',
            'discovered_elements': 5,
            'game_controls': [
                {'element': {'tag': 'button'}, 'role': 'start', 'confidence': 0.9}
            ],
            'interface_map': {'has_canvas': False}
        }
        
        # Strategy should be able to process exploration results
        context = {
            'exploration_results': exploration_results,
            'recommendations': []
        }
        
        strategy_results = strategy_agent.execute(context)
        
        assert strategy_results['success'] == True
        assert 'strategy' in strategy_results
        assert 'test_sequence' in strategy_results


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
