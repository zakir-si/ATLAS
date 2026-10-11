import pytest
from pydantic import ValidationError

from atlas.schemas import RunResultInput, SelectionRequest


def test_blank_name_rejected() -> None:
    with pytest.raises(ValidationError):
        RunResultInput(name="   ", quality=0.8, accelerator_hours=1,
                       peak_memory_gb=1, tokens_per_second=1)


def test_nan_rejected() -> None:
    with pytest.raises(ValidationError):
        RunResultInput(name="x", quality=float("nan"), accelerator_hours=1,
                       peak_memory_gb=1, tokens_per_second=1)


def test_empty_request_rejected() -> None:
    with pytest.raises(ValidationError):
        SelectionRequest(results=[], min_quality=0.5, max_accelerator_hours=1)
