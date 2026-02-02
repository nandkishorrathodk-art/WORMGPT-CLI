from typing import Dict, Optional, TYPE_CHECKING
from .message_bus import MessageBus

if TYPE_CHECKING:
    from .orchestrator import QueenOrchestrator

class QueenRegistry:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(QueenRegistry, cls).__new__(cls)
            cls._instance.queens: Dict[str, 'QueenOrchestrator'] = {}
            cls._instance.message_bus = MessageBus()
        return cls._instance

    def register_queen(self, queen_id: str, queen_instance: 'QueenOrchestrator'):
        if queen_id in self.queens:
            raise ValueError(f"Queen with ID '{queen_id}' already registered.")
        self.queens[queen_id] = queen_instance
        queen_instance.message_bus = self.message_bus

    def get_queen(self, queen_id: str) -> Optional['QueenOrchestrator']:
        return self.queens.get(queen_id)

    def get_all_queens(self) -> Dict[str, 'QueenOrchestrator']:
        return self.queens
