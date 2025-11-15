from maxapi.types import CallbackButton

from ui.base import BaseRoute
from interfaces.tags import BaseTagManager


class TagsRoute(BaseRoute):
    """Expects `chat_id` in builder/handler `args`"""
    def __init__(self, tag_manager: BaseTagManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tag_manager = tag_manager

    def build_text(self, event, args: dict):
        return "Теги:"

    def build_buttons(self, event, args):
        curr_chat_id, user_id = event.get_ids()
        if 'chat_id' not in args:
            chat_id = curr_chat_id
        else:
            chat_id = int(args['chat_id'][0])
        
        # Tag list
        tags = self.tag_manager.get_tags(user_id, chat_id)
        tag_names = [tag.name for tag in tags]
        tag_payloads = [f'/get_messages?chat_id={chat_id}&tag={tn}' for tn in tag_names]

        # тут передавались объекты Tag в виде tags вместо [t.name for t in tags]
        tag_grid = self._build_button_grid(list(zip([t.name for t in tags], tag_payloads)))

        # Back button
        back_button_pl = '/menu' if chat_id == curr_chat_id else '/groups'
        tag_grid.append([
            CallbackButton(text="Назад", payload=back_button_pl)
        ])
        return tag_grid