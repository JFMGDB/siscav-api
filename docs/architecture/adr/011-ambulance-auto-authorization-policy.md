# ADR 011: Ambulance Auto-Authorization Policy

## Status

Accepted

## Context

SISCAV (Mantis) integrates a binary ambulance classifier (MobileNetV2) to support hospital access control. The model runs on Render Free Tier (CPU-only, no PyTorch at runtime). Access decisions remain backend-owned per [ADR 002](./002-vehicle-classification-layer.md).

Requirements:

- Auto-authorize ambulances on IoT ingest when confidence ≥ threshold, even without whitelist
- No database migration for classification audit in this phase
- Academic demo needs isolated ML inspection without polluting access logs
- Render cold starts and IoT HTTP timeouts are operational risks

## Decision

### 1. Runtime: ONNX Runtime (CPU)

- Deploy artifact: single `ambulance_classifier.onnx` file
- Backend id: `VEHICLE_CLASSIFIER_BACKEND=onnx`
- **No `torch` in production runtime** (Render memory/dependency constraints)
- Conversion from TorchScript is a one-time offline step (`scripts/convert_ambulance_to_onnx.py`, extra `convert`)

### 2. Concurrency

- All `classifier.classify()` calls use `fastapi.concurrency.run_in_threadpool`
- `threading.Lock` is **only** used in `_load_model()` (session initialization)
- `InferenceSession.run()` is invoked **without** a global lock (ORT thread-safe inference)

### 3. Auto-authorization policy (ingest only)

On `POST /api/v1/access_logs/` when `backend=onnx`:

1. Classify frame in threadpool
2. If `predicted_category == ambulance` AND `confidence >= VEHICLE_CLASSIFIER_THRESHOLD` (default **0.85**): set `Authorized`
3. Else: existing whitelist logic unchanged
4. Gate auto-open follows existing ADR 010 rules when authorized

Structured log: `ambulance_auto_authorized` with plate, confidence, model_version.

### 4. Ephemeral classification data

- `vehicle_classification` on `AccessLogRead` response only — **not** persisted in `access_logs`
- No Alembic migration in this phase

### 5. ML Playground (academic demo)

- Frontend route `/ml-playground` calls `POST /api/v1/ml/classify-vehicle` directly
- No access log creation, no gate trigger
- Results stay on screen until next upload (React local state)

### 6. Cold start mitigations

| Mitigation | Purpose |
|------------|---------|
| FastAPI **lifespan warm-up** | Load ONNX + dummy inference at container startup |
| External **keep-alive** (`GET /api/v1/health` every 10–14 min) | Prevent Render spin-down during operations |
| Pre-demo warm-up runbook | Ping health + one Playground classification before presentation |

IoT firmware HTTP timeout must account for cold-start latency or rely on keep-alive. Retry logic is a future evolution.

## Consequences

- Positive: Clear separation between demo ML path and operational ingest path
- Positive: Minimal DB impact; rollback via `VEHICLE_CLASSIFIER_BACKEND=stub`
- Risk: False-positive ambulance detection opens gate — mitigated by conservative threshold (0.85) and monitoring
- Risk: First request after long idle may still hit Render VM spin-up before warm-up helps

## Alternatives considered

- **Persist classification in DB**: deferred until audit requirements are concrete
- **PyTorch runtime**: rejected for Render Free Tier
- **Frontend-only demo without `/classify-vehicle`**: rejected — hides ML layer from academic evaluation
