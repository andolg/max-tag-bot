from typing import Optional

from maxapi.types import MessageCreated
from maxapi.types.message import LinkedMessage, MessageLinkType
from ui.base import ChatUI


class TagBotUI(ChatUI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _extract_reply_tags(self, event: MessageCreated) -> tuple[bool, list[str]]:
        text = event.message.body.text.split()
        if not text:
            return False, []
        link = event.message.link
        if not (isinstance(link, LinkedMessage) and link.type == MessageLinkType.REPLY):
            return False, []
        first = text[0]
        if first == "/add_tag":
            return True, text[1:]
        if not first.startswith("/"):
            return True, text
        return False, []

    def extract_message_created_payload(self, event: MessageCreated) -> tuple[str | None, dict]:
        text = event.message.body.text.split()
        if not text:
            return "", {}
        has_tags, tags = self._extract_reply_tags(event)
        print(has_tags, tags, flush=True)
        if has_tags:
            return "/add_tag", {"tag": tags}
        
        if text[0].startswith("/"):
            route_name = text[0]
            args = {i: [v] for i, v in enumerate(text[1:])}
            return route_name, args

        return None, {}