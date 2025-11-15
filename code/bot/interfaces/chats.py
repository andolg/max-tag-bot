from abc import ABC, abstractmethod
from models import *

class BaseChatManager(ABC):
    @abstractmethod
    def add_chat(self, chat_id: int, name: str) -> None:
        """Add information about chat."""
        pass

    # тут удалил параметр name, тк не используется
    @abstractmethod
    def remove_chat(self, chat_id: int) -> None:
        """Removes all information about chat
          including links between chat and tags etc."""
        pass

    @abstractmethod
    def remember_user(self, user_id: int, chat_id: int, is_main = True) -> None:
        """Associate a user with a chat."""
        pass

    @abstractmethod
    def forget_user(self, user_id: int, chat_id: int) -> None:
        """Disassociate a user from a chat."""
        pass

    @abstractmethod
    def get_user_chats(self, user_id: int) -> List[Chat]:
        """Get all chats associated with a user."""
        pass

    @abstractmethod
    def get_chat_users(self, chat_id: int) -> List[int]:
        """Get all users associated with a chat."""
        pass
    
    def get_chat(self, chat_id: int) -> Chat:
        """Get chat by its id."""
        pass

    @abstractmethod
    def get_main_chat(self, user_id: int) -> Optional[Chat]:
        """Get the main chat associated with a user."""
        pass

    @abstractmethod
    def get_ext_chats(self, user_id: int) -> List[Chat]:
        """Get the non-main chats associated with a user."""
        pass

    @abstractmethod
    def is_user_in_chat(self, user_id: int, chat_id: int) -> bool:
        """Check if a user is associated with a chat."""
        pass