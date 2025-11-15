import asyncio
import logging
import os

from maxapi import Bot, Dispatcher
from maxapi.types import MessageCreated, BotStarted, MessageCallback
from maxapi.methods.types.sended_message import SendedMessage

from ui.tag_bot import build_ui, TagBotUI

from sql_adapters.tags import SQLTagManager
from sql_adapters.chats import SQLChatManager
from sql_adapters.sessions import SQLSessionManager
from sql_adapters.db import init_db
from ocr_http_adapter.ocr import httpOCR


logging.basicConfig(level=logging.INFO)

with open('token.txt', 'r') as f:
    token = f.read()

bot = Bot(token)
dp = Dispatcher()

ui: TagBotUI
session_manager: SQLSessionManager


@dp.bot_started()
async def hello(event: BotStarted):
    route_name = '/greeting'
    args = {}
    response = await ui.respond(event, route_name, args)
    await bot.send_message(chat_id=event.chat_id, **response)


@dp.message_created()
async def message_created(event: MessageCreated):
    await message_handler(event)


@dp.message_callback()
async def message_callback(event: MessageCallback):
    await message_handler(event)


async def message_handler(event):
    # End previous session before ui.respond (it can send new messages to the current session)
    prev_sess_messages = session_manager.end_session(event.get_ids()[0])

    if isinstance(event, MessageCreated):
        route_name, args = ui.extract_message_created_payload(event)
    elif isinstance(event, MessageCallback):
        route_name, args = ui.extract_message_callback_payload(event)
    
    if route_name is not None:
        response = await ui.respond(event, route_name, args)
        sent_message: SendedMessage = await event.message.answer(**response)

        if isinstance(sent_message, SendedMessage):
            chat_id, user_id = event.get_ids()
            session_manager.update_session(user_id, chat_id, [sent_message.message.body.mid])

        # Clear previous session.
        # This is done after sending the response for a smoother chat interaction.
        for mid in prev_sess_messages:
            await bot.delete_message(mid)


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    sess_maker = init_db(os.getenv('DB_CONNECTION_STRING'))
    chat_manager = SQLChatManager(sess_maker)
    tag_manager = SQLTagManager(sess_maker)
    session_manager = SQLSessionManager(sess_maker)
    ocr_client = httpOCR(os.getenv('OCR_BASE_URL'))
    ui = build_ui(tag_manager=tag_manager,
                  chat_manager=chat_manager,
                  session_manager=session_manager,
                  ocr_client=ocr_client,
                  bot=bot)

    asyncio.run(main())
