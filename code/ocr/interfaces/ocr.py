from abc import ABC, abstractmethod
import numpy as np

class BaseOCRManager(ABC):
    @abstractmethod
    def get_image_transcription(self, image: np.ndarray) -> str:
        """Extract and return text from the given image."""
        pass