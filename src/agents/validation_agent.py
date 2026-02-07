"""Validation agent for verifying game behavior."""

from typing import Dict, Any, List
from .base_agent import BaseAgent
from loguru import logger
import time


class ValidationAgent(BaseAgent):
    """
    Agent responsible for validating game behavior and detecting issues.
    Analyzes execution results and verifies expected outcomes.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("ValidationAgent", config)
        self.screenshot_on_error = config.get('screenshot_on_error', True)
        self.log_level = config.get('log_level', 'INFO')
        self.validation_results = []
        
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate execution results and game behavior.
        
        Args:
            context: Must contain 'execution_results', 'browser', 'exploration_results'
            
        Returns:
            Dict with validation results
        """
        self.log_action("Starting validation")
        
        execution_results = context.get('execution_results', {})
        browser = context.get('browser')
        exploration_results = context.get('exploration_results', {})
        
        # Validate execution success
        execution_validation = self._validate_execution(execution_results)
        
        # Validate page state
        state_validation = self._validate_page_state(browser, exploration_results)
        
        # Detect anomalies
        anomalies = self._detect_anomalies(execution_results, browser)
        
        # Generate validation report
        validation_report = {
            'success': True,
            'timestamp': time.time(),
            'execution_validation': execution_validation,
            'state_validation': state_validation,
            'anomalies': anomalies,
            'overall_health': self._calculate_health_score(execution_validation, state_validation, anomalies)
        }
        
        self.validation_results.append(validation_report)
        self.log_action("Validation complete", {
            'health_score': validation_report['overall_health']
        })
        
        return validation_report
        
    def _validate_execution(self, execution_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate execution results."""
        total_actions = execution_results.get('total_actions', 0)
        successful_actions = execution_results.get('successful_actions', 0)
        success_rate = execution_results.get('success_rate', 0)
        
        validation = {
            'passed': success_rate > 0.5,  # At least 50% success rate
            'success_rate': success_rate,
            'total_actions': total_actions,
            'successful_actions': successful_actions,
            'failed_actions': total_actions - successful_actions,
        }
        
        # Analyze failure patterns
        results = execution_results.get('results', [])
        failure_reasons = {}
        
        for result in results:
            if not result.get('success'):
                error = result.get('error', 'unknown')
                failure_reasons[error] = failure_reasons.get(error, 0) + 1
                
        validation['failure_patterns'] = failure_reasons
        
        return validation
        
    def _validate_page_state(self, browser, exploration_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate current page state."""
        if not browser or not browser.driver:
            return {'passed': False, 'error': 'Browser not available'}
            
        try:
            # Check if page is responsive
            page_title = browser.driver.title
            current_url = browser.driver.current_url
            
            # Check for JavaScript errors (if possible)
            js_errors = []
            try:
                logs = browser.driver.get_log('browser')
                js_errors = [log for log in logs if log['level'] == 'SEVERE']
            except:
                pass  # Not all browsers support this
                
            # Check if key elements still exist
            game_type = exploration_results.get('game_type', 'unknown')
            elements_intact = self._verify_elements_intact(browser, exploration_results)
            
            validation = {
                'passed': len(js_errors) == 0 and elements_intact,
                'page_title': page_title,
                'current_url': current_url,
                'js_errors': len(js_errors),
                'elements_intact': elements_intact,
                'game_type': game_type
            }
            
            return validation
            
        except Exception as e:
            logger.error(f"Page state validation error: {e}")
            return {'passed': False, 'error': str(e)}
            
    def _verify_elements_intact(self, browser, exploration_results: Dict[str, Any]) -> bool:
        """Verify that key game elements are still present."""
        try:
            categorized = exploration_results.get('categorized_elements', {})
            
            # Check if main element categories still exist
            buttons = browser.driver.find_elements(browser.driver.__class__.By.TAG_NAME, 'button')
            inputs = browser.driver.find_elements(browser.driver.__class__.By.TAG_NAME, 'input')
            
            original_buttons = len(categorized.get('buttons', []))
            original_inputs = len(categorized.get('inputs', []))
            
            # Allow some variance (80% threshold)
            buttons_ok = len(buttons) >= original_buttons * 0.8
            inputs_ok = len(inputs) >= original_inputs * 0.8
            
            return buttons_ok and inputs_ok
            
        except Exception as e:
            logger.debug(f"Element verification error: {e}")
            return False
            
    def _detect_anomalies(self, execution_results: Dict[str, Any], browser) -> List[Dict[str, Any]]:
        """Detect anomalies in execution or page state."""
        anomalies = []
        
        # Check for unusually high failure rate
        success_rate = execution_results.get('success_rate', 1.0)
        if success_rate < 0.3:
            anomalies.append({
                'type': 'high_failure_rate',
                'severity': 'high',
                'message': f'Success rate is very low: {success_rate:.2%}',
                'value': success_rate
            })
            
        # Check for repeated errors
        results = execution_results.get('results', [])
        error_counts = {}
        for result in results:
            if not result.get('success'):
                error = result.get('error', 'unknown')
                error_counts[error] = error_counts.get(error, 0) + 1
                
        for error, count in error_counts.items():
            if count > 3:
                anomalies.append({
                    'type': 'repeated_error',
                    'severity': 'medium',
                    'message': f'Error repeated {count} times: {error}',
                    'error': error,
                    'count': count
                })
                
        # Check for timeout issues
        if browser and browser.driver:
            try:
                # Check page load time (basic check)
                start = time.time()
                browser.driver.title  # Simple operation to check responsiveness
                elapsed = time.time() - start
                
                if elapsed > 5:
                    anomalies.append({
                        'type': 'slow_response',
                        'severity': 'low',
                        'message': f'Page response is slow: {elapsed:.2f}s',
                        'value': elapsed
                    })
            except Exception as e:
                anomalies.append({
                    'type': 'browser_error',
                    'severity': 'high',
                    'message': f'Browser error: {str(e)}',
                    'error': str(e)
                })
                
        return anomalies
        
    def _calculate_health_score(self, execution_validation: Dict, state_validation: Dict, anomalies: List) -> float:
        """Calculate overall health score (0-100)."""
        score = 100.0
        
        # Deduct for execution failures
        success_rate = execution_validation.get('success_rate', 0)
        score -= (1 - success_rate) * 40  # Max 40 points deduction
        
        # Deduct for state validation failures
        if not state_validation.get('passed', False):
            score -= 20
            
        # Deduct for anomalies
        for anomaly in anomalies:
            severity = anomaly.get('severity', 'low')
            if severity == 'high':
                score -= 15
            elif severity == 'medium':
                score -= 10
            else:
                score -= 5
                
        return max(0, min(100, score))
        
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report."""
        if not self.validation_results:
            return {'error': 'No validation results available'}
            
        latest = self.validation_results[-1]
        
        report = {
            'summary': {
                'total_validations': len(self.validation_results),
                'latest_health_score': latest['overall_health'],
                'timestamp': latest['timestamp']
            },
            'latest_validation': latest,
            'historical_scores': [v['overall_health'] for v in self.validation_results],
            'trend': self._calculate_trend()
        }
        
        return report
        
    def _calculate_trend(self) -> str:
        """Calculate trend in health scores."""
        if len(self.validation_results) < 2:
            return 'insufficient_data'
            
        scores = [v['overall_health'] for v in self.validation_results[-5:]]
        
        if len(scores) < 2:
            return 'stable'
            
        avg_first_half = sum(scores[:len(scores)//2]) / (len(scores)//2)
        avg_second_half = sum(scores[len(scores)//2:]) / (len(scores) - len(scores)//2)
        
        diff = avg_second_half - avg_first_half
        
        if diff > 5:
            return 'improving'
        elif diff < -5:
            return 'degrading'
        else:
            return 'stable'
