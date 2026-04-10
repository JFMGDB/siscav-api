from PIL import Image
from io import BytesIO


def assert_image_bytes(content: bytes) -> None:
    try:
        image = Image.open(BytesIO(content))
        image.verify()  # valida se é uma imagem válida
    except Exception:
        raise ValueError("not a valid image")
        