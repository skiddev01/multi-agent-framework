"""Research agent: find real, printable Gridfinity models for each group.

Uses Claude's server-side ``web_search`` tool to look up existing models on
Printables, Thingiverse, MakerWorld and gridfinity.xyz. When no API key is
available it falls back to constructing useful search-and-generator links so
the recommendation is still actionable offline.
"""

from __future__ import annotations

import os
from urllib.parse import quote_plus
from typing import List, Optional

from .models import BinRecommendation, PrintableModel

DEFAULT_RESEARCH_MODEL = os.getenv(
    "GRIDFINITY_RESEARCH_MODEL", "claude-opus-4-20250514"
)


class ResearchUnavailable(RuntimeError):
    """Raised when a real research call cannot be made."""


def _fallback_links(rec: BinRecommendation) -> List[PrintableModel]:
    """Deterministic, useful links when live search is unavailable."""
    query = quote_plus(f"gridfinity {rec.category} {rec.group_name}")
    return [
        PrintableModel(
            title=f"Generate a custom {rec.bin_label} bin (gridfinity.xyz)",
            url="https://gridfinity.xyz/tools/",
            source="gridfinity.xyz",
            note="Parametric generator — enter the exact footprint and height.",
        ),
        PrintableModel(
            title=f"Search Printables for '{rec.group_name}' bins",
            url=f"https://www.printables.com/search/models?q={query}",
            source="Printables",
            note="Community models that may already fit this group.",
        ),
        PrintableModel(
            title=f"Search MakerWorld for '{rec.group_name}' bins",
            url=f"https://makerworld.com/en/search/models?keyword={query}",
            source="MakerWorld",
        ),
        PrintableModel(
            title=f"Search Thingiverse for '{rec.group_name}' bins",
            url=f"https://www.thingiverse.com/search?q={query}",
            source="Thingiverse",
        ),
    ]


def _research_prompt(rec: BinRecommendation) -> str:
    return (
        "Find up to 3 existing, printable Gridfinity models suited to storing "
        f"'{rec.group_name}' ({rec.category}, roughly a {rec.bin_label} bin). "
        "Prefer Printables, MakerWorld, Thingiverse or gridfinity.xyz. For each "
        "result give the title and the direct URL. Answer as a short bulleted "
        "list of 'Title - URL'. If nothing specific exists, suggest a "
        "parametric generator link instead."
    )


def _parse_link_lines(text: str, source_hint: str = "web") -> List[PrintableModel]:
    models: List[PrintableModel] = []
    for raw in text.splitlines():
        line = raw.strip().lstrip("-*0123456789. ").strip()
        if "http" not in line:
            continue
        idx = line.find("http")
        url = line[idx:].split()[0].rstrip(").,")
        title = line[:idx].rstrip(" -–—:").strip() or url
        models.append(PrintableModel(title=title, url=url, source=source_hint))
        if len(models) >= 3:
            break
    return models


def research_models(
    rec: BinRecommendation,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> List[PrintableModel]:
    """Search the web for printable models matching one recommendation."""
    key = api_key or os.getenv("ANTHROPIC_API_KEY")
    if not key or key.startswith("your_"):
        raise ResearchUnavailable("ANTHROPIC_API_KEY is not configured")

    try:
        import anthropic
    except ImportError as exc:  # pragma: no cover - env dependent
        raise ResearchUnavailable("anthropic package is not installed") from exc

    client = anthropic.Anthropic(api_key=key)
    message = client.messages.create(
        model=model or DEFAULT_RESEARCH_MODEL,
        max_tokens=1024,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 3}],
        messages=[{"role": "user", "content": _research_prompt(rec)}],
    )
    text = "".join(
        block.text for block in message.content if block.type == "text"
    )
    models = _parse_link_lines(text)
    return models or _fallback_links(rec)[:2]


def research_or_fallback(
    rec: BinRecommendation, api_key: Optional[str] = None
) -> List[PrintableModel]:
    """Best-effort research: live search, else deterministic fallback links."""
    try:
        return research_models(rec, api_key=api_key)
    except (ResearchUnavailable, Exception):  # noqa: BLE001 - degrade gracefully
        return _fallback_links(rec)
