from __future__ import annotations

from pathlib import Path
import json

from cbcc.asset_compiler import compile_asset_packages
from cbcc.asset_package_full_lineage_v0671 import materialize_full_asset_lineage
from cbcc.canonical_materialization_integrity import audit_asset_directory
from cbcc.compiler import build_project


def _pack(tmp_path: Path) -> Path:
    d = tmp_path / "packs"
    d.mkdir(exist_ok=True)
    (d / "test.yaml").write_text(
        """pack_id: r0603-generic
platform_family: tiktok_shop
site: "*"
status: TEST_FIXTURE_VERIFIED
synthetic_for_test: true
capabilities: [LISTING, SEARCH, OFFER_PROMOTION, VISUAL, VIDEO, CREATOR_AFFILIATE, CX, MEASUREMENT]
surfaces: [PDP, GALLERY, PDP_VIDEO, CREATOR, FAQ]
rule_atoms: []
research_required_for: []
""",
        encoding="utf-8",
    )
    return d


def _request() -> dict:
    root = Path(__file__).resolve().parents[1]
    req = json.loads((root / "tests/fixtures/v059_category_commerce/apparel_tshirt.json").read_text(encoding="utf-8"))
    req["project_id"] = "R0603-CANONICAL-PROJECTION"
    req["planning_only"] = True
    return req


def _asset() -> dict:
    return {
        "asset_id": "AST-R0603",
        "asset_name": "Canonical projection sentinel",
        "asset_type": "IMAGE",
        "status": "ACTIVATE",
        "surface": "GALLERY",
        "family": "VISUAL",
        "consumer_question": "What is this product?",
        "strategic_job": "Resolve product identity",
        "production_mode": "GENERATIVE",
        "product_fidelity": "REFERENCE_GUIDED",
        "priority": "P0",
        "dependencies": [],
        "source_ids": ["SRC-R0603"],
        "claim_ids": [],
        "listing_reference": [],
        "success_metric": "PDP CVR",
        "visible_copy": {"headline": "ORIGINAL HEADLINE", "subline": "ORIGINAL SUBLINE"},
        "asset_art_direction": {
            "visual_carrier": "PRODUCT_HERO",
            "product_presence": {"planning_state": "REQUIRED", "presence_why": "Identity proof requires product visibility."},
            "subject": "product",
            "action": "static",
            "environment": "clean studio",
            "props": [],
            "composition": "centered hero",
            "evidence_hierarchy": ["product identity"],
            "copy_render_route": "MODEL_RENDER_INTEGRATED",
            "camera": "85mm eye-level",
            "lighting": "soft key light",
            "cmf": "warm ivory matte",
            "output": "1600x1600 sRGB",
            "culture_inclusion": "neutral",
            "truth_boundary": "no invented claims",
        },
    }


def _compiled_asset(tmp_path: Path) -> Path:
    root = tmp_path / "asset_packages"
    compile_asset_packages(
        root,
        [_asset()],
        {"name": "P"},
        {"platform_family": "tiktok_shop", "site": "MY", "market": "Malaysia"},
        {},
        {"visible_copy_locales": ["ms-MY"]},
        {"profiles": []},
        strategy_authority=None,
    )
    return root / "AST-R0603"


def test_build_project_materializes_canonical_commerce_graph_as_real_runtime_authority(tmp_path: Path):
    project = tmp_path / "project"
    build_project(project, _request(), _pack(tmp_path))
    graph_path = project / "artifacts/canonical_commerce_graph.json"
    assert graph_path.exists(), "canonical commerce graph exists as a module/test but is not consumed by build_project"
    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    assert graph.get("graph_sha256")
    roles = {row["surface"]: row["role"] for row in graph.get("projection_surfaces") or []}
    assert roles.get("JSON") == "CANONICAL_AUTHORITY"
    assert roles.get("MARKDOWN") == "PROJECTION_ONLY"
    assert roles.get("HTML") == "PROJECTION_ONLY"
    assert roles.get("MODEL_PROMPT") == "PROJECTION_ONLY"
    assert roles.get("ASSET_PACKAGE") == "PROJECTION_ONLY"


def test_visible_copy_markdown_and_visible_copy_block_cannot_diverge_under_fresh_lineage(tmp_path: Path):
    asset_dir = _compiled_asset(tmp_path)
    copy_path = asset_dir / "08_copy.md"
    copy_path.write_text(copy_path.read_text(encoding="utf-8").replace("ORIGINAL HEADLINE", "CONFLICT HEADLINE"), encoding="utf-8")
    # Re-materialize byte lineage to prove this is not merely an old hash mismatch.
    materialize_full_asset_lineage(asset_dir.parent)
    issues = audit_asset_directory(asset_dir)
    assert any(row.get("code") == "ASSET_VISIBLE_COPY_CANONICAL_DRIFT" for row in issues), issues


def test_design_card_and_prompt_contract_cannot_be_two_authorities_under_fresh_lineage(tmp_path: Path):
    asset_dir = _compiled_asset(tmp_path)
    card_path = asset_dir / "12_design_card.json"
    card = json.loads(card_path.read_text(encoding="utf-8"))
    card["visual_objective"] = "CONFLICT OBJECTIVE"
    card_path.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding="utf-8")
    materialize_full_asset_lineage(asset_dir.parent)
    issues = audit_asset_directory(asset_dir)
    assert any(row.get("code") == "ASSET_DESIGN_CARD_PROMPT_CONTRACT_DRIFT" for row in issues), issues


def test_prompt_text_and_prompt_contract_cannot_diverge_under_fresh_lineage(tmp_path: Path):
    asset_dir = _compiled_asset(tmp_path)
    prompt_path = asset_dir / "06_prompt_EN.txt"
    prompt_path.write_text("CONFLICT PROVIDER PROMPT", encoding="utf-8")
    materialize_full_asset_lineage(asset_dir.parent)
    issues = audit_asset_directory(asset_dir)
    assert any(row.get("code") == "ASSET_PROMPT_CONTRACT_TEXT_DRIFT" and row.get("field") == "prompt_en" for row in issues), issues
