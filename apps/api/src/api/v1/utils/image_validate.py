from io import BytesIO

from PIL import Image


def assert_image_bytes(content: bytes) -> None:
    try:
        image = Image.open(BytesIO(content))
        image.verify()  # valida se é uma imagem válida
    except Exception as exc:
        msg = "not a valid image"
        raise ValueError(msg) from exc
