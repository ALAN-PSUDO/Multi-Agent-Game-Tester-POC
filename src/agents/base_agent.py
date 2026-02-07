"""Base agent class for multi-agent system."""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from loguru import logger
from datetime import datetime


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.
    Each agent has a specific responsibility in the game testing process.
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize base agent.
        
        Args:
            name: Agent identifier
            config: Agent configuration
        """
        self.name = name
        self.config = config
        self.enabled = config.get('enabled', True)
        self.state = {}
        self.history = []
        
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent's main task.
        
        Args:
            context: Execution context with relevant data
            
        Returns:
            Dict containing execution results
        """
        pass
        
    def log_action(self, action: str, details: Optional[Dict[str, Any]] = None):
        """Log an action to history."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'agent': self.name,
            'action': action,
            'details': details or {}
        }
        self.history.append(entry)
        logger.info(f"[{self.name}] {action}")
        
    def get_history(self) -> list:
        """Get agent's action history."""
        return self.history
        
    def reset(self):
        """Reset agent state."""
        self.state = {}
        self.history = []
        logger.info(f"[{self.name}] Reset")
