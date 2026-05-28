# ADR 002: Vehicle Classification Layer (Backend-owned)

## Status

Accepted

## Context

SISCAV currently makes an access decision based on a plate-centric model:
- whitelist entries live in `authorized_plates`
- access attempts are logged in `access_logs` with `Authorized` / `Denied`

There is an optional OCR route (`POST /api/v1/ml/recognize-plate`) that returns plate candidates, but there is **no vehicle category/type classification** concept in the backend (no DB tables, no contracts, no services).

The project roadmap requires future integration of a vehicle classifier model. This classifier is expected to evolve over time (different model versions, potentially different backends such as local inference or remote services). The backend must own:
- public API contracts for classification
- business rules around classification
- data normalization / transformation for inference
- integration boundaries to avoid leaking ML concerns into the frontend

## Decision

Introduce a backend-owned classification layer with:

1. **Stable Pydantic contracts** in `apps/api/src/api/v1/schemas/classification.py`
2. A **classifier abstraction** using a `Protocol` in `apps/api/src/api/v1/ml/classifier.py`
3. A **stub classifier** (`StubVehicleClassifier`) as the default implementation
4. A new API endpoint `POST /api/v1/ml/classify-vehicle` that uses dependency injection to obtain the current classifier implementation

This prepares the backend for a real classifier integration while keeping the current plate-centric flows unchanged.

## Rationale

- **Backend ownership**: contracts and orchestration must not move to the frontend; the frontend should only consume backend contracts.
- **DIP / Replaceability**: `VehicleClassifier` provides a clear integration boundary so classifier implementations can change without touching API contracts.
- **Graceful degradation**: the stub allows the API and tests to function even before a real classifier is integrated.
- **Minimalism**: no new persistence or migrations are introduced until there is a real need to store classification results.

## Consequences

- The API gains a new route under the existing `/ml` namespace.
- The backend gains a new integration seam for ML inference without introducing heavy dependencies.
- A future real model integration can be added by extending `get_vehicle_classifier()` (e.g., switch by environment variable or configuration) and by adding optional dependencies to `requirements-ml.txt`.

## Implementation inventory (what was changed)

This section is a checklist for the engineer who will integrate the real classifier model.

### Created

- `apps/api/src/api/v1/schemas/classification.py`
- `apps/api/src/api/v1/ml/classifier.py`
- `apps/api/src/api/v1/endpoints/classification.py`
- `tests/unit/test_classification.py`
- `tests/manual/debug_token.py`
- `docs/architecture/adr/002-vehicle-classification-layer.md`

### Modified

- `apps/api/src/api/v1/api.py` (router registration under `/api/v1/ml/*`)
- `apps/api/src/api/v1/deps.py` (added `get_classifier()` dependency)
- `apps/api/src/api/v1/schemas/__init__.py` (exports for the new classification schemas)
- `pyproject.toml` (removed duplicated `[dependency-groups]` section)
- `tests/manual/README.md` (updated manual helper list)
- `docs/architecture/adr/README.md` (linked ADR 002)

### Removed

- `tests/manual/register_endpoint_manual.py` (stale script referencing an API route that isn't part of the current backend)

### Moved

- `scripts/debug_token.py` → `tests/manual/debug_token.py` (manual-only helper; repo-root bootstrap fixed)

## Alternatives considered

- **Frontend classification**: rejected because it would duplicate business rules and make the system harder to evolve and secure.
- **Immediate DB schema changes**: rejected to avoid premature complexity; storage requirements should be driven by concrete use cases.
- **Hard-coding a single classifier implementation**: rejected; it would create tight coupling and make future evolution costly.

