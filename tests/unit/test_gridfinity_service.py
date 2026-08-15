"""Tests for the orchestration service and web API (offline / demo path)."""

from src.gridfinity import service
from src.gridfinity.models import GridSpec


def test_plan_without_image_uses_demo(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    grid = GridSpec(width_units=5, depth_units=4)
    result = service.plan(grid=grid, image_bytes=None, do_research=True)

    assert result.groups  # demo groups
    assert result.recommendations
    assert result.layout is not None
    assert any("demo" in n.lower() for n in result.notes)
    # Research fell back to generic links, each rec has models.
    assert all(r.printable_models for r in result.recommendations)


def test_plan_research_disabled_has_no_models(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    grid = GridSpec(width_units=5, depth_units=4)
    result = service.plan(grid=grid, image_bytes=None, do_research=False)
    assert all(not r.printable_models for r in result.recommendations)


def test_plan_notes_unplaced_on_tiny_grid(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    grid = GridSpec(width_units=1, depth_units=1)
    result = service.plan(grid=grid, image_bytes=None, do_research=False)
    # Demo has a 180mm screwdriver that cannot fit a 1x1 grid.
    assert result.layout.unplaced_groups
    assert any("did not fit" in n for n in result.notes)


def test_web_api_health_and_plan(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    from fastapi.testclient import TestClient
    from src.gridfinity.web.app import app

    client = TestClient(app)

    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.json()["vision_enabled"] is False

    resp = client.post(
        "/api/plan",
        data={"width_units": 5, "depth_units": 4, "research": "false"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["recommendations"]
    assert body["layout"]["grid_width_units"] == 5


def test_web_api_rejects_bad_grid(monkeypatch):
    from fastapi.testclient import TestClient
    from src.gridfinity.web.app import app

    client = TestClient(app)
    resp = client.post(
        "/api/plan", data={"width_units": 0, "depth_units": 4}
    )
    assert resp.status_code == 400
