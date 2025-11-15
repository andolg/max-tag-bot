from maxapi.types import CallbackButton, NewMessageLink
from maxapi.enums.message_link_type import MessageLinkType
from maxapi.methods.types.sended_message import SendedMessage
from maxapi import Bot

from ui.base import BaseRoute
from interfaces.tags import BaseTagManager
from interfaces.sessions import BaseSessionsManager
from models import Tag, Message, TagOperation


class GetMessagesRoute(BaseRoute):
    def __init__(self,
                 tag_manager: BaseTagManager,
                 session_manager: BaseSessionsManager,
                 bot: Bot,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.session_manager = session_manager
        self.tag_manager = tag_manager
        self.bot = bot

    async def handle(self, event, args):
        curr_chat_id, user_id = event.get_ids()
        chat_id = int(args['chat_id'][0])
        tags = [Tag(name=tn) for tn in args['tag']]
        if 'op' in args and args['op'] and len(args['tag']) > 1:
            messages = self.tag_manager.get_messages_multitag(user_id=user_id,
                                                                 chat_id=chat_id,
                                                                 tags=tags,
                                                                 tag_op=TagOperation(args['op']))
        else:
            messages = self.tag_manager.get_messages(user_id=user_id, chat_id=chat_id, tag=tags[0])
        
        mids = [message.message_id for message in messages]
        print(mids, flush=True)

        sent_msg_ids = []
        for mid in mids:
            link = NewMessageLink(type=MessageLinkType.FORWARD, mid=mid)
            sent_msg = await self.bot.send_message(chat_id=curr_chat_id, link=link)
            if isinstance(sent_msg, SendedMessage):
                sent_msg_ids.append(sent_msg.message.body.mid)
        
        self.session_manager.update_session(user_id, curr_chat_id, sent_msg_ids)

    def build_text(self, event, args: dict):
        if len(args['tag']) > 1:
            return "⬆️ Собщения с тегами " + ' '.join(args['tag'])
        return "⬆️ Собщения с тегом " + args['tag'][0]

    def build_buttons(self, event, args):
        chat_id = int(args['chat_id'][0])
        back_button_pl = f'/tags?chat_id={chat_id}'
        return [[CallbackButton(text="Назад", payload=back_button_pl)]]