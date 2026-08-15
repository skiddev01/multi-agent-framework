"""Tests for the recommender and grid packing."""

from src.gridfinity import recommender, vision
from src.gridfinity.models import (
    BinRecommendation,
    DetectedItem,
    Dimensions,
    GridSpec,
    ItemGroup,
)


def _group(name, length, width, height, qty=1):
    return ItemGroup(
        name=name,
        category="tools",
        items=[
            DetectedItem(
                name=name,
                quantity=qty,
                dimensions=Dimensions(
                    length_mm=length, width_mm=width, height_mm=height
                ),
            )
        ],
    )


def test_recommend_bin_basic():
    rec = recommender.recommend_bin(_group("AA battery", 50, 14, 14, qty=8))
    assert rec.width_units >= 2  # 50mm needs > 1 cell
    assert rec.depth_units == 1
    assert rec.item_count == 8
    assert rec.fit_warning is None
    assert "8" in rec.rationale


def test_recommend_all_sorted_largest_first():
    groups = [
        _group("small", 20, 20, 10),
        _group("big", 200, 40, 30),
    ]
    recs = recommender.recommend_all(groups)
    first_cells = recs[0].width_units * recs[0].depth_units
    last_cells = recs[-1].width_units * recs[-1].depth_units
    assert first_cells >= last_cells


def _rec(name, w, d):
    return BinRecommendation(
        group_name=name, category="misc", item_count=1, bin_label=f"{w}x{d}x6",
        width_units=w, depth_units=d, height_units=6,
        usable_width_mm=0, usable_depth_mm=0, usable_height_mm=0,
    )


def test_pack_grid_places_bins_without_overlap():
    grid = GridSpec(width_units=4, depth_units=4)
    recs = [_rec("a", 2, 2), _rec("b", 2, 2), _rec("c", 2, 2), _rec("d", 2, 2)]
    layout = recommender.pack_grid(grid, recs)
    assert len(layout.placed) == 4
    assert not layout.unplaced_groups
    assert layout.free_cells == 0

    # No two placed bins overlap.
    seen = set()
    for p in layout.placed:
        for y in range(p.y, p.y + p.depth_units):
            for x in range(p.x, p.x + p.width_units):
                assert (x, y) not in seen
                seen.add((x, y))


def test_pack_grid_reports_unplaced_when_full():
    grid = GridSpec(width_units=2, depth_units=1)
    recs = [_rec("a", 2, 1), _rec("b", 2, 1)]
    layout = recommender.pack_grid(grid, recs)
    assert len(layout.placed) == 1
    assert layout.unplaced_groups == ["b"]


def test_pack_grid_rotates_to_fit():
    grid = GridSpec(width_units=1, depth_units=3)
    recs = [_rec("wide", 3, 1)]  # only fits rotated to 1x3
    layout = recommender.pack_grid(grid, recs)
    assert len(layout.placed) == 1
    assert layout.placed[0].width_units == 1
    assert layout.placed[0].depth_units == 3


def test_demo_groups_are_recommendable():
    groups = vision.demo_groups()
    recs = recommender.recommend_all(groups)
    assert len(recs) == len(groups)
    assert all(r.bin_label for r in recs)
