from __future__ import annotations
from sqlalchemy import Column, BigInteger, String, Boolean, ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column, declarative_base
from typing import List

Base = declarative_base()


class DbChat(Base):
    __tablename__ = 'chat'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    relationships: Mapped[List[DbUserChat]] = relationship(
        "DbUserChat",
        back_populates="chat",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    tags: Mapped[List[DbTag]] = relationship(
        "DbTag",
        back_populates="chat",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    session_messages: Mapped[List[DbSessionMessage]] = relationship(
        "DbSessionMessage",
        back_populates="chat",
        cascade="all, delete-orphan", 
        passive_deletes=True,
    )


class DbUserChat(Base):
    __tablename__ = 'user_chat'

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('chat.id', ondelete='CASCADE'), primary_key=True)
    is_main: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    chat: Mapped[DbChat] = relationship("DbChat", back_populates="relationships")


class DbTag(Base):
    __tablename__ = 'tag'
    
    name: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    chat_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('chat.id', ondelete='CASCADE'),
                                         primary_key=True, nullable=False)

    message_tags: Mapped[List[DbMessageTag]] = relationship(
        "DbMessageTag",
        back_populates="tag",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    chat: Mapped[DbChat] = relationship("DbChat", back_populates="tags")


class DbMessageTag(Base):
    __tablename__ = 'message_tag'
    
    message_id: Mapped[str] = mapped_column(String, primary_key=True)
    tag_name: Mapped[str] = mapped_column(String, primary_key=True)
    tag_chat_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ['tag_name', 'tag_chat_id'],
            ['tag.name', 'tag.chat_id'],
            ondelete='CASCADE'
        ),
    )

    tag: Mapped[DbTag] = relationship(
        "DbTag", 
        back_populates="message_tags",
        foreign_keys=[tag_name, tag_chat_id]
    )


class DbSessionMessage(Base):
    """
    Таблица хранит сообщения, которые были отправлены
    ботом в указанный чат в рамках текущего запроса пользователя, 
    именно они будут удалены при следующей команде 
    пользователя, чтобы не засорять чат
    """
    __tablename__ = 'chat_session_messages'
    
    message_id: Mapped[str] = mapped_column(String, primary_key=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('chat.id', ondelete='CASCADE'),
                                         primary_key=True, nullable=False)

    chat: Mapped[DbChat] = relationship("DbChat", back_populates="session_messages")
