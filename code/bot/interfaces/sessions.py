from abc import ABC, abstractmethod
from models import *

class BaseSessionsManager(ABC):
    @abstractmethod
    def update_session(self, chat_id: int, messages: List[str]) -> None:
        """Adds messages to a session"""
        pass

    @abstractmethod
    def end_session(self, chat_id: int) -> List[str]:
        """Ends session, deletes and returns messages from this session"""
        pass
