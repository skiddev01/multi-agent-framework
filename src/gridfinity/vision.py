"""Vision agent: identify and group objects in an uploaded photo.

Uses Anthropic Claude's vision capability to detect objects, estimate their
physical size, and group similar items. If no ``ANTHROPIC_API_KEY`` is set (or
the ``anthropic`` package is missing), it falls back to a deterministic demo
grouping so the app and tests still run offline.
"""

from __future__ import annotations

import base64
import json
import os
from typing import List, Optional

from .models import DetectedItem, Dimensions, ItemGroup

DEFAULT_VISION_MODEL = os.getenv("GRIDFINITY_VISION_MODEL", "claude-opus-4-20250514")

_SYSTEM_PROMPT = """\
You are a vision assistant for a Gridfinity storage planner. You are given a \
photo of small objects a user wants to store. Identify the distinct objects, \
estimate each object's real physical size in millimetres (length x width x \
height), and group similar objects together (e.g. all screwdrivers, all AA \
batteries). Use everyday reference objects in the photo for scale when you can.

Respond with ONLY a JSON object, no prose, matching exactly this schema:
{
  "groups": [
    {
      "name": "short group name",
      "category": "one of: tools, fasteners, electronics, stationery, \
crafts, kitchen, gaming, misc",
      "notes": "optional short note about scale assumptions",
      "items": [
        {
          "name": "object name",
          "quantity": 1,
          "length_mm": 100, "width_mm": 20, "height_mm": 20,
          "confidence": 0.0-1.0
        }
      ]
    }
  ]
}
Estimate conservatively but realistically. If unsure of scale, say so in notes."""


class VisionUnavailable(RuntimeError):
    """Raised when a real vision call is requested but cannot be made."""


def _parse_groups(payload: dict) -> List[ItemGroup]:
    groups: List[ItemGroup] = []
    for g in payload.get("groups", []):
        items: List[DetectedItem] = []
        for it in g.get("items", []):
            items.append(
                DetectedItem(
                    name=str(it.get("name", "item")),
                    quantity=int(it.get("quantity", 1) or 1),
                    dimensions=Dimensions(
                        length_mm=float(it.get("length_mm", 0) or 0),
                        width_mm=float(it.get("width_mm", 0) or 0),
                        height_mm=float(it.get("height_mm", 0) or 0),
                    ),
                    confidence=float(it.get("confidence", 0.5) or 0.5),
                )
            )
        if not items:
            continue
        groups.append(
            ItemGroup(
                name=str(g.get("name", "Group")),
                category=str(g.get("category", "misc")),
                items=items,
                notes=g.get("notes"),
            )
        )
    return groups


def _extract_json(text: str) -> dict:
    """Pull the first JSON object out of a model response."""
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("no JSON object found in vision response")
    return json.loads(text[start : end + 1])


def analyze_image(
    image_bytes: bytes,
    media_type: str = "image/jpeg",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> List[ItemGroup]:
    """Analyze a photo with Claude and return grouped, sized items."""
    key = api_key or os.getenv("ANTHROPIC_API_KEY")
    if not key or key.startswith("your_"):
        raise VisionUnavailable("ANTHROPIC_API_KEY is not configured")

    try:
        import anthropic
    except ImportError as exc:  # pragma: no cover - env dependent
        raise VisionUnavailable("anthropic package is not installed") from exc

    client = anthropic.Anthropic(api_key=key)
    b64 = base64.standard_b64encode(image_bytes).decode("ascii")
    message = client.messages.create(
        model=model or DEFAULT_VISION_MODEL,
        max_tokens=2000,
        system=_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": "Identify, size, and group the objects in "
                        "this photo. Return only the JSON.",
                    },
                ],
            }
        ],
    )
    text = "".join(
        block.text for block in message.content if block.type == "text"
    )
    return _parse_groups(_extract_json(text))


def demo_groups() -> List[ItemGroup]:
    """Deterministic sample used when no API key is available."""
    return [
        ItemGroup(
            name="Screwdrivers",
            category="tools",
            notes="Demo data (no ANTHROPIC_API_KEY set).",
            items=[
                DetectedItem(
                    name="Phillips screwdriver",
                    quantity=3,
                    dimensions=Dimensions(
                        length_mm=180, width_mm=25, height_mm=25
                    ),
                    confidence=0.6,
                )
            ],
        ),
        ItemGroup(
            name="AA batteries",
            category="electronics",
            notes="Demo data.",
            items=[
                DetectedItem(
                    name="AA battery",
                    quantity=8,
                    dimensions=Dimensions(
                        length_mm=50, width_mm=14, height_mm=14
                    ),
                    confidence=0.7,
                )
            ],
        ),
        ItemGroup(
            name="M3 screws",
            category="fasteners",
            notes="Demo data.",
            items=[
                DetectedItem(
                    name="M3 screw",
                    quantity=40,
                    dimensions=Dimensions(
                        length_mm=16, width_mm=6, height_mm=6
                    ),
                    confidence=0.5,
                )
            ],
        ),
    ]
