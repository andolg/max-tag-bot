from paddleocr import PaddleOCRVL
from interfaces.ocr import *

class PaddleOCRManager(BaseOCRManager):
    def __init__(self):
        self.pipeline = PaddleOCRVL(use_doc_unwarping=True)

    def _resize_image(self, image: np.ndarray, max_dim: int = 1024) -> np.ndarray:
        height, width = image.shape[:2]
        if max(height, width) > max_dim:
            scale = max_dim / max(height, width)
            new_size = (int(width * scale), int(height * scale))
            from cv2 import resize, INTER_AREA
            print(f"Downsampling image from ({width}x{height}) → ({new_size})")
            image = resize(image, new_size, interpolation=INTER_AREA)
        return image

    def get_image_transcription(self, image: np.ndarray) -> str:
        print('Performing OCR on the image')
        image = self._resize_image(image)
        output = self.pipeline.predict(image, use_layout_detection=False,
                                       prompt_label='ocr')
        texts = []
        for r in output:
            texts.extend(r.markdown["markdown_texts"])
        return "".join(texts)
