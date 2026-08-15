"""Gridfinity specification and bin-sizing math.

Gridfinity is a modular storage standard by Zack Freedman. The core numbers:

* The grid is built from **42 mm x 42 mm** cells ("units", ``u``).
* Bin footprints are whole numbers of cells, e.g. a ``2 x 1`` bin.
* Bin height is expressed in **7 mm** "height units" (``h``). A ``6h`` bin is
  ``6 * 7 = 42 mm`` tall on the outside.

The exact interior a printed bin gives you depends on wall thickness, the
stacking lip and the base, so the usable dimensions below are deliberately
*conservative* heuristics. They are intentionally easy to tune from one place.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

# --- Core standard constants (do not change; these define the standard) -------

#: Size of a single grid cell, in millimetres.
GRID_UNIT_MM: float = 42.0

#: Height increment, in millimetres. Bin heights are whole multiples of this.
HEIGHT_UNIT_MM: float = 7.0

# --- Conservative usable-space heuristics (safe to tune) ----------------------

#: Total mm lost across a footprint dimension to walls + print clearance.
#: Applied once per footprint dimension (not per cell).
_FOOTPRINT_LOSS_MM: float = 8.0

#: mm of interior depth lost to the base + stacking lip of a bin.
_DEPTH_LOSS_MM: float = 6.4

#: Standard height units that are commonly available / printed.
STANDARD_HEIGHT_UNITS: List[int] = [2, 3, 4, 5, 6, 7, 8, 9, 10, 12]

#: Largest footprint (in cells) we will ever recommend for a single bin.
MAX_FOOTPRINT_UNITS: int = 6


@dataclass(frozen=True)
class BinSize:
    """A concrete Gridfinity bin size and its usable interior."""

    width_units: int
    depth_units: int
    height_units: int

    @property
    def label(self) -> str:
        """Human label, e.g. ``2x1x6``."""
        return f"{self.width_units}x{self.depth_units}x{self.height_units}"

    @property
    def outer_width_mm(self) -> float:
        return self.width_units * GRID_UNIT_MM

    @property
    def outer_depth_mm(self) -> float:
        return self.depth_units * GRID_UNIT_MM

    @property
    def outer_height_mm(self) -> float:
        return self.height_units * HEIGHT_UNIT_MM

    @property
    def usable_width_mm(self) -> float:
        return usable_footprint_mm(self.width_units)

    @property
    def usable_depth_mm(self) -> float:
        return usable_footprint_mm(self.depth_units)

    @property
    def usable_height_mm(self) -> float:
        return usable_depth_mm(self.height_units)

    @property
    def cells(self) -> int:
        return self.width_units * self.depth_units


def usable_footprint_mm(units: int) -> float:
    """Conservative usable interior length across ``units`` grid cells."""
    return max(0.0, units * GRID_UNIT_MM - _FOOTPRINT_LOSS_MM)


def usable_depth_mm(height_units: int) -> float:
    """Conservative usable interior depth of a bin ``height_units`` tall."""
    return max(0.0, height_units * HEIGHT_UNIT_MM - _DEPTH_LOSS_MM)


def footprint_units_for(length_mm: float) -> int:
    """Smallest number of grid cells whose usable interior fits ``length_mm``."""
    units = 1
    while usable_footprint_mm(units) < length_mm and units < MAX_FOOTPRINT_UNITS:
        units += 1
    return units


def height_units_for(height_mm: float) -> int:
    """Smallest standard height (in 7 mm units) whose interior fits ``height_mm``."""
    for units in STANDARD_HEIGHT_UNITS:
        if usable_depth_mm(units) >= height_mm:
            return units
    return STANDARD_HEIGHT_UNITS[-1]


def fit_bin(
    length_mm: float,
    width_mm: float,
    height_mm: float,
) -> BinSize:
    """Return the smallest standard :class:`BinSize` that fits one object.

    The object's longest horizontal side is aligned to the bin's wider
    footprint dimension so we do not waste a cell to orientation.
    """
    long_side, short_side = sorted((length_mm, width_mm), reverse=True)
    width_units = footprint_units_for(long_side)
    depth_units = footprint_units_for(short_side)
    height_units = height_units_for(height_mm)
    return BinSize(
        width_units=width_units,
        depth_units=depth_units,
        height_units=height_units,
    )


def describe_fit(bin_size: BinSize, length_mm: float, width_mm: float,
                 height_mm: float) -> Optional[str]:
    """Warn if an object does not actually fit the given bin, else ``None``."""
    long_side, short_side = sorted((length_mm, width_mm), reverse=True)
    problems = []
    if long_side > bin_size.usable_width_mm:
        problems.append(
            f"length {long_side:.0f}mm exceeds usable "
            f"{bin_size.usable_width_mm:.0f}mm"
        )
    if short_side > bin_size.usable_depth_mm:
        problems.append(
            f"width {short_side:.0f}mm exceeds usable "
            f"{bin_size.usable_depth_mm:.0f}mm"
        )
    if height_mm > bin_size.usable_height_mm:
        problems.append(
            f"height {height_mm:.0f}mm exceeds usable "
            f"{bin_size.usable_height_mm:.0f}mm"
        )
    return "; ".join(problems) if problems else None
