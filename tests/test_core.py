"""Unit tests for core modules."""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.dom_analyzer import DOMAnalyzer


class TestDOMAnalyzer:
    """Test DOM Analyzer functionality."""
    
    def test_initialization(self):
        """Test DOMAnalyzer initialization."""
        config = {
            'interactive_elements': ['button', 'input'],
            'ignore_elements': ['script', 'style'],
            'attribute_priority': ['id', 'class']
        }
        
        analyzer = DOMAnalyzer(config)
        
        assert analyzer.interactive_tags == ['button', 'input']
        assert analyzer.ignore_tags == ['script', 'style']
        assert analyzer.attribute_priority == ['id', 'class']
        
    def test_analyze_page_basic(self):
        """Test basic page analysis."""
        config = {
            'interactive_elements': ['button', 'input'],
            'ignore_elements': ['script'],
            'attribute_priority': ['id', 'class']
        }
        
        analyzer = DOMAnalyzer(config)
        
        # Simple HTML
        html = """
        <html>
            <head><title>Test Game</title></head>
            <body>
                <button id="start">Start Game</button>
                <input type="text" id="answer" />
                <canvas id="gameCanvas"></canvas>
            </body>
        </html>
        """
        
        result = analyzer.analyze_page(html)
        
        assert 'interactive_elements' in result
        assert 'page_structure' in result
        assert 'game_indicators' in result
        assert len(result['interactive_elements']) > 0
        
    def test_detect_game_indicators(self):
        """Test game indicator detection."""
        config = {
            'interactive_elements': ['button'],
            'ignore_elements': ['script'],
            'attribute_priority': ['id']
        }
        
        analyzer = DOMAnalyzer(config)
        
        # HTML with game indicators
        html = """
        <html>
            <body>
                <div id="game-board">
                    <div class="score">Score: 100</div>
                    <button id="play-button">Play Game</button>
                    <canvas id="gameCanvas"></canvas>
                </div>
            </body>
        </html>
        """
        
        result = analyzer.analyze_page(html)
        indicators = result['game_indicators']
        
        # Should detect game-related keywords
        assert len(indicators) > 0
        
    def test_find_clickable_elements(self):
        """Test finding clickable elements."""
        config = {
            'interactive_elements': ['button', 'a', 'input'],
            'ignore_elements': [],
            'attribute_priority': ['id', 'class']
        }
        
        analyzer = DOMAnalyzer(config)
        
        html = """
        <html>
            <body>
                <button id="btn1">Button 1</button>
                <button id="btn2">Button 2</button>
                <a href="#" id="link1">Link</a>
                <input type="text" id="input1" />
            </body>
        </html>
        """
        
        analysis = analyzer.analyze_page(html)
        clickable = analyzer.find_clickable_elements(analysis)
        
        # Should find buttons and links
        assert len(clickable) > 0
        

class TestAgents:
    """Test agent functionality."""
    
    def test_exploration_agent_initialization(self):
        """Test ExplorationAgent initialization."""
        from src.agents.exploration_agent import ExplorationAgent
        
        config = {
            'max_depth': 5,
            'timeout': 60
        }
        
        agent = ExplorationAgent(config)
        
        assert agent.name == "ExplorationAgent"
        assert agent.max_depth == 5
        assert agent.timeout == 60
        
    def test_strategy_agent_initialization(self):
        """Test StrategyAgent initialization."""
        from src.agents.strategy_agent import StrategyAgent
        
        config = {
            'learning_rate': 0.1,
            'exploration_factor': 0.2
        }
        
        agent = StrategyAgent(config)
        
        assert agent.name == "StrategyAgent"
        assert agent.learning_rate == 0.1
        assert agent.exploration_factor == 0.2
        
    def test_execution_agent_initialization(self):
        """Test ExecutionAgent initialization."""
        from src.agents.execution_agent import ExecutionAgent
        
        config = {
            'max_retries': 3,
            'action_delay': 0.5
        }
        
        agent = ExecutionAgent(config)
        
        assert agent.name == "ExecutionAgent"
        assert agent.max_retries == 3
        assert agent.action_delay == 0.5
        
    def test_validation_agent_initialization(self):
        """Test ValidationAgent initialization."""
        from src.agents.validation_agent import ValidationAgent
        
        config = {
            'screenshot_on_error': True,
            'log_level': 'INFO'
        }
        
        agent = ValidationAgent(config)
        
        assert agent.name == "ValidationAgent"
        assert agent.screenshot_on_error == True
        assert agent.log_level == 'INFO'


class TestHeuristicLearning:
    """Test heuristic learning functionality."""
    
    def test_initialization(self):
        """Test HeuristicLearning initialization."""
        from src.core.heuristic_learning import HeuristicLearning
        
        config = {
            'enabled': True,
            'save_patterns': False,  # Don't save during tests
            'min_confidence': 0.6
        }
        
        learning = HeuristicLearning(config)
        
        assert learning.enabled == True
        assert learning.min_confidence == 0.6
        
    def test_extract_features(self):
        """Test feature extraction."""
        from src.core.heuristic_learning import HeuristicLearning
        
        config = {
            'enabled': True,
            'save_patterns': False,
            'min_confidence': 0.6
        }
        
        learning = HeuristicLearning(config)
        
        execution_data = {
            'success_rate': 0.8,
            'results': [
                {'action': 'click', 'success': True},
                {'action': 'input', 'success': True}
            ]
        }
        
        validation_data = {
            'anomalies': []
        }
        
        features = learning._extract_features(execution_data, validation_data)
        
        assert len(features) > 0
        assert any(f['type'] == 'success_rate' for f in features)


class TestReporting:
    """Test reporting functionality."""
    
    def test_report_generator_initialization(self):
        """Test ReportGenerator initialization."""
        from src.utils.reporting import ReportGenerator
        
        generator = ReportGenerator(output_dir="/tmp/test_reports")
        
        assert generator.output_dir.name == "test_reports"
        
    def test_generate_json_report(self):
        """Test JSON report generation."""
        from src.utils.reporting import ReportGenerator
        import json
        import os
        
        generator = ReportGenerator(output_dir="/tmp/test_reports")
        
        report_data = {
            'success': True,
            'game_url': 'https://example.com/game',
            'summary': {
                'overall_success_rate': 0.85,
                'health_score': 90.0
            }
        }
        
        filepath = generator.generate_json_report(report_data, "test_report.json")
        
        assert os.path.exists(filepath)
        
        # Verify content
        with open(filepath, 'r') as f:
            loaded = json.load(f)
            assert loaded['success'] == True
            assert loaded['game_url'] == 'https://example.com/game'
            
        # Cleanup
        os.remove(filepath)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
