"""Tests for the Gridfinity spec math."""

from src.gridfinity import spec


def test_grid_constants():
    assert spec.GRID_UNIT_MM == 42.0
    assert spec.HEIGHT_UNIT_MM == 7.0


def test_usable_footprint_grows_with_cells():
    one = spec.usable_footprint_mm(1)
    two = spec.usable_footprint_mm(2)
    assert two > one
    # Roughly one extra cell of usable width.
    assert abs((two - one) - spec.GRID_UNIT_MM) < 0.01


def test_footprint_units_for_small_object_is_one_cell():
    assert spec.footprint_units_for(20) == 1


def test_footprint_units_for_long_object_spans_multiple_cells():
    # A 180mm screwdriver cannot fit one 42mm cell.
    assert spec.footprint_units_for(180) >= 5


def test_height_units_for_returns_standard_value():
    units = spec.height_units_for(25)
    assert units in spec.STANDARD_HEIGHT_UNITS
    assert spec.usable_depth_mm(units) >= 25


def test_fit_bin_orients_long_side_to_width():
    bin_size = spec.fit_bin(length_mm=180, width_mm=25, height_mm=25)
    assert bin_size.width_units >= bin_size.depth_units
    assert bin_size.width_units >= 5
    assert bin_size.depth_units == 1


def test_describe_fit_none_when_it_fits():
    bin_size = spec.fit_bin(50, 14, 14)
    assert spec.describe_fit(bin_size, 50, 14, 14) is None


def test_describe_fit_warns_when_too_tall():
    small = spec.BinSize(width_units=1, depth_units=1, height_units=2)
    warning = spec.describe_fit(small, 10, 10, 500)
    assert warning is not None
    assert "height" in warning


def test_bin_size_label_and_cells():
    bin_size = spec.BinSize(width_units=2, depth_units=1, height_units=6)
    assert bin_size.label == "2x1x6"
    assert bin_size.cells == 2
    assert bin_size.outer_width_mm == 84.0
    assert bin_size.outer_height_mm == 42.0
