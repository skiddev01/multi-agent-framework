"""Gridfinity assistant: photo -> grouped items -> printable bin recommendations."""

from .models import (
    AssistantResult,
    BinRecommendation,
    GridLayout,
    GridSpec,
    ItemGroup,
)
from .service import plan

__all__ = [
    "AssistantResult",
    "BinRecommendation",
    "GridLayout",
    "GridSpec",
    "ItemGroup",
    "plan",
]
