from abc import ABC, abstractmethod
from models import *

class BaseTagManager(ABC):
    @abstractmethod
    def get_messages(self, user_id: int,
                      chat_id: int, tag: Tag) -> List[Message]:
        """Return a list of messages that have the given tag."""
        pass

    @abstractmethod
    def get_messages_multitag(self, user_id: int,
                               chat_id: int, tags: List[Tag],
                                 tag_op: TagOperation) -> List[Message]:
        """Return a list of messages by multiple tags."""
        pass

    @abstractmethod
    def add_tag(self, user_id: int, chat_id: int,
                 tag: Tag, message_id: str) -> None:
        """Add a tag to a specific message."""
        pass

    @abstractmethod
    def add_tags(self, user_id: int, 
                 chat_id: int, tags: List[Tag], message_id: str) -> None:
        """Add a list of tags to a specific message."""
        pass

    @abstractmethod
    def add_tag_to_many(self, user_id: int, chat_id: int, tag: Tag,
                         message_ids: List[str]) -> None:
        """Add a tag to multiple messages."""
        pass

    @abstractmethod
    def add_tags_to_many(self, user_id: int, chat_id: int, 
                         tags: List[Tag], message_ids: List[str]) -> None:
        """Add the same list of tags to multiple messages."""
        pass

    @abstractmethod
    def rename_tag(self, user_id: int, 
                   chat_id: int, old_tag: Tag, new_tag: Tag) -> None:
        """Rename an existing tag."""
        pass

    @abstractmethod
    def reassign_tag(self, user_id: int, chat_id: int, 
                     message_id: str, old_tag: Tag, new_tag: Tag) -> None:
        """Replace a tag on a message with a new one."""
        pass

    @abstractmethod
    def get_tags(self, user_id: int, chat_id: int) -> List[Tag]:
        """Get all tags for a specific chat."""
        pass

    @abstractmethod
    def delete_tag(self, user_id: int, chat_id: int, tag: Tag) -> None:
        """Delete a specific tag."""
        pass

    @abstractmethod
    def get_message_tags(self, user_id: int,
                          chat_id: int, message_id: str) -> List[Tag]:
        """Get all tags associated with a specific message."""
        pass

    @abstractmethod
    def remove_tag_from_message(self, user_id: int,
                                 chat_id: int, tag: Tag, message_id: str) -> None:
        """Remove a specific tag from a specific message."""
        pass

    @abstractmethod
    def delete_message(self, user_id: int,
                                 chat_id: int, message_id: str) -> None:
        """Delete a specific message from a specific chat 
        (with deleting of tags relations and orphan tags )."""
        pass
