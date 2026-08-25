"""Provider Template A2UI 画廊数据集测试。"""

from __future__ import annotations

import json
from collections import Counter

from services.template_generation.engine.cardplan.preview_dataset import (
    build_template_preview_cases,
    validate_preview_asset_paths,
    write_template_preview_dataset,
)


def test_template_preview_dataset_covers_all_business_templates(tmp_path):
    manifest = write_template_preview_dataset(tmp_path)
    cases = manifest["cases"]

    assert manifest["templateCount"] == 87
    assert manifest["countsByLayout"] == {
        "Compact": 30,
        "Hero": 6,
        "Full": 35,
        "WideHero": 1,
        "WideFull": 15,
    }
    assert manifest["countsBySize"] == {"2x2": 71, "2x4": 16}
    assert len(cases) == 87
    assert len({case["templateId"] for case in cases}) == 87
    assert all((tmp_path / case["file"]).is_file() for case in cases)


def test_template_preview_a2ui_has_surface_components_and_data():
    cases = build_template_preview_cases()

    for case in cases:
        assert len(case.messages) == 3
        assert "createSurface" in case.messages[0]
        assert "updateComponents" in case.messages[1]
        assert "updateDataModel" in case.messages[2]
        components = case.messages[1]["updateComponents"]["components"]
        root = next(component for component in components if component["id"] == "root")
        assert root["component"] == "Column"
        slot = next(component for component in components if component["id"] == "root_0")
        assert slot["styles"]["height"] == case.content_height_vp


def test_template_preview_assets_are_bundled_by_genui_evaluation():
    cases = build_template_preview_cases()
    paths = validate_preview_asset_paths(cases)
    names = {path.rsplit("/", 1)[-1] for path in paths}

    assert names == {
        "battery_leaf_fill.svg",
        "calendar_fill.svg",
        "clock_fill.svg",
        "externaldrive_fill.svg",
        "figure_run.svg",
        "flame_fill.svg",
        "heart_fill.svg",
        "icon_earphone.svg",
        "icon_tiktok.png",
        "icon_weather1.svg",
        "l_circle_fill.svg",
        "location_north_up_right_fill.svg",
        "moon_z_fill_1.svg",
        "r_circle_fill.svg",
    }


def test_battery_percent_ring_hero_preview_is_neutral_skeleton_layout():
    cases = build_template_preview_cases()
    case = next(
        case for case in cases if case.template_id == "BatteryOverviewPercentRingHero@1"
    )
    components = case.messages[1]["updateComponents"]["components"]
    by_id = {component["id"]: component for component in components}

    assert by_id["root"]["styles"]["backgroundColor"] == "#FFFFFFFF"
    assert by_id["root"]["styles"]["padding"] == 12
    assert by_id["root_0"]["styles"]["height"] == 124

    hero = by_id["root_0_0"]
    assert hero["styles"]["padding"]["top"] == 8
    assert hero["styles"]["justifyContent"] == "start"
    assert hero["styles"]["alignItems"] == "center"

    ring = by_id["root_0_0_0"]
    progress = by_id["root_0_0_0_0"]
    icon = by_id["root_0_0_0_1"]
    title = by_id["root_0_0_1"]
    assert ring["styles"]["width"] == 52
    assert ring["styles"]["height"] == 52
    assert progress["styles"]["color"] == "#E6000000"
    assert progress["styles"]["backgroundColor"] == "#1A000000"
    assert progress["styles"]["width"] == 52
    assert progress["styles"]["height"] == 52
    assert icon["styles"]["width"] == 20
    assert icon["styles"]["height"] == 20
    assert icon["styles"]["fillColor"] == "#E6000000"
    assert title["styles"]["fontColor"] == "#E6000000"
    assert title["styles"]["height"] == 28


def test_template_preview_manifest_data_tiers_are_disjoint():
    cases = build_template_preview_cases()

    for case in cases:
        counts = Counter((*case.primary_data, *case.secondary_data, *case.optional_data))
        assert all(count == 1 for count in counts.values())
        assert case.primary_data
        assert json.dumps(case.messages, ensure_ascii=False)
