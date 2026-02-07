"""Core browser automation module for 32-bit Windows compatibility."""

from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from loguru import logger
import platform


class BrowserAutomation:
    """
    Browser automation wrapper optimized for 32-bit Windows environments.
    Handles WebDriver initialization, page navigation, and basic interactions.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize browser automation with configuration.
        
        Args:
            config: Browser configuration dictionary
        """
        self.config = config
        self.driver: Optional[webdriver.Chrome] = None
        self._is_32bit = self._check_architecture()
        
    def _check_architecture(self) -> bool:
        """Check if running on 32-bit architecture."""
        arch = platform.architecture()[0]
        is_32bit = arch == "32bit"
        logger.info(f"System architecture: {arch} (32-bit: {is_32bit})")
        return is_32bit
        
    def initialize(self) -> bool:
        """
        Initialize the WebDriver with 32-bit compatible settings.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            chrome_options = Options()
            
            # Configure for 32-bit compatibility
            if self._is_32bit:
                logger.info("Configuring for 32-bit Windows environment")
                # Disable GPU acceleration for better 32-bit compatibility
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
            
            # Headless mode
            if self.config.get('headless', False):
                chrome_options.add_argument('--headless')
                
            # Window size
            window_size = self.config.get('window_size', '1280x720')
            chrome_options.add_argument(f'--window-size={window_size}')
            
            # Disable unnecessary features for efficiency
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-notifications')
            
            # Initialize driver
            driver_path = self.config.get('driver_path')
            if driver_path:
                service = Service(driver_path)
            else:
                # Auto-detect and download appropriate driver
                logger.info("Auto-detecting ChromeDriver...")
                service = Service(ChromeDriverManager().install())
                
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Set timeouts
            self.driver.implicitly_wait(self.config.get('implicit_wait', 10))
            self.driver.set_page_load_timeout(self.config.get('page_load_timeout', 30))
            
            logger.info("Browser automation initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            return False
            
    def navigate_to(self, url: str) -> bool:
        """
        Navigate to a URL.
        
        Args:
            url: Target URL
            
        Returns:
            bool: True if navigation successful
        """
        if not self.driver:
            logger.error("Driver not initialized")
            return False
            
        try:
            logger.info(f"Navigating to: {url}")
            self.driver.get(url)
            return True
        except TimeoutException:
            logger.error(f"Timeout loading URL: {url}")
            return False
        except WebDriverException as e:
            logger.error(f"Navigation error: {e}")
            return False
            
    def wait_for_element(self, by: By, value: str, timeout: int = 10):
        """
        Wait for an element to be present.
        
        Args:
            by: Selenium By locator strategy
            value: Locator value
            timeout: Maximum wait time in seconds
            
        Returns:
            WebElement or None
        """
        if not self.driver:
            return None
            
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logger.warning(f"Element not found: {by}={value}")
            return None
            
    def get_page_source(self) -> Optional[str]:
        """Get current page HTML source."""
        if self.driver:
            return self.driver.page_source
        return None
        
    def execute_script(self, script: str, *args):
        """Execute JavaScript in the browser context."""
        if self.driver:
            return self.driver.execute_script(script, *args)
        return None
        
    def take_screenshot(self, filepath: str) -> bool:
        """
        Take a screenshot of the current page.
        
        Args:
            filepath: Path to save screenshot
            
        Returns:
            bool: True if successful
        """
        if not self.driver:
            return False
            
        try:
            self.driver.save_screenshot(filepath)
            logger.info(f"Screenshot saved: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return False
            
    def close(self):
        """Close the browser and cleanup."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser closed successfully")
            except Exception as e:
                logger.error(f"Error closing browser: {e}")
            finally:
                self.driver = None
                
    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
