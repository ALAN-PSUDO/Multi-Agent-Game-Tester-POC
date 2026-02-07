"""Main orchestrator for the multi-agent game testing system."""

from typing import Dict, Any, Optional
import yaml
import time
from pathlib import Path
from loguru import logger
import sys

from src.core.browser_automation import BrowserAutomation
from src.core.dom_analyzer import DOMAnalyzer
from src.core.heuristic_learning import HeuristicLearning
from src.agents.exploration_agent import ExplorationAgent
from src.agents.strategy_agent import StrategyAgent
from src.agents.execution_agent import ExecutionAgent
from src.agents.validation_agent import ValidationAgent
from src.utils.reporting import ReportGenerator


class GameTesterOrchestrator:
    """
    Main orchestrator that coordinates all agents and manages the
    game testing workflow.
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the orchestrator.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self._setup_logging()
        
        # Initialize components
        self.browser = None
        self.dom_analyzer = None
        self.heuristic_learning = None
        
        # Initialize agents
        self.exploration_agent = None
        self.strategy_agent = None
        self.execution_agent = None
        self.validation_agent = None
        
        self._initialize_components()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            # Return default config
            return {
                'browser': {'type': 'chrome', 'headless': False},
                'agents': {},
                'game_testing': {},
                'heuristics': {'enabled': True}
            }
            
    def _setup_logging(self):
        """Setup logging configuration."""
        log_config = self.config.get('logging', {})
        log_level = log_config.get('level', 'INFO')
        log_file = log_config.get('file', 'game_tester.log')
        console = log_config.get('console', True)
        
        # Remove default logger
        logger.remove()
        
        # Add console logger
        if console:
            logger.add(sys.stderr, level=log_level)
            
        # Add file logger
        if log_file:
            logger.add(log_file, level=log_level, rotation="10 MB")
            
    def _initialize_components(self):
        """Initialize all components and agents."""
        logger.info("Initializing components...")
        
        # Initialize core components
        self.browser = BrowserAutomation(self.config.get('browser', {}))
        self.dom_analyzer = DOMAnalyzer(self.config.get('dom_analysis', {}))
        self.heuristic_learning = HeuristicLearning(self.config.get('heuristics', {}))
        
        # Initialize agents
        agents_config = self.config.get('agents', {})
        self.exploration_agent = ExplorationAgent(agents_config.get('exploration', {}))
        self.strategy_agent = StrategyAgent(agents_config.get('strategy', {}))
        self.execution_agent = ExecutionAgent(agents_config.get('execution', {}))
        self.validation_agent = ValidationAgent(agents_config.get('validation', {}))
        
        logger.info("All components initialized")
        
    def test_game(self, game_url: str) -> Dict[str, Any]:
        """
        Test a game at the specified URL.
        
        Args:
            game_url: URL of the game to test
            
        Returns:
            Dict with comprehensive test results
        """
        logger.info(f"Starting game test for: {game_url}")
        start_time = time.time()
        
        try:
            # Initialize browser
            if not self.browser.initialize():
                return {'success': False, 'error': 'Browser initialization failed'}
                
            # Navigate to game
            if not self.browser.navigate_to(game_url):
                return {'success': False, 'error': 'Navigation failed'}
                
            # Wait for page to load
            time.sleep(3)
            
            # Phase 1: Exploration
            logger.info("=== Phase 1: Exploration ===")
            exploration_results = self._exploration_phase()
            
            # Phase 2: Strategy Generation
            logger.info("=== Phase 2: Strategy Generation ===")
            strategy_results = self._strategy_phase(exploration_results)
            
            # Phase 3: Execution
            logger.info("=== Phase 3: Execution ===")
            execution_results = self._execution_phase(strategy_results)
            
            # Phase 4: Validation
            logger.info("=== Phase 4: Validation ===")
            validation_results = self._validation_phase(execution_results, exploration_results)
            
            # Phase 5: Learning
            logger.info("=== Phase 5: Learning ===")
            learning_results = self._learning_phase(execution_results, validation_results)
            
            # Update game profile
            self._update_profile(game_url, {
                'timestamp': time.time(),
                'game_type': exploration_results.get('game_type'),
                'success_rate': execution_results.get('success_rate'),
                'strategy': strategy_results.get('strategy'),
                'characteristics': exploration_results.get('interface_map')
            })
            
            # Generate report
            elapsed_time = time.time() - start_time
            report = self._generate_report(
                game_url,
                exploration_results,
                strategy_results,
                execution_results,
                validation_results,
                learning_results,
                elapsed_time
            )
            
            logger.info(f"Game test completed in {elapsed_time:.2f}s")
            return report
            
        except Exception as e:
            logger.error(f"Test failed with error: {e}")
            return {
                'success': False,
                'error': str(e),
                'game_url': game_url
            }
            
        finally:
            # Cleanup
            if self.browser:
                self.browser.close()
                
    def _exploration_phase(self) -> Dict[str, Any]:
        """Execute exploration phase."""
        # Get page source and analyze DOM
        page_source = self.browser.get_page_source()
        dom_analysis = self.dom_analyzer.analyze_page(page_source, self.browser.driver)
        
        # Run exploration agent
        context = {
            'dom_analysis': dom_analysis,
            'browser': self.browser
        }
        
        exploration_results = self.exploration_agent.execute(context)
        return exploration_results
        
    def _strategy_phase(self, exploration_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute strategy generation phase."""
        # Get recommendations from heuristic learning
        game_type = exploration_results.get('game_type', 'unknown')
        recommendations = self.heuristic_learning.get_recommendations(game_type, exploration_results)
        
        # Run strategy agent
        context = {
            'exploration_results': exploration_results,
            'recommendations': recommendations
        }
        
        strategy_results = self.strategy_agent.execute(context)
        return strategy_results
        
    def _execution_phase(self, strategy_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute testing actions phase."""
        context = {
            'browser': self.browser,
            'strategy': strategy_results.get('strategy'),
            'test_sequence': strategy_results.get('test_sequence', [])
        }
        
        execution_results = self.execution_agent.execute(context)
        return execution_results
        
    def _validation_phase(self, execution_results: Dict[str, Any], exploration_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute validation phase."""
        context = {
            'execution_results': execution_results,
            'browser': self.browser,
            'exploration_results': exploration_results
        }
        
        validation_results = self.validation_agent.execute(context)
        return validation_results
        
    def _learning_phase(self, execution_results: Dict[str, Any], validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute learning phase."""
        learning_results = self.heuristic_learning.learn_from_execution(
            execution_results,
            validation_results
        )
        
        # Adapt strategy based on feedback if needed
        self.strategy_agent.adapt_strategy({
            'success_rate': execution_results.get('success_rate', 0)
        })
        
        return learning_results
        
    def _update_profile(self, game_url: str, game_data: Dict[str, Any]):
        """Update game profile in heuristic learning."""
        self.heuristic_learning.update_game_profile(game_url, game_data)
        
    def _generate_report(self, game_url: str, exploration: Dict, strategy: Dict,
                        execution: Dict, validation: Dict, learning: Dict,
                        elapsed_time: float) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        report = {
            'success': True,
            'game_url': game_url,
            'elapsed_time': elapsed_time,
            'timestamp': time.time(),
            'phases': {
                'exploration': {
                    'game_type': exploration.get('game_type'),
                    'elements_discovered': exploration.get('discovered_elements'),
                    'game_controls': len(exploration.get('game_controls', []))
                },
                'strategy': {
                    'strategy_type': strategy.get('strategy', {}).get('type'),
                    'test_sequence_length': len(strategy.get('test_sequence', []))
                },
                'execution': {
                    'total_actions': execution.get('total_actions'),
                    'successful_actions': execution.get('successful_actions'),
                    'success_rate': execution.get('success_rate')
                },
                'validation': {
                    'health_score': validation.get('overall_health'),
                    'anomalies': len(validation.get('anomalies', []))
                },
                'learning': {
                    'patterns_learned': learning.get('patterns_learned', 0),
                    'total_patterns': learning.get('total_patterns', 0)
                }
            },
            'summary': {
                'overall_success_rate': execution.get('success_rate', 0),
                'health_score': validation.get('overall_health', 0),
                'game_type': exploration.get('game_type'),
                'recommendation': self._get_recommendation(validation)
            }
        }
        
        return report
        
    def _get_recommendation(self, validation: Dict[str, Any]) -> str:
        """Get recommendation based on validation results."""
        health_score = validation.get('overall_health', 0)
        
        if health_score >= 80:
            return "Game is functioning well. All tests passed successfully."
        elif health_score >= 60:
            return "Game is generally functional with minor issues detected."
        elif health_score >= 40:
            return "Game has moderate issues that should be investigated."
        else:
            return "Game has significant issues requiring immediate attention."
            
    def batch_test(self, game_urls: list) -> list:
        """
        Test multiple games in batch.
        
        Args:
            game_urls: List of game URLs to test
            
        Returns:
            List of test reports
        """
        reports = []
        
        for i, url in enumerate(game_urls):
            logger.info(f"Testing game {i+1}/{len(game_urls)}: {url}")
            report = self.test_game(url)
            reports.append(report)
            
            # Brief pause between tests
            time.sleep(2)
            
        return reports
