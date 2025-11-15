import asyncio

from maxapi.types import UpdateUnion, MessageCreated, MessageCallback, CallbackButton, ButtonsPayload
from maxapi.enums.intent import Intent
from urllib.parse import parse_qs, urlparse


class ChatUI:
    def __init__(self, routes: dict):
        self.routes = routes

    async def respond(self, event: UpdateUnion, route_name: str, args: dict) -> dict:
        """Render response message and perform actions based on the event."""
        
        if route_name not in self.routes:
            raise ValueError('Route not found')
        route: BaseRoute = self.routes[route_name]
        
        handle_method = route.handle
        if asyncio.iscoroutinefunction(handle_method):
            await handle_method(event, args)
        else:
            handle_method(event, args)

        response = {}
        response['text'] = route.build_text(event, args)
        response['attachments'] = []
        buttons = route.build_buttons(event, args)
        if buttons != [[]]:
            buttons_payload = ButtonsPayload(buttons=route.build_buttons(event, args)).pack()
            response['attachments'].append(buttons_payload)

        # === Images ===
        # TODO

        return response
    
    def extract_message_created_payload(self, event: MessageCreated) -> tuple[str, dict]:
        message_text = event.message.body.text.split()
        route_name = message_text[0]
        args = {k: [v] for k, v in zip(range(0, len(message_text) - 1), message_text[1:])}
        return route_name, args

    def extract_message_callback_payload(self, event: MessageCallback) -> tuple[str, dict]:
        pl_parsed = urlparse(event.callback.payload)
        route_name = pl_parsed.path
        args = parse_qs(pl_parsed.query)
        return route_name, args


class BaseRoute():
    def __init__(self, bgrid_h=5, bgrid_w=3, empty_pl='/empty'):
        self.bgrid_h = bgrid_h
        self.bgrid_w = bgrid_w
        self.empty_pl = empty_pl

    def handle(self, event: UpdateUnion, args):
        return
    
    def build_buttons(self, event: UpdateUnion, args):
        return [[]]
    
    def build_text(self, event: UpdateUnion, args):
        return ''
    
    # def build_images():
    #    return []

    def _build_button_grid(self, contents: list[tuple[str, str]]):
        """
        Build a 2D list of CallbackButton objects.
        The grid will be exactly `self.bgrid_w` buttons wide, and no more than `self.bgrid_h` rows tall.
        If a row is not full, the remaining columns will be filled
        with placeholder buttons (text='...', payload=self.empty_pl, intent=Intent.NEGATIVE).

        Args:
            contents (list[tuple[str, str]]): A list of (button_text, button_payload) tuples
        
        """
        grid = []
        total_slots = self.bgrid_h * self.bgrid_w
        contents = contents[:total_slots]  # Don't exceed max capacity

        for i in range(0, len(contents), self.bgrid_w):
            row_contents = contents[i:i + self.bgrid_w]

            # Pad last row
            while len(row_contents) < self.bgrid_w:
                row_contents.append(("...", self.empty_pl))

            row = [
                CallbackButton(
                    text=text,
                    payload=pl,
                    intent=Intent.DEFAULT if pl != self.empty_pl else Intent.NEGATIVE
                )
                for text, pl in row_contents
            ]
            grid.append(row)
        return grid
