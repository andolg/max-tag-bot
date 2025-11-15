from sqlalchemy.orm import sessionmaker, Session
from exceptions import AlreadyExistsException, NotFoundException
from contextlib import contextmanager
from typing import List, Optional

from models import Chat
from interfaces.chats import BaseChatManager
from sql_adapters.models import DbUserChat, DbChat


class SQLChatManager(BaseChatManager):
    def __init__(self, sess_maker: sessionmaker):
        self.sess_maker = sess_maker

    @contextmanager
    def _session_scope(self):
        _session: Session = self.sess_maker()
        try:
            yield _session
            _session.commit()
        except Exception:
            _session.rollback()
            raise
        finally:
            _session.close()
    
    def add_chat(self, chat_id: int, name: str) -> None:
        """Add information about chat."""
        with self._session_scope() as session:
            existing_chat = session.get(DbChat, chat_id)
            if existing_chat:
                raise AlreadyExistsException(f"Информация о чате {chat_id} \
                                             уже существует")
            new_chat = DbChat(
                    id=chat_id,
                    name=name,
                    )
            session.add(new_chat)
    
    def remove_chat(self, chat_id: int) -> None:
        """Removes all information about chat
          including links between chat and tags etc."""
        with self._session_scope() as session:
            existing_chat = session.get(DbChat, chat_id)
            if not existing_chat:
                raise NotFoundException(f"Информация о чате {chat_id} \
                                        не найдена")
            session.delete(existing_chat)
    
    def remember_user(self, user_id: int, chat_id: int,
                       is_main: bool = True) -> None:
        """Associate a user with a chat."""
        with self._session_scope() as session:
            existing_chat = session.get(DbChat, chat_id)
            if not existing_chat:
                raise NotFoundException(f"Информация о чате \
                                        {chat_id} не найдена")
            existing_userchat = session.get(DbUserChat, (user_id, chat_id))
            if existing_userchat:
                raise AlreadyExistsException(f"Связь пользователя" \
                " {user_id} и чата {chat_id} уже существует")
            else:
                new_association = DbUserChat(
                    user_id=user_id,
                    chat_id=chat_id,
                    is_main=is_main
                )
                session.add(new_association)
    
    def forget_user(self, user_id: int, chat_id: int) -> None:
        """Disassociate a user from a chat."""
        with self._session_scope() as session:
            association = session.get(DbUserChat, (user_id, chat_id))
            
            if association is not None:
                session.delete(association)
            else:
                raise NotFoundException(f"Связь пользователя" \
                " {user_id} и чата {chat_id} не найдена в хранилище")
    
    def get_user_chats(self, user_id: int) -> List[Chat]:
        """Get all chats associated with a user."""
        with self._session_scope() as session:
            user_chats = session.query(DbUserChat).filter_by(
                user_id=user_id
            ).all()
            if not user_chats:
                raise NotFoundException(f"Не найдены записи о чатах \
                                        пользователя {user_id}")
            # должно вроде работать через навигационные свойства
            return [Chat(name=c.chat.name, id=c.chat.id) for c in user_chats]
    
    def get_chat_users(self, chat_id: int) -> List[int]:
        """Get all users associated with a chat."""
        with self._session_scope() as session:
            existing_chat = session.get(DbChat, chat_id)
            if not existing_chat:
                raise NotFoundException(f"Информация о чате \
                                        {chat_id} не найдена")
            associations = session.query(DbUserChat).filter_by(
                chat_id=chat_id
            ).all()
            if not associations:
                raise NotFoundException(f"Не найдены записи " \
                "о пользователях чата {chat_id}")
            return [assoc.user_id for assoc in associations]
    
    def get_chat(self, chat_id: int) -> Chat:
        with self._session_scope() as session:
            chat = session.get(DbChat, chat_id)
            if not chat:
                raise NotFoundException(f"Информация о чате {chat_id} не найдена")
            return chat

    def get_main_chat(self, user_id: int) -> Optional[Chat]:
        """Get the main chat associated with a user."""
        with self._session_scope() as session:
            association = session.query(DbUserChat).filter_by(
                user_id=user_id,
                is_main=True
            ).first()
            return association.chat_id if association else None
    
    def get_ext_chats(self, user_id: int) -> List[Chat]:
        """Get the non-main chats associated with a user."""
        with self._session_scope() as session:
            user_chats = session.query(DbUserChat).filter_by(
                user_id=user_id,
                is_main=False
            ).all()
            if not user_chats:
                raise NotFoundException(f"Не найдены записи о чатах \
                                        пользователя {user_id}")
            return [Chat(name=c.chat.name, id=c.chat.id) for c in user_chats]
        
    def is_user_in_chat(self, user_id: int, chat_id: int) -> bool:
        """Check if a user is associated with a chat."""
        with self._session_scope() as session:
            user_in_chat = session.get(DbUserChat, (user_id, chat_id))
            return user_in_chat is not None
