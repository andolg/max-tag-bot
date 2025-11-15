import requests

from interfaces.ocr import BaseOCR


class httpOCR(BaseOCR):
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_transcription_by_url(self, image_url: str) -> str:
        """Send image URL to OCR service and return extracted text."""
        response = requests.post(f"{self.base_url}/ocr",
                                 json={"image": image_url},
                                 timeout=60)

        if response.status_code != 200:
            raise Exception(f"OCR service error: {response.text}")
        
        data = response.json()
        return data.get("text", "")