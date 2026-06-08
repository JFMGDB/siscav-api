# ADR 013: OCR inference performance and initialization reliability

## Status

Accepted

## Context

Monitor auto-OCR on `/monitor` was slow (130–589 s per request on CPU) and sometimes failed with client timeouts (180 s). Debug instrumentation showed:

- `preprocess_placa()` applied unconditional `cv2.resize(fx=3, fy=3)`, producing images up to **2880×2160** before EasyOCR.
- `_full_frame_fallback()` ran multiple full-frame and crop passes, each with **detail + paragraph** `readtext()` calls.
- A single `readtext()` on 2880×2160 took ~44 s; paragraph fallback added ~42 s more.
- `warm_up_easyocr()` only constructed `easyocr.Reader()` without a dummy inference; startup could report ready before the engine was hot.
- Uvicorn `--reload` restarted the worker and aborted in-flight OCR during development.

## Decision

1. **Cap OCR input size** — Resize any image passed to `readtext()` so the longest side is ≤ 1280 px (`INTER_AREA`).
2. **Conditional upscale in preprocessing** — Apply 3×/2× upscale only on small plate crops (longest side < 200 / 400), not on full frames.
3. **Single-pass OCR on large regions** — Drop `paragraph=True` fallback when capped image longest side > 320 px.
4. **Bound contour work** — Sort plate-like contours by area; process top 6 only.
5. **Slim full-frame fallback** — One capped full-frame pass instead of preprocessed frame + 2 crops + raw loop.
6. **Warm-up with dummy inference** — `warm_up_easyocr()` runs a tiny `readtext()` after `Reader()` init; track `_warm_up_ready` / `_warm_up_error`.
7. **Honest 503 on init failure** — `recognize-plate` returns the concrete warm-up/load error instead of hanging on lazy load.
8. **Demo server start** — `scripts/start_server.ps1` runs uvicorn **without** `--reload`.

## Measured impact (local CPU, 640×480 webcam frame)

| Metric | Before | After (expected) |
|--------|--------|------------------|
| Single `readtext` on oversized frame | 44–87 s | 3–8 s on ~1280 px cap |
| Total `recognize-plate` inference | 130–589 s | Single-digit seconds typical |
| Reader init | ~3.6 s | ~3.6 s + dummy inference |

## Consequences

- Faster demo loop on Intel Iris Xe (CPU-only, no new dependencies).
- Empty-scene frames still reach the API when motion triggers fire; presence gating on the frontend reduces unnecessary calls (ADR 014).
- First request after failed warm-up gets 503 with actionable detail.

## Alternatives considered

- **Replace EasyOCR with Tesseract/Paddle** — Rejected; duplicates ML stack and diverges from existing pipeline.
- **GPU / OpenVINO for OCR** — Rejected for this iteration; CPU cap achieves demo targets with zero new deps.
