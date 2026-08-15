"""Orchestration for the Gridfinity assistant.

Coordinates the vision, recommendation, research and packing steps into a
single :class:`AssistantResult`. Each external step degrades gracefully so the
whole pipeline runs with or without API keys.
"""

from __future__ import annotations

import os
from typing import List, Optional

from . import recommender, research, vision
from .models import AssistantResult, GridSpec, ItemGroup


def _has_key(api_key: Optional[str]) -> bool:
    key = api_key or os.getenv("ANTHROPIC_API_KEY")
    return bool(key) and not key.startswith("your_")


def get_groups(
    image_bytes: Optional[bytes],
    media_type: str = "image/jpeg",
    api_key: Optional[str] = None,
) -> tuple[List[ItemGroup], List[str]]:
    """Return item groups from a photo, plus any status notes."""
    notes: List[str] = []
    if image_bytes and _has_key(api_key):
        try:
            groups = vision.analyze_image(
                image_bytes, media_type=media_type, api_key=api_key
            )
            if groups:
                return groups, notes
            notes.append("Vision returned no groups; using demo data instead.")
        except Exception as exc:  # noqa: BLE001 - degrade to demo
            notes.append(f"Vision analysis failed ({exc}); using demo data.")
    elif image_bytes:
        notes.append(
            "No ANTHROPIC_API_KEY configured — showing demo groups. Set the "
            "key to analyze your actual photo."
        )
    else:
        notes.append("No image provided — showing demo groups.")
    return vision.demo_groups(), notes


def plan(
    grid: GridSpec,
    image_bytes: Optional[bytes] = None,
    media_type: str = "image/jpeg",
    api_key: Optional[str] = None,
    do_research: bool = True,
) -> AssistantResult:
    """Run the full pipeline for one photo + grid."""
    groups, notes = get_groups(image_bytes, media_type=media_type, api_key=api_key)

    recommendations = recommender.recommend_all(groups)

    if do_research:
        for rec in recommendations:
            rec.printable_models = research.research_or_fallback(
                rec, api_key=api_key
            )
        if not _has_key(api_key):
            notes.append(
                "Container links are generic search/generator links — set "
                "ANTHROPIC_API_KEY for live web research of specific models."
            )

    layout = recommender.pack_grid(grid, recommendations)
    if layout.unplaced_groups:
        notes.append(
            f"{len(layout.unplaced_groups)} group(s) did not fit the "
            f"{grid.width_units}x{grid.depth_units} grid: "
            + ", ".join(layout.unplaced_groups)
        )

    return AssistantResult(
        groups=groups,
        recommendations=recommendations,
        layout=layout,
        notes=notes,
    )
