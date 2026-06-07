"""One-time offline conversion: TorchScript MobileNetV2 -> ONNX.

Requires: uv sync --locked --extra convert
Usage:
  uv run python scripts/convert_ambulance_to_onnx.py \\
    --input ../modelo_ambulancia_prod \\
    --output models/ambulance_classifier.onnx
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert TorchScript ambulance model to ONNX")
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to TorchScript model directory (modelo_ambulancia_prod)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("models/ambulance_classifier.onnx"),
        help="Output .onnx file path",
    )
    parser.add_argument("--input-size", type=int, default=224)
    args = parser.parse_args()

    try:
        import torch
    except ImportError:
        print("torch not installed. Run: uv sync --locked --extra convert", file=sys.stderr)
        return 1

    input_path = args.input.resolve()
    if (
        input_path.is_dir()
        or (input_path.is_file() and input_path.suffix.lower() == ".zip")
        or input_path.is_file()
    ):
        load_path = input_path
    else:
        print(f"Input path not found: {input_path}", file=sys.stderr)
        return 1

    output_path = args.output.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading TorchScript from {load_path}...")
    model = torch.jit.load(str(load_path), map_location="cpu")
    model.eval()

    dummy = torch.randn(1, 3, args.input_size, args.input_size)
    print(f"Exporting ONNX to {output_path}...")
    torch.onnx.export(
        model,
        dummy,
        str(output_path),
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={"input": {0: "batch"}, "output": {0: "batch"}},
        opset_version=17,
        dynamo=False,
    )
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
