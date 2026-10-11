"""HTTP request/response schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from atlas.models import RunResult


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class RunResultInput(StrictModel):
    name: str = Field(min_length=1, max_length=120)
    quality: float = Field(ge=0.0, le=1.0, allow_inf_nan=False)
    accelerator_hours: float = Field(gt=0.0, allow_inf_nan=False)
    peak_memory_gb: float = Field(ge=0.0, allow_inf_nan=False)
    tokens_per_second: float = Field(ge=0.0, allow_inf_nan=False)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("name must not be blank")
        return value

    def to_run_result(self) -> RunResult:
        return RunResult(
            name=self.name,
            quality=self.quality,
            accelerator_hours=self.accelerator_hours,
            peak_memory_gb=self.peak_memory_gb,
            tokens_per_second=self.tokens_per_second,
        )


class SelectionRequest(StrictModel):
    results: list[RunResultInput] = Field(min_length=1, max_length=500)
    min_quality: float = Field(ge=0.0, le=1.0, allow_inf_nan=False)
    max_accelerator_hours: float = Field(gt=0.0, allow_inf_nan=False)


class SelectedRunOutput(StrictModel):
    name: str
    quality: float
    accelerator_hours: float
    peak_memory_gb: float
    tokens_per_second: float


class SelectionResponse(StrictModel):
    selected: SelectedRunOutput
    quality_margin: float
    quality_per_accelerator_hour: float
    eligible_run_count: int
    considered_run_count: int
