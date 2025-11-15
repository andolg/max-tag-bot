from maxapi.types import CallbackButton

from ui.base import BaseRoute

class MenuRoute(BaseRoute):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def build_text(self, event, args):
        return "Главное меню"

    def build_buttons(self, event, args):
        return [
            [
                CallbackButton(text="Мои теги", payload=f"/tags?chat_id={event.get_ids()[0]}"),
                CallbackButton(text="Группы", payload="/groups")
            ],
            [
                CallbackButton(text="Помощь", payload="/help")
            ]
        ]