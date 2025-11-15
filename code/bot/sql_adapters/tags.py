from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import func
from exceptions import AlreadyExistsException, NotFoundException
from contextlib import contextmanager
from typing import List, Dict, Iterator

from models import Tag, Message, TagOperation
from interfaces.tags import BaseTagManager
from sql_adapters.models import DbTag, DbMessageTag, DbUserChat

class SQLTagManager(BaseTagManager):
    def __init__(self, sess_maker: sessionmaker):
        self.sess_maker = sess_maker
    
    @contextmanager
    def _session_scope(self) -> Iterator[Session]:
        session: Session = self.sess_maker()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def _ensure_user_in_chat(self, user_id: int, chat_id: int,
                              session: Session) -> None:
        if session.get(DbUserChat, (user_id, chat_id)) is None:
            raise NotFoundException(f"Пользователь {user_id} \
                                    не найден в чате {chat_id}")

    def _get_or_create_tag(self, session: Session,
                            chat_id: int, tag: Tag) -> DbTag:
        db_tag = session.query(DbTag).filter_by(
            name=tag.name,
            chat_id=chat_id
        ).first()
        if db_tag is None:
            db_tag = DbTag(name=tag.name, chat_id=chat_id)
            session.add(db_tag)
            session.flush()
        return db_tag

    def _check_tag_not_assigned(self, session: Session, chat_id: int, tag: Tag, message_id: str) -> None:
        existing_message_tag = session.query(DbMessageTag).filter_by(
            message_id=message_id,
            tag_name=tag.name,
            tag_chat_id=chat_id
        ).first()
        if existing_message_tag:
            raise AlreadyExistsException(
                f"Тег {tag.name} в чате {chat_id} уже \
                  присвоен сообщению {message_id}"
            )

    def get_messages(self, user_id: int,
                      chat_id: int, tag: Tag) -> List[Message]:
        """Return a list of messages that have the given tag."""
        with self._session_scope() as session:  
            self._ensure_user_in_chat(user_id, chat_id, session)
            tagged_messages = session.query(DbMessageTag).filter_by(
                tag_name=tag.name,
                tag_chat_id=chat_id
            ).all()
            return [
                Message(
                    message_id=tm.message_id,
                    chat_id=chat_id,
                    tags=[tag]
                ) for tm in tagged_messages
            ]
        
    def get_messages_multitag(self, user_id: int, chat_id: int, tags: List[Tag], 
                             tag_op: TagOperation) -> List[Message]:
        """Return a list of messages by multiple tags."""
        if not tags:
            return []
        with self._session_scope() as session:
            self._ensure_user_in_chat(user_id, chat_id, session)
            tag_names = [tag.name for tag in tags]
            if tag_op == TagOperation.OR:
                # Для OR: сообщения, у которых есть 
                # хотя бы один из указанных тегов
                tagged_messages = (session.query(DbMessageTag)
                        .filter(DbMessageTag.tag_chat_id == chat_id,
                                DbMessageTag.tag_name.in_(tag_names))
                        .distinct().all())
                # Получаем теги для каждого сообщения
                message_tags_map: Dict[str, List[Tag]] = {}
                for tm in tagged_messages:
                    if tm.message_id not in message_tags_map:
                        message_tags_map[tm.message_id] = []
                    message_tags_map[tm.message_id].append(Tag(name=tm.tag_name))
                return [
                    Message(
                        message_id=msg_id,
                        chat_id=chat_id,
                        tags=message_tags
                    ) for msg_id, message_tags in message_tags_map.items()
                ] 
            elif tag_op == TagOperation.AND:
                # Для AND: сообщения, у которых есть все указанные теги
                tagged_messages = (session.query(DbMessageTag)
                        .filter(DbMessageTag.tag_chat_id == chat_id,
                                DbMessageTag.tag_name.in_(tag_names))
                        .group_by(DbMessageTag.message_id)
                        .having(func.count(DbMessageTag.tag_name.distinct()) == len(tags))
                        .all())
                return [
                    Message(
                        message_id=tm.message_id,
                        chat_id=chat_id,
                        tags=tags
                    ) for tm in tagged_messages
                ]

    def add_tag(self, user_id: int, chat_id: int,
                 tag: Tag, message_id: str) -> None:
        """Add a tag to a specific message."""
        with self._session_scope() as session:
            self._ensure_user_in_chat(user_id, chat_id, session)
            
            db_tag = self._get_or_create_tag(session, chat_id, tag)
            self._check_tag_not_assigned(session, chat_id, tag, message_id)
            session.add(DbMessageTag(
                message_id=message_id,
                tag_name=db_tag.name,
                tag_chat_id=chat_id
            ))
    
    def add_tags(self, user_id: int, chat_id: int,
                  tags: List[Tag], message_id: str) -> None:
        """Add a list of tags to a specific message."""
        with self._session_scope() as session:
            self._ensure_user_in_chat(user_id, chat_id, session)
            for tag in tags:
                db_tag = self._get_or_create_tag(session, chat_id, tag)
                self._check_tag_not_assigned(session, chat_id, tag, message_id)
                session.add(DbMessageTag(
                    message_id=message_id,
                    tag_name=db_tag.name,
                    tag_chat_id=chat_id
                ))
    
    def add_tag_to_many(self, user_id: int, chat_id: int, tag: Tag, 
                       message_ids: List[str]) -> None:
        """Add a tag to multiple messages."""
        with self._session_scope() as session:
            self._ensure_user_in_chat(user_id, chat_id, session)
            db_tag = self._get_or_create_tag(session, chat_id, tag)
            for message_id in message_ids:
                self._check_tag_not_assigned(session, chat_id, tag, message_id)
                session.add(DbMessageTag(
                    message_id=message_id,
                    tag_name=db_tag.name,
                    tag_chat_id=chat_id
                ))

    def add_tags_to_many(self, user_id: int, chat_id: int, tags: List[Tag], 
                        message_ids: List[str]) -> None:
        """Add multiple tags to multiple messages."""
        with self._session_scope() as session:
            self._ensure_user_in_chat(user_id, chat_id, session)
            for message_id in message_ids:
                for tag in tags:
                    db_tag = self._get_or_create_tag(session, chat_id, tag)
                    self._check_tag_not_assigned(session, chat_id, tag, message_id)
                    session.add(DbMessageTag(
                        message_id=message_id,
                        tag_name=db_tag.name,
                        tag_chat_id=chat_id
                    ))
    
    def rename_tag(self, user_id: int, chat_id: int,
                    old_tag: Tag, new_tag: Tag) -> None:
        """Rename an existing tag."""
        with self._session_scope() as session:
            self._ensure_user_in_chat(user_id, chat_id, session)
            existing_old_tag = session.query(DbTag).filter_by(
                name=old_tag.name,
                chat_id=chat_id
            ).first()
            if not existing_old_tag:
                raise NotFoundException(f"Старый тег {old_tag.name} \
                                        в чате {chat_id} не найден")
            existing_new_tag = session.query(DbTag).filter_by(
                name=new_tag.name,
                chat_id=chat_id
            ).first()
            if existing_new_tag:
                # Объединяем теги: переносим все сообщения 
                # со старого тега на новый
                old_tag_messages = session.query(DbMessageTag).filter_by(
                    tag_name=existing_old_tag.name,
                    tag_chat_id=chat_id
                ).all()
                for otm in old_tag_messages:
                    # Проверяем, нет ли уже такого тега у сообщения
                    existing_assignment = session.query(DbMessageTag).filter_by(
                        message_id=otm.message_id,
                        tag_name=existing_new_tag.name,
                        tag_chat_id=chat_id
                    ).first()
                    if not existing_assignment:
                        otm.tag_name = existing_new_tag.name
                    else:
                        # Если тег уже есть, удаляем старую запись
                        session.delete(otm)
                # Удаляем старый тег
                session.delete(existing_old_tag)
            else:
                # Просто переименовываем тег
                existing_old_tag.name = new_tag.name

    def reassign_tag(self, user_id: int, chat_id: int, message_id: str, 
                    old_tag: Tag, new_tag: Tag) -> None:
        """Reassign a tag from one to another for a specific message."""
        with self._session_scope() as session:
            self._ensure_user_in_chat(user_id, chat_id, session)
            # Добавляем новый тег
            db_new_tag = self._get_or_create_tag(session, chat_id, new_tag)
            self._check_tag_not_assigned(session, chat_id, new_tag, message_id)
            session.add(DbMessageTag(
                message_id=message_id,
                tag_name=db_new_tag.name,
                tag_chat_id=chat_id
            ))
            # Удаляем старый тег
            old_message_tag = session.query(DbMessageTag).filter_by(
                message_id=message_id,
                tag_name=old_tag.name,
                tag_chat_id=chat_id
            ).first()
            if old_message_tag:
                session.delete(old_message_tag)
                # Проверяем, нужно ли удалять старый тег полностью
                old_tag_usage = session.query(DbMessageTag).filter_by(
                    tag_name=old_tag.name,
                    tag_chat_id=chat_id
                ).count()
                if old_tag_usage == 0:
                    old_db_tag = session.query(DbTag).filter_by(
                        name=old_tag.name,
                        chat_id=chat_id
                    ).first()
                    if old_db_tag:
                        session.delete(old_db_tag)

    def get_tags(self, user_id: int, chat_id: int) -> List[Tag]:
        """Get all tags for a specific chat."""
        with self._session_scope() as session:
            self._ensure_user_in_chat(user_id, chat_id, session)
            db_tags = session.query(DbTag).filter_by(chat_id=chat_id).all()
            return [
                Tag(name=db_tag.name)
                for db_tag in db_tags
            ]

    def delete_tag(self, user_id: int, chat_id: int, tag: Tag) -> None:
        """Delete a specific tag."""
        with self._session_scope() as session:
            self._ensure_user_in_chat(user_id, chat_id, session)
            existing_tag = session.query(DbTag).filter_by(
                name=tag.name,
                chat_id=chat_id
            ).first()
            if not existing_tag:
                raise NotFoundException(f"Тег {tag.name} \
                                        в чате {chat_id} не найден")
            session.delete(existing_tag)

    def get_message_tags(self, user_id: int, chat_id: int, message_id: str) -> List[Tag]:
        """Get all tags associated with a specific message."""
        with self._session_scope() as session:
            self._ensure_user_in_chat(user_id, chat_id, session)
            message_tags = session.query(DbMessageTag).filter_by(
                message_id=message_id,
                tag_chat_id=chat_id
            ).all()
            return [
                Tag(name=mt.tag_name)
                for mt in message_tags
            ]

    def remove_tag_from_message(self, user_id: int, chat_id: int, 
                               tag: Tag, message_id: str) -> None:
        """Remove a specific tag from a specific message."""
        with self._session_scope() as session:
            self._ensure_user_in_chat(user_id, chat_id, session)
            
            message_tag = session.query(DbMessageTag).filter_by(
                message_id=message_id,
                tag_name=tag.name,
                tag_chat_id=chat_id
            ).first()
            if not message_tag:
                raise NotFoundException(f"Тег {tag.name} не присвоен сообщению {message_id}")
            session.delete(message_tag) 
            # Проверяем, нужно ли удалять тег полностью
            tag_usage_count = session.query(DbMessageTag).filter_by(
                tag_name=tag.name, 
                tag_chat_id=chat_id
            ).count()
            if tag_usage_count == 0:
                db_tag = session.query(DbTag).filter_by(
                    name=tag.name,
                    chat_id=chat_id
                ).first()
                if db_tag:
                    session.delete(db_tag)
    
    def delete_message(self, user_id: int,
                                 chat_id: int, message_id: str) -> None:
        """Delete a specific message from a specific chat 
        (with deleting of tags relations and orphan tags )."""
        with self._session_scope() as session:
            # получаем все теги сообщения
            message_tags = session.query(DbMessageTag).filter_by(
                message_id=message_id,
                tag_chat_id=chat_id
            ).all()
            # если у сообщения нет тегов, больше ничего не требуется
            if not message_tags:
                return
            tag_names = [mt.tag_name for mt in message_tags]
            # массовое удаление связей между сообщением и тегами
            (session.query(DbMessageTag)
                    .filter(DbMessageTag.message_id == message_id,
                            DbMessageTag.tag_chat_id == chat_id)
                    .delete(synchronize_session=False))
            # теги которые используются другими сообщениями удалять не нужно, 
            # но остальные нужно
            still_used_tags = (session.query(DbMessageTag.tag_name)
                            .filter(DbMessageTag.tag_name.in_(tag_names),
                                    DbMessageTag.tag_chat_id == chat_id)
                            .distinct()
                            .all())
            used_tag_names = {tag[0] for tag in still_used_tags}
            unused_tag_names = set(tag_names) - used_tag_names
            # массовое удаление неиспользуемых тегов
            if unused_tag_names:
                (session.query(DbTag)
                .filter(DbTag.name.in_(unused_tag_names),
                        DbTag.chat_id == chat_id)
                .delete(synchronize_session=False))