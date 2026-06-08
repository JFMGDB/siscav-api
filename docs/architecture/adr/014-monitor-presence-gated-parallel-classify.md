# ADR 014: Monitor presence-gated capture and parallel ambulance classification

## Status

Accepted

## Context

The `/monitor` page had three frontend issues:

1. **Blind 6 s OCR timer** — `recognize-plate` was called even with no vehicle/plate in frame.
2. **Missed triggers** — Slow OCR held the in-flight lock and dropped timer ticks; pointing a plate did not reliably start recognition.
3. **No parallel classification** — Only `recognize-plate` ran; ambulance ONNX classification existed on `/ml-playground` and on access-log ingest (ADR 011) but not in the auto monitor loop.

Additionally, `GET /access_logs?...` without a trailing slash caused **307 redirects**, doubling poll traffic (~40 req/min per tab at 3 s interval).

## Decision

### Presence-gated pipeline (frontend)

- Sample motion every **1 s** via downscaled grayscale frame diff (`64×48`) from the registered camera handler.
- Fire OCR + classification only when motion score ≥ **14**, or on **30 s** idle recheck if motion was seen recently.
- Remove the blind `setInterval(6000)` OCR loop.

### Parallel classify + OCR (frontend)

On each triggered cycle:

1. Capture one JPEG blob.
2. Start `classifyVehicle` and `recognizePlate` in parallel.
3. If classification returns `ambulance` with confidence ≥ **0.85** (matches `VEHICLE_CLASSIFIER_THRESHOLD`): abort OCR, register access with plate sentinel `AMBULANCIA`, rely on ingest-side ambulance auto-authorization (ADR 011) and gate auto-open.
4. Else continue OCR stable-read → whitelist / operator dialog flow unchanged.

### access_logs polling reduction

- Fix GET URL to `/api/v1/access_logs/?...` (trailing slash) to eliminate 307 doubling.
- Raise poll interval to **10 s**; disable `refetchOnWindowFocus` on the last-capture query.

## Consequences

- Empty static scenes no longer spam the OCR API.
- Ambulance detection target **< 5 s** (ONNX 224 px on CPU).
- Plate OCR target **< 10 s** after ADR 013 backend caps.
- Last-reading panel updates less aggressively but with half the HTTP overhead.

## Alternatives considered

- **Server-side motion detection** — Rejected; browser already has the video element; avoids extra upload round-trips for motion-only probes.
- **Sequential classify-then-OCR** — Rejected; parallel start minimizes ambulance path latency.
