"""Execution agent for performing game interactions."""

from typing import Dict, Any, List
from .base_agent import BaseAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException, ElementNotInteractableException
from loguru import logger
import time
import random


class ExecutionAgent(BaseAgent):
    """
    Agent responsible for executing test actions on the game interface.
    Performs clicks, inputs, and other interactions based on strategy.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("ExecutionAgent", config)
        self.max_retries = config.get('max_retries', 3)
        self.action_delay = config.get('action_delay', 0.5)
        self.executed_actions = []
        
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute test actions based on strategy.
        
        Args:
            context: Must contain 'browser', 'strategy', and 'test_sequence'
            
        Returns:
            Dict with execution results
        """
        self.log_action("Starting test execution")
        
        browser = context.get('browser')
        strategy = context.get('strategy', {})
        test_sequence = context.get('test_sequence', [])
        
        if not browser or not browser.driver:
            return {'success': False, 'error': 'Browser not available'}
            
        results = []
        success_count = 0
        
        for i, test_action in enumerate(test_sequence):
            self.log_action(f"Executing action {i+1}/{len(test_sequence)}", test_action)
            
            result = self._execute_action(browser, test_action)
            results.append(result)
            
            if result.get('success'):
                success_count += 1
                
            # Delay between actions
            time.sleep(self.action_delay)
            
        execution_result = {
            'success': True,
            'total_actions': len(test_sequence),
            'successful_actions': success_count,
            'success_rate': success_count / len(test_sequence) if test_sequence else 0,
            'results': results
        }
        
        self.executed_actions.extend(results)
        self.log_action("Execution complete", {
            'success_rate': execution_result['success_rate']
        })
        
        return execution_result
        
    def _execute_action(self, browser, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single action."""
        action_type = action.get('action')
        
        try:
            if action_type == 'click':
                return self._execute_click(browser, action)
            elif action_type == 'input_test':
                return self._execute_input_test(browser, action)
            elif action_type == 'interaction_test':
                return self._execute_interaction_test(browser, action)
            elif action_type == 'verify_state':
                return self._verify_game_state(browser)
            else:
                return {'success': False, 'error': f'Unknown action type: {action_type}'}
                
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            return {'success': False, 'error': str(e)}
            
    def _execute_click(self, browser, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a click action."""
        target = action.get('target', {})
        selector = target.get('selector')
        
        if not selector:
            return {'success': False, 'error': 'No selector provided'}
            
        for attempt in range(self.max_retries):
            try:
                element = self._find_element(browser, selector)
                if element:
                    element.click()
                    return {
                        'success': True,
                        'action': 'click',
                        'selector': selector,
                        'attempt': attempt + 1
                    }
            except ElementNotInteractableException:
                logger.warning(f"Element not interactable: {selector}, attempt {attempt + 1}")
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"Click failed: {e}")
                
        return {'success': False, 'error': 'Click failed after retries'}
        
    def _execute_input_test(self, browser, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute input testing (for forms and text fields)."""
        pattern = action.get('pattern', '')
        
        # Find all input fields
        try:
            inputs = browser.driver.find_elements(By.TAG_NAME, 'input')
            test_values = self._generate_test_values(pattern)
            
            results = []
            for input_elem in inputs[:5]:  # Test first 5 inputs
                try:
                    input_type = input_elem.get_attribute('type')
                    if input_type in ['text', 'number', 'email']:
                        for value in test_values:
                            input_elem.clear()
                            input_elem.send_keys(str(value))
                            time.sleep(0.2)
                            results.append({
                                'input_type': input_type,
                                'value': value,
                                'success': True
                            })
                except Exception as e:
                    logger.debug(f"Input test error: {e}")
                    
            return {
                'success': True,
                'action': 'input_test',
                'tests_performed': len(results),
                'results': results
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    def _execute_interaction_test(self, browser, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute general interaction testing."""
        pattern = action.get('pattern', '')
        
        try:
            if 'button' in pattern:
                buttons = browser.driver.find_elements(By.TAG_NAME, 'button')
                clicked = 0
                for button in buttons[:5]:  # Test first 5 buttons
                    try:
                        if button.is_displayed() and button.is_enabled():
                            button.click()
                            clicked += 1
                            time.sleep(0.3)
                    except:
                        pass
                        
                return {
                    'success': True,
                    'action': 'interaction_test',
                    'pattern': pattern,
                    'interactions': clicked
                }
            elif 'link' in pattern:
                # Test links (but don't navigate away)
                links = browser.driver.find_elements(By.TAG_NAME, 'a')
                return {
                    'success': True,
                    'action': 'interaction_test',
                    'pattern': pattern,
                    'links_found': len(links)
                }
            else:
                return {'success': True, 'action': 'interaction_test', 'pattern': pattern}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    def _verify_game_state(self, browser) -> Dict[str, Any]:
        """Verify the current game state."""
        try:
            # Take a screenshot for verification
            screenshot_path = f"reports/state_verification_{int(time.time())}.png"
            browser.take_screenshot(screenshot_path)
            
            # Check if page is still responsive
            page_title = browser.driver.title
            
            # Look for error indicators
            errors = browser.driver.find_elements(By.XPATH, "//*[contains(text(), 'error') or contains(text(), 'Error')]")
            
            return {
                'success': True,
                'action': 'verify_state',
                'page_title': page_title,
                'errors_found': len(errors),
                'screenshot': screenshot_path
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    def _find_element(self, browser, selector: str):
        """Find an element using the selector."""
        try:
            if selector.startswith('#'):
                return browser.driver.find_element(By.ID, selector[1:])
            elif selector.startswith('.'):
                return browser.driver.find_element(By.CLASS_NAME, selector[1:])
            else:
                return browser.driver.find_element(By.CSS_SELECTOR, selector)
        except:
            return None
            
    def _generate_test_values(self, pattern: str) -> List[Any]:
        """Generate test values based on pattern."""
        if 'math' in pattern or 'number' in pattern:
            return [0, 1, 10, 100, -1, 0.5, 'abc', '']
        elif 'email' in pattern:
            return ['test@example.com', 'invalid', '', 'test@']
        else:
            return ['test', '123', '', 'special!@#']
