from maxapi import Bot
from maxapi.enums.chat_type import ChatType
from maxapi.types import CallbackButton
from exceptions import AlreadyExistsException

from ui.base import *
from interfaces.chats import BaseChatManager


class StartRoute(BaseRoute):
    def __init__(self,
                 chat_manager: BaseChatManager,
                 bot: Bot,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.chat_manager = chat_manager
        self.bot = bot

    async def handle(self, event: UpdateUnion, args):
        chat_id, user_id = event.get_ids()
        try:
            chat = await self.bot.get_chat_by_id(chat_id)
            chat_title = chat.title if chat.title is not None else ''
            is_main = chat.type is ChatType.DIALOG

            self.chat_manager.add_chat(chat_id, chat_title)
            self.chat_manager.remember_user(user_id, chat_id, is_main)
        except AlreadyExistsException:
            print("Чат уже добавлен")

    def build_text(self, event, args):
        return (
            "👋 Добро пожаловать в SmartVault!\n\n"
            "Этот бот помогает удобно организовывать избранные сообщения:\n"
            "⭐ Добавляйте сообщения в избранное с тегами,\n"
            "🏷️ Группируйте и управляйте тегами,\n"
            "👥 Создавайте общие избранные сообщения через групповые теги для совместной работы,\n"
            "🔎 Находите нужные сообщения по тегам и фильтрам,\n"
            "🖼️ Распознавайте текст на изображениях с помощью ИИ.\n\n"
            "❓ Чтобы увидеть список всех команд, используйте /help."
        )
        
    def build_buttons(self, event, args):
        return [
            [
                CallbackButton(text="Мои теги", payload=f"/tags?chat_id={event.get_ids()[0]}"),
                CallbackButton(text="Помощь", payload="/help")
            ],
            [
                CallbackButton(text="Группы", payload="/groups")
            ]
        ]