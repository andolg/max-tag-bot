from maxapi import Bot

from interfaces.chats import BaseChatManager
from interfaces.tags import BaseTagManager
from interfaces.sessions import BaseSessionsManager
from ocr_http_adapter.ocr import httpOCR

from ui.tag_bot.routes.greeting import GreetingRoute
from ui.tag_bot.routes.start import StartRoute
from ui.tag_bot.routes.help import HelpRoute
from ui.tag_bot.routes.tags import TagsRoute
from ui.tag_bot.routes.menu import MenuRoute
from ui.tag_bot.routes.groups import GroupsRoute
from ui.tag_bot.routes.add_tag import ReplyRoute
from ui.tag_bot.routes.get_messages import GetMessagesRoute

from ui.tag_bot.routes.ocr import OCRRoute
from ui.tag_bot.ui import TagBotUI


def build_ui(tag_manager: BaseTagManager,
             chat_manager: BaseChatManager,
             session_manager: BaseSessionsManager,
             ocr_client: httpOCR,
             bot: Bot) -> TagBotUI:
    """
    Build routes and return a UI object.
    """
    routes = {
        '/greeting': GreetingRoute(),
        '/start': StartRoute(chat_manager=chat_manager, bot=bot),
        '/help': HelpRoute(),
        '/tags': TagsRoute(tag_manager=tag_manager),
        '/get_messages': GetMessagesRoute(tag_manager=tag_manager,
                                          session_manager=session_manager,
                                          bot=bot),
        '/groups': GroupsRoute(chat_manager=chat_manager),
        '/menu': MenuRoute(),
        '/add_tag': ReplyRoute(tag_manager=tag_manager),
        '/ocr': OCRRoute(ocr_client=ocr_client),
    }
    return TagBotUI(routes=routes)
