"""Domain models for the Gridfinity assistant."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, computed_field


class Dimensions(BaseModel):
    """Approximate physical size of an object, in millimetres."""

    length_mm: float = Field(..., description="Longest horizontal dimension")
    width_mm: float = Field(..., description="Shorter horizontal dimension")
    height_mm: float = Field(..., description="Vertical dimension / thickness")


class DetectedItem(BaseModel):
    """A single object the vision model found in the photo."""

    name: str
    quantity: int = 1
    dimensions: Dimensions
    confidence: float = Field(0.5, ge=0.0, le=1.0)


class ItemGroup(BaseModel):
    """A set of similar objects that can share a bin type."""

    name: str
    category: str = "misc"
    items: List[DetectedItem] = Field(default_factory=list)
    notes: Optional[str] = None

    @property
    def total_count(self) -> int:
        return sum(item.quantity for item in self.items)

    def bounding_dimensions(self) -> Dimensions:
        """Largest dimension across every item in the group."""
        if not self.items:
            return Dimensions(length_mm=0, width_mm=0, height_mm=0)
        return Dimensions(
            length_mm=max(i.dimensions.length_mm for i in self.items),
            width_mm=max(i.dimensions.width_mm for i in self.items),
            height_mm=max(i.dimensions.height_mm for i in self.items),
        )


class GridSpec(BaseModel):
    """The Gridfinity baseplate the user is filling."""

    width_units: int = Field(..., ge=1, description="Grid cells across (X)")
    depth_units: int = Field(..., ge=1, description="Grid cells deep (Y)")

    @property
    def total_cells(self) -> int:
        return self.width_units * self.depth_units


class PrintableModel(BaseModel):
    """A real, printable Gridfinity model found by web research."""

    title: str
    url: str
    source: Optional[str] = None
    note: Optional[str] = None


class BinRecommendation(BaseModel):
    """The recommended bin for one group, plus supporting research."""

    group_name: str
    category: str
    item_count: int
    bin_label: str
    width_units: int
    depth_units: int
    height_units: int
    usable_width_mm: float
    usable_depth_mm: float
    usable_height_mm: float
    fit_warning: Optional[str] = None
    rationale: str = ""
    printable_models: List[PrintableModel] = Field(default_factory=list)


class PlacedBin(BaseModel):
    """A bin placed at a position on the baseplate."""

    group_name: str
    bin_label: str
    x: int
    y: int
    width_units: int
    depth_units: int


class GridLayout(BaseModel):
    """Result of packing recommended bins onto the baseplate."""

    grid_width_units: int
    grid_depth_units: int
    placed: List[PlacedBin] = Field(default_factory=list)
    unplaced_groups: List[str] = Field(default_factory=list)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def used_cells(self) -> int:
        return sum(p.width_units * p.depth_units for p in self.placed)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def free_cells(self) -> int:
        return self.grid_width_units * self.grid_depth_units - self.used_cells


class AssistantResult(BaseModel):
    """Everything the assistant produces for one photo + grid."""

    groups: List[ItemGroup] = Field(default_factory=list)
    recommendations: List[BinRecommendation] = Field(default_factory=list)
    layout: Optional[GridLayout] = None
    notes: List[str] = Field(default_factory=list)
