from maxapi.types import UpdateUnion, CallbackButton
from maxapi.enums.intent import Intent

from ui.base import BaseRoute


class GreetingRoute(BaseRoute):
    def build_text(self, event: UpdateUnion, args: dict):
        return ("Привет! SmartVault — бот для организации сохранённых сообщений\n\n"
                "/start - начать работу с ботом")

    def build_buttons(self, event, args):
        return [[
            CallbackButton(text="Начать", payload="/start", intent=Intent.POSITIVE)
        ]]
