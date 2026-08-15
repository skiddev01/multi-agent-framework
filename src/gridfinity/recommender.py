"""Turn item groups + a grid into bin recommendations and a packed layout.

This module is deterministic and offline: it depends only on the Gridfinity
spec math, never on the network or an LLM. That makes it fully unit-testable
and keeps the app useful even without API keys.
"""

from __future__ import annotations

from typing import List

from . import spec
from .models import (
    BinRecommendation,
    GridLayout,
    GridSpec,
    ItemGroup,
    PlacedBin,
)


def recommend_bin(group: ItemGroup) -> BinRecommendation:
    """Recommend the smallest standard bin that fits a group's largest item."""
    dims = group.bounding_dimensions()
    bin_size = spec.fit_bin(dims.length_mm, dims.width_mm, dims.height_mm)
    warning = spec.describe_fit(
        bin_size, dims.length_mm, dims.width_mm, dims.height_mm
    )

    rationale = (
        f"Largest item ~{dims.length_mm:.0f} x {dims.width_mm:.0f} x "
        f"{dims.height_mm:.0f} mm. A {bin_size.label} bin gives "
        f"{bin_size.usable_width_mm:.0f} x {bin_size.usable_depth_mm:.0f} x "
        f"{bin_size.usable_height_mm:.0f} mm of usable space."
    )
    if group.total_count > 1:
        rationale += (
            f" Holds {group.total_count} similar items; consider a divided "
            f"bin or one bin per item if they must not touch."
        )

    return BinRecommendation(
        group_name=group.name,
        category=group.category,
        item_count=group.total_count,
        bin_label=bin_size.label,
        width_units=bin_size.width_units,
        depth_units=bin_size.depth_units,
        height_units=bin_size.height_units,
        usable_width_mm=round(bin_size.usable_width_mm, 1),
        usable_depth_mm=round(bin_size.usable_depth_mm, 1),
        usable_height_mm=round(bin_size.usable_height_mm, 1),
        fit_warning=warning,
        rationale=rationale,
    )


def recommend_all(groups: List[ItemGroup]) -> List[BinRecommendation]:
    """Recommend a bin for every group, largest footprint first."""
    recs = [recommend_bin(g) for g in groups]
    recs.sort(key=lambda r: r.width_units * r.depth_units, reverse=True)
    return recs


def pack_grid(
    grid: GridSpec, recommendations: List[BinRecommendation]
) -> GridLayout:
    """Greedily place recommended bins on the baseplate.

    Uses a simple bottom-left / row-scan placement: for each bin (largest
    first) find the first free position where its footprint fits. Bins are
    tried in their given orientation and rotated 90 degrees.
    """
    W, D = grid.width_units, grid.depth_units
    occupied = [[False] * W for _ in range(D)]
    placed: List[PlacedBin] = []
    unplaced: List[str] = []

    def fits(x: int, y: int, w: int, d: int) -> bool:
        if x + w > W or y + d > D:
            return False
        for yy in range(y, y + d):
            for xx in range(x, x + w):
                if occupied[yy][xx]:
                    return False
        return True

    def mark(x: int, y: int, w: int, d: int) -> None:
        for yy in range(y, y + d):
            for xx in range(x, x + w):
                occupied[yy][xx] = True

    for rec in recommendations:
        orientations = {
            (rec.width_units, rec.depth_units),
            (rec.depth_units, rec.width_units),
        }
        spot = None
        for y in range(D):
            for x in range(W):
                for (w, d) in orientations:
                    if fits(x, y, w, d):
                        spot = (x, y, w, d)
                        break
                if spot:
                    break
            if spot:
                break

        if spot:
            x, y, w, d = spot
            mark(x, y, w, d)
            placed.append(
                PlacedBin(
                    group_name=rec.group_name,
                    bin_label=rec.bin_label,
                    x=x,
                    y=y,
                    width_units=w,
                    depth_units=d,
                )
            )
        else:
            unplaced.append(rec.group_name)

    return GridLayout(
        grid_width_units=W,
        grid_depth_units=D,
        placed=placed,
        unplaced_groups=unplaced,
    )
