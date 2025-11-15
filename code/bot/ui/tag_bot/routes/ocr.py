from ocr_http_adapter.ocr import httpOCR
from ui.base import BaseRoute
from maxapi.types import MessageCreated
from maxapi.types.message import LinkedMessage, MessageLinkType
from maxapi.types.attachments.image import Image
from maxapi.types.attachments.attachment import PhotoAttachmentPayload
from maxapi.types import CallbackButton


class OCRRoute(BaseRoute):
    def __init__(self, ocr_client: httpOCR, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ocr_client = ocr_client

    def build_buttons(self, event, args):
        return [[
            CallbackButton(text="Назад", payload="/menu")
        ]]

    def _get_image_url(self, event: MessageCreated) -> str | None:
        """Возвращает URL изображения или None, если его нет."""
        link = event.message.link
        if not (isinstance(link, LinkedMessage) and link.type == MessageLinkType.REPLY):
            return None

        msg = link.message

        for att in msg.attachments or []:
            if isinstance(att, Image):
                payload = att.payload
                if isinstance(payload, PhotoAttachmentPayload):
                    return payload.url
                if payload and hasattr(payload, "url"):
                    return payload.url

        return None

    def build_text(self, event: MessageCreated, args):
        image_url = self._get_image_url(event)

        if image_url is None:
            return "Пожалуйста, отправь команду /ocr ответом на сообщение с изображением."

        print("DEBUG image_url:", image_url)

        try:
            transcribed_text = self.ocr_client.get_transcription_by_url(
                image_url)
        except Exception as e:
            return f"Не удалось распознать текст на изображении."


        if not transcribed_text:
            return "Текст на изображении не распознан."

        return transcribed_text
