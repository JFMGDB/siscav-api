"""Gera imagens JPEG de placas brasileiras (estilo Mercosul) para uso no demo OCR.

Saída padrão: ../siscav-web/public/demo/plates/<placa>.jpg
Uso:
    uv run python scripts/generate_demo_plates.py
    uv run python scripts/generate_demo_plates.py --out ../siscav-web/public/demo/plates

Estilo otimizado para EasyOCR: fundo branco, cabeçalho azul Mercosul,
texto preto bold em alto contraste. Sem traços/parafusos para reduzir ruído.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

DEFAULT_OUT = Path(__file__).resolve().parents[1].parent / "siscav-web" / "public" / "demo" / "plates"

# Placas NÃO presentes em scripts/seed_demo.py (DEMO_PLATES)
# e diferentes da `XYZ9A87` já usada como exemplo de placa desconhecida.
DEMO_NEW_PLATES = [
    "RBL2H45",
    "PFG7T82",
    "MKT3R94",
    "NDV5B27",
    "JHP6Q38",
    "QXC4M75",
    "RKM4729",
    "PTL3947",
    "NCV3614",
    "JBQ7294",
]

MERCOSUL_RE = re.compile(r"^[A-Z]{3}\d[A-Z]\d{2}$")
LEGACY_RE = re.compile(r"^[A-Z]{3}\d{4}$")

PLATE_W, PLATE_H = 1200, 400
HEADER_H = 90
HEADER_BG = (0, 56, 142)  # azul Mercosul
HEADER_FG = (255, 255, 255)
PLATE_BG = (255, 255, 255)
PLATE_FG = (0, 0, 0)
BORDER = (0, 0, 0)


def _validate(plate: str) -> None:
    if not (MERCOSUL_RE.match(plate) or LEGACY_RE.match(plate)):
        raise ValueError(f"Placa fora do padrão BR: {plate!r}")


def _load_font(size: int) -> ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _draw_centered(draw: ImageDraw.ImageDraw, text: str, box: tuple[int, int, int, int],
                   font: ImageFont.ImageFont, fill: tuple[int, int, int]) -> None:
    left, top, right, bottom = box
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = left + (right - left - tw) // 2 - bbox[0]
    y = top + (bottom - top - th) // 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=fill)


def render_plate(plate: str) -> Image.Image:
    _validate(plate)
    img = Image.new("RGB", (PLATE_W, PLATE_H), PLATE_BG)
    draw = ImageDraw.Draw(img)

    draw.rectangle((0, 0, PLATE_W - 1, PLATE_H - 1), outline=BORDER, width=6)
    draw.rectangle((0, 0, PLATE_W, HEADER_H), fill=HEADER_BG)

    header_font = _load_font(48)
    _draw_centered(draw, "BRASIL", (0, 0, PLATE_W, HEADER_H), header_font, HEADER_FG)

    plate_font = _load_font(220)
    _draw_centered(draw, plate, (0, HEADER_H, PLATE_W, PLATE_H), plate_font, PLATE_FG)
    return img


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT,
                        help="Diretório de saída (padrão: siscav-web/public/demo/plates)")
    parser.add_argument("--plates", nargs="*", default=DEMO_NEW_PLATES,
                        help="Lista custom de placas (default: 10 placas demo prontas)")
    parser.add_argument("--force", action="store_true",
                        help="Sobrescreve arquivos existentes")
    args = parser.parse_args()

    out: Path = args.out
    out.mkdir(parents=True, exist_ok=True)

    generated: list[Path] = []
    for plate in args.plates:
        plate = plate.upper().strip()
        target = out / f"{plate.lower()}.jpg"
        if target.exists() and not args.force:
            print(f"[SKIP] {target.name} já existe (use --force para sobrescrever)")
            continue
        img = render_plate(plate)
        img.save(target, format="JPEG", quality=92, optimize=True)
        generated.append(target)
        print(f"[OK]   {target.relative_to(out.parent.parent)}")

    print(f"\n{len(generated)} imagem(ns) gerada(s) em {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
