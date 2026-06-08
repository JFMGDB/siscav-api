# ADR 012: OCR plate flow validation and monitor operator orchestration

## Status

Accepted

## Context

The Mantis monitor must support a real academic demo: USB camera capture, server-side EasyOCR, whitelist lookup, access log audit, and gate actuation. The previous UI required manual clicks between OCR and access log ingest, and contour-only OCR often returned empty candidates. A synthetic canvas fallback existed when the camera produced no frame, which is unsuitable for a live demo.

Brazil uses two plate formats (legacy `LLLNNNN` and Mercosul `LLLNLNN`); both are validated server-side via `validate_brazilian_plate()`.

## Decision

1. **OCR reliability (backend)** — Extend `plate_ocr.py` with:
   - EasyOCR `allowlist` restricted to `A-Z` and `0-9`.
   - Full-frame OCR fallback when contour detection returns no candidates.

2. **Monitor orchestration (frontend)** — Add `useMonitorPlateOrchestration`:
   - Poll camera frames and call `POST /api/v1/ml/recognize-plate`.
   - Load whitelist via `GET /api/v1/whitelist`.
   - On stable read (two consecutive identical plates):
     - If whitelisted → `POST /api/v1/access_logs/` (auto gate when `GATE_AUTO_OPEN_ON_AUTHORIZE=true`).
     - If not whitelisted → operator dialog to authorize; on confirm → access log + `POST /api/v1/gate_control/trigger`; optional second dialog to add plate to whitelist.
   - Fail closed when `captureFrame()` is empty (no synthetic image).

3. **Real-only demo policy** — No frontend mocks for OCR, whitelist, access logs, or gate in the auto path. CI may mock EasyOCR in pytest; banca/e2e use the live stack.

4. **UI polish** — Map `ocr_success` from access logs to the last-reading panel; enable token refresh retry on `createAccessLog`.

OCR remains a separate HTTP step from access log ingest (no merged endpoint).

## E2E validation (2026-06-07)

Validated on `localhost:3000` + `localhost:8000` with account `fguerra127@gmail.com` (client admin), Chrome DevTools MCP (cursor-ide-browser), and live EasyOCR (CPU).

| Step | Result |
|------|--------|
| Login + JWT cookies | OK |
| Whitelist contains `ABC1D23` | OK (pre-existing) |
| USB camera saved in `/camera` | OK |
| `POST /ml/recognize-plate` → `ABC1D23` | OK (~60–120 s per frame on CPU) |
| `POST /access_logs/` whitelisted plate → `Authorized` | OK |
| Monitor auto-OCR → dialog "Nova placa detectada" for `XYZ9A87` | OK (after 2 stable reads) |
| Operator authorize → denied log + gate attempt → "Cadastrar placa" dialog | OK |
| `POST /access_logs/{id}/whitelist` → `XYZ9A87` in DB | OK |

### Gate actuator (demo without Wokwi)

**Problem:** `.env.local` had `GATE_ACTUATOR_URL=http://127.0.0.1:9080/open` with no listener. Auto-open returned `connection_refused`; manual authorize called `POST /gate_control/trigger`, got HTTP 502, and aborted before the whitelist dialog.

**Fix (minimal):**

1. Set `GATE_ACTUATOR_URL=` (empty) in `siscav-api/.env.local` → API uses built-in `integration: simulated` (not a frontend mock).
2. In `use-monitor-plate-orchestration.ts`, wrap `gateApi.openGate()` so access log + whitelist dialog proceed even when the actuator is unreachable (warning toast instead of hard failure).

**Restore for Wokwi demo:** set `GATE_ACTUATOR_URL=http://127.0.0.1:9080/open`, start Wokwi + `wokwigw` per `demo/wokwi-gate/README.md`, restart uvicorn. Use `127.0.0.1`, not `localhost`.

### Demo assets

Reference plate JPEGs for rehearsal: `siscav-web/public/demo/plates/abc1d23.jpg`, `xyz9a87.jpg` (point phone/webcam at printed image or use live vehicle).

### Demo timing note

EasyOCR on CPU dominates latency. Expect **1–2 minutes per OCR request** on first warm models; monitor waits for **two consecutive identical reads** (~12 s interval between attempts, but each attempt blocks until OCR returns). For the banca, warm up the API before presenting (start server, trigger one OCR from `/monitor`).

## Consequences

- Operators see automatic authorized access without extra clicks when the plate is whitelisted.
- Unknown plates require explicit confirmation before gate override.
- Demo depends on USB camera configuration and ML dependencies on the API host.
- First EasyOCR request may be slow (model load).
- On Render free tier (512MB RAM), **EasyOCR is not installed** — `POST /ml/recognize-plate` returns **503**. Run OCR locally (`pip install -r requirements-ml.txt`) or point the frontend at `localhost:8000` for banca demos. Render hosts auth, whitelist, access logs, and ONNX ambulance classification.

## Alternatives considered

- **Merge OCR into `POST /access_logs/`** — Rejected; keeps IoT ingest path simple and preserves operator choice.
- **Client-side Tesseract** — Rejected; duplicates ML stack and diverges from server truth.
- **Synthetic IoT canvas when camera missing** — Rejected for monitor auto/demo paths.
