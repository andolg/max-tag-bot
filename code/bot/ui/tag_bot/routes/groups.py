from maxapi.types import CallbackButton

from exceptions import NotFoundException
from ui.base import BaseRoute
from interfaces.chats import BaseChatManager

class GroupsRoute(BaseRoute):
    def __init__(self, chat_manager: BaseChatManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat_manager = chat_manager

    def build_text(self, event, args):
        return "Твои группы:"

    def build_buttons(self, event, args):
        try:
            chats = self.chat_manager.get_ext_chats(event.get_ids()[1])
        except NotFoundException:
            chats = []

        chat_names = [chat.name for chat in chats]
        payloads = [f"/tags?chat_id={chat.id}" for chat in chats]
        tag_grid = self._build_button_grid(list(zip(chat_names, payloads)))
        tag_grid.append([
            CallbackButton(text="Назад", payload="/menu")
        ])
        return tag_grid