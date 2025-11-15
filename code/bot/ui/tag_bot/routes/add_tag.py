from maxapi.types.message import LinkedMessage, MessageLinkType
from maxapi.types import CallbackButton

from ui.base import BaseRoute
from interfaces.tags import BaseTagManager
from models import Tag

class ReplyRoute(BaseRoute):
    def __init__(self, tag_manager: BaseTagManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tag_manager = tag_manager

    def handle(self, event, args):
        link = event.message.link
        if not (isinstance(link, LinkedMessage) and link.type == MessageLinkType.REPLY):
            print("ReplyRoute: No reply link found in the message.")
        mid = link.message.mid

        tag_values = args.get("tag", [])
        tags = [Tag(name=t) for t in tag_values]

        self.tag_manager.add_tags(user_id=event.get_ids()[1], chat_id=event.get_ids()[0],
                                 tags=tags, message_id=mid)
        return

    def build_text(self, event, args: dict):

        return "Тег присвоен сообщению."
    
    def build_buttons(self, event, args: dict):
        return [[CallbackButton(text="Назад", payload="/menu")]]