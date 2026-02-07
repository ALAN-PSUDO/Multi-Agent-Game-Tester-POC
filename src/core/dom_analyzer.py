"""DOM analysis module for dynamic page understanding."""

from typing import List, Dict, Any, Optional, Set
from bs4 import BeautifulSoup
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from loguru import logger
import re


class DOMAnalyzer:
    """
    Analyzes DOM structure to identify interactive elements and game components.
    Uses heuristics to understand page structure dynamically.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize DOM analyzer.
        
        Args:
            config: DOM analysis configuration
        """
        self.config = config
        self.interactive_tags = config.get('interactive_elements', [])
        self.ignore_tags = config.get('ignore_elements', [])
        self.attribute_priority = config.get('attribute_priority', [])
        
    def analyze_page(self, html_source: str, driver=None) -> Dict[str, Any]:
        """
        Analyze page structure and identify key elements.
        
        Args:
            html_source: HTML source of the page
            driver: Optional Selenium WebDriver for live element access
            
        Returns:
            Dict containing analysis results
        """
        soup = BeautifulSoup(html_source, 'lxml')
        
        analysis = {
            'interactive_elements': self._find_interactive_elements(soup, driver),
            'page_structure': self._analyze_structure(soup),
            'game_indicators': self._detect_game_indicators(soup),
            'forms': self._find_forms(soup),
            'canvas_elements': self._find_canvas_elements(soup, driver),
        }
        
        logger.info(f"DOM Analysis complete: {len(analysis['interactive_elements'])} interactive elements found")
        return analysis
        
    def _find_interactive_elements(self, soup: BeautifulSoup, driver=None) -> List[Dict[str, Any]]:
        """Find all interactive elements on the page."""
        elements = []
        
        for tag in self.interactive_tags:
            found = soup.find_all(tag)
            for elem in found:
                element_info = self._extract_element_info(elem)
                if element_info and self._is_visible_element(element_info):
                    elements.append(element_info)
                    
        # If driver is available, enrich with live element data
        if driver:
            elements = self._enrich_with_selenium_data(elements, driver)
            
        return elements
        
    def _extract_element_info(self, element) -> Optional[Dict[str, Any]]:
        """Extract relevant information from a BeautifulSoup element."""
        try:
            info = {
                'tag': element.name,
                'text': element.get_text(strip=True)[:100],  # Limit text length
                'attributes': {},
                'selector': None,
            }
            
            # Extract key attributes based on priority
            for attr in self.attribute_priority:
                if element.has_attr(attr):
                    info['attributes'][attr] = element[attr]
                    
            # Build CSS selector
            info['selector'] = self._build_selector(element)
            
            # Extract other relevant attributes
            if element.has_attr('type'):
                info['type'] = element['type']
            if element.has_attr('value'):
                info['value'] = element['value']
            if element.has_attr('href'):
                info['href'] = element['href']
                
            return info
        except Exception as e:
            logger.debug(f"Error extracting element info: {e}")
            return None
            
    def _build_selector(self, element) -> str:
        """Build a CSS selector for an element."""
        # Prioritize ID selector
        if element.has_attr('id') and element['id']:
            return f"#{element['id']}"
            
        # Use class selector
        if element.has_attr('class') and element['class']:
            classes = '.'.join(element['class'][:2])  # Use first 2 classes
            return f"{element.name}.{classes}"
            
        # Use name attribute
        if element.has_attr('name'):
            return f"{element.name}[name='{element['name']}']"
            
        # Fallback to tag name
        return element.name
        
    def _is_visible_element(self, element_info: Dict[str, Any]) -> bool:
        """Heuristic to determine if element is likely visible."""
        # Skip elements with display:none or visibility:hidden in style
        style = element_info['attributes'].get('style', '')
        if 'display:none' in style.replace(' ', '') or 'visibility:hidden' in style.replace(' ', ''):
            return False
            
        # Skip hidden inputs
        if element_info.get('type') == 'hidden':
            return False
            
        return True
        
    def _analyze_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze overall page structure."""
        structure = {
            'title': soup.title.string if soup.title else "Unknown",
            'has_canvas': len(soup.find_all('canvas')) > 0,
            'has_forms': len(soup.find_all('form')) > 0,
            'script_count': len(soup.find_all('script')),
            'total_elements': len(soup.find_all()),
        }
        return structure
        
    def _detect_game_indicators(self, soup: BeautifulSoup) -> List[str]:
        """Detect indicators that suggest this is a game page."""
        indicators = []
        
        # Check for game-related keywords
        game_keywords = ['game', 'score', 'level', 'play', 'player', 'puzzle', 'math']
        text_content = soup.get_text().lower()
        
        for keyword in game_keywords:
            if keyword in text_content:
                indicators.append(f"keyword:{keyword}")
                
        # Check for canvas (common in HTML5 games)
        if soup.find_all('canvas'):
            indicators.append("canvas_detected")
            
        # Check for game-related class/id names
        all_attrs = []
        for elem in soup.find_all():
            if elem.has_attr('class'):
                all_attrs.extend(elem['class'])
            if elem.has_attr('id'):
                all_attrs.append(elem['id'])
                
        game_patterns = ['game', 'score', 'level', 'board', 'puzzle']
        for attr in all_attrs:
            attr_lower = str(attr).lower()
            for pattern in game_patterns:
                if pattern in attr_lower:
                    indicators.append(f"attribute:{pattern}")
                    break
                    
        return list(set(indicators))  # Remove duplicates
        
    def _find_forms(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Find and analyze forms on the page."""
        forms = []
        for form in soup.find_all('form'):
            form_info = {
                'action': form.get('action', ''),
                'method': form.get('method', 'get'),
                'inputs': []
            }
            
            for input_elem in form.find_all(['input', 'select', 'textarea']):
                form_info['inputs'].append({
                    'type': input_elem.get('type', 'text'),
                    'name': input_elem.get('name', ''),
                    'id': input_elem.get('id', ''),
                })
                
            forms.append(form_info)
            
        return forms
        
    def _find_canvas_elements(self, soup: BeautifulSoup, driver=None) -> List[Dict[str, Any]]:
        """Find and analyze canvas elements (common in games)."""
        canvas_elements = []
        
        for canvas in soup.find_all('canvas'):
            canvas_info = {
                'id': canvas.get('id', ''),
                'class': canvas.get('class', []),
                'width': canvas.get('width', 'auto'),
                'height': canvas.get('height', 'auto'),
            }
            
            # If driver available, get computed dimensions
            if driver and canvas.get('id'):
                try:
                    elem = driver.find_element(By.ID, canvas['id'])
                    canvas_info['actual_size'] = elem.size
                except:
                    pass
                    
            canvas_elements.append(canvas_info)
            
        return canvas_elements
        
    def _enrich_with_selenium_data(self, elements: List[Dict[str, Any]], driver) -> List[Dict[str, Any]]:
        """Enrich element data with live information from Selenium."""
        enriched = []
        
        for elem_info in elements:
            try:
                selector = elem_info.get('selector')
                if selector:
                    # Try to find element using Selenium
                    web_element = None
                    if selector.startswith('#'):
                        web_element = driver.find_element(By.ID, selector[1:])
                    else:
                        web_element = driver.find_element(By.CSS_SELECTOR, selector)
                        
                    if web_element:
                        elem_info['is_displayed'] = web_element.is_displayed()
                        elem_info['is_enabled'] = web_element.is_enabled()
                        elem_info['location'] = web_element.location
                        elem_info['size'] = web_element.size
                        
            except Exception as e:
                logger.debug(f"Could not enrich element: {e}")
                
            enriched.append(elem_info)
            
        return enriched
        
    def find_clickable_elements(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract clickable elements from analysis.
        
        Args:
            analysis: Result from analyze_page()
            
        Returns:
            List of clickable elements
        """
        clickable = []
        clickable_tags = ['button', 'a', 'input']
        
        for elem in analysis.get('interactive_elements', []):
            if elem['tag'] in clickable_tags:
                if elem.get('is_displayed', True) and elem.get('is_enabled', True):
                    clickable.append(elem)
                    
        return clickable
