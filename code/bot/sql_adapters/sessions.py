from sqlalchemy.orm import sessionmaker, Session
from exceptions import AlreadyExistsException, NotFoundException
from contextlib import contextmanager
from typing import List

from interfaces.sessions import BaseSessionsManager
from sql_adapters.models import DbUserChat, DbChat, DbSessionMessage


class SQLSessionManager(BaseSessionsManager):
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
    
    def _ensure_user_in_chat(self, user_id: int, chat_id: int,
                              dbsession: Session) -> None:
        if dbsession.get(DbUserChat, (user_id, chat_id)) is None:
            raise NotFoundException(f"Пользователь {user_id} \
                                    не найден в чате {chat_id}")
    
    def update_session(self, user_id: int, 
                      chat_id: int, messages: List[str]) -> None:
        """Adds messages to a session"""
        with self._session_scope() as dbsession:
            existing_chat = dbsession.get(DbChat, chat_id)
            if not existing_chat:
                raise NotFoundException(f"Информация о чате {chat_id} \
                                             не найдена")
            self._ensure_user_in_chat(user_id, chat_id, dbsession)
            for m in messages:
                dbsession.add(DbSessionMessage(message_id=m, chat_id=chat_id))

    def end_session(self, chat_id: int) -> List[str]:
        """Ends session, deletes and returns messages from this session"""
        with self._session_scope() as dbsession:
            message_ids = (dbsession.query(DbSessionMessage.message_id)
                    .filter(DbSessionMessage.chat_id == chat_id)
                    .all())
            ans = [mid[0] for mid in message_ids]
            (dbsession.query(DbSessionMessage)
                .filter(DbSessionMessage.chat_id == chat_id)
                .delete())
            return ans