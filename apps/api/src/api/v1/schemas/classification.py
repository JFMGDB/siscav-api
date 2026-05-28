"""Schemas for vehicle classification contracts.

These contracts are backend-owned and are intended to remain stable as classifier
implementations evolve (stub, local model, remote service, etc.).
"""

from enum import Enum

from pydantic import BaseModel, Field


class VehicleCategory(str, Enum):
    car = "car"
    motorcycle = "motorcycle"
    truck = "truck"
    bus = "bus"
    van = "van"
    unknown = "unknown"


class ClassificationConfidence(BaseModel):
    category: VehicleCategory
    score: float = Field(ge=0.0, le=1.0)


class VehicleClassificationRequest(BaseModel):
    """Optional metadata that may accompany an image classification request."""

    plate_hint: str | None = Field(
        default=None,
        description="Optional plate string for additional context (not used by the stub).",
        examples=["ABC1234"],
    )


class VehicleClassificationResult(BaseModel):
    predicted_category: VehicleCategory
    confidence: float = Field(ge=0.0, le=1.0)
    all_scores: list[ClassificationConfidence] = Field(default_factory=list)
    model_version: str = Field(default="stub-v0")
    classifier_backend: str = Field(default="stub")

