from abc import ABC, abstractmethod

class BaseOCR(ABC):
    @abstractmethod
    def get_transcription_by_url(self, image_url: str) -> str:
        """Send image URL to OCR service and return extracted text."""
        pass