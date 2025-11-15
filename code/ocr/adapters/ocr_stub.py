from interfaces.ocr import *

class StubOCRManager(BaseOCRManager):
    def get_image_transcription(self, image: np.ndarray):
        return "Cейчас недоступно"