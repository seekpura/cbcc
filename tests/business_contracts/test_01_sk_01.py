"""SK-01: real consumer counterfactuals for host-authored input.

These tests cover input -> downstream behavior, not a live LLM's ability to author
the plan or autonomously invoke a second compile. Keep those claims separate.
The synthetic product is created inside this test only.
"""
from __future__ import annotations

import copy
import json

from runtime.cbcc.agent_autonomy import compile_agent_autonomy_plan
from runtime.cbcc.compiler import build_project


PRODUCT = {
    "name": "Fixture C01 cable guide",
    "category": "home organization",
    "material": "silicone (synthetic test fact)",
    "package_contents": "one cable guide (synthetic test fact)",
}
QUESTION = "What needs to be understood before choosing this cable guide?"
FIT_COMPOSITION = (
    "side-profile desk-edge interface paired with a top-down groove view; "
    "no invented dimension labels"
)
TENSION_COMPOSITION = (
    "loose cable paths cross an uncluttered desk edge; "
    "no product silhouette or branded packshot"
)
LOCAL_REVISION_COMPOSITION = (
    "tight cropped cable-path diagram; preserve empty margin for later copy assembly"
)


def _pack(tmp_path):
    packs = tmp_path / "packs"
    packs.mkdir()
    (packs / "test.yaml").write_text(
        "pack_id: sk01-test\n"
        "platform_family: sk01_test_platform\n"
        'site: "*"\n'
        "status: TEST_FIXTURE_VERIFIED\n"
        "synthetic_for_test: true\n"
        "capabilities: [LISTING, SEARCH, VISUAL, VIDEO, PAID, MEASUREMENT, COMPLIANCE]\n"
        "surfaces: [GALLERY, PDP, PDP_VIDEO, PAID_AD]\n"
        "rule_atoms: []\n"
        "research_required_for: []\n",
        encoding="utf-8",
    )
    return packs


def _direction(composition, *, presence, visual_carrier, why):
    return {
        "consumer_question": QUESTION,
        "visual_carrier": visual_carrier,
        "visual_carrier_why": why,
        "subject": (
            "test cable guide physically at a desk edge"
            if presence == "REQUIRED" else
            "an everyday desk edge and loose cables, deliberately without a product"
        ),
        "decisive_moment": (
            "the cable approaches the guide groove" if presence == "REQUIRED"
            else "the scattered cable lines become the first visual question"
        ),
        "composition_grammar": composition,
        "evidence_plane": "synthetic product facts only; no unverified performance evidence",
        "negative_space": "controlled information hierarchy rather than an empty template",
        "product_presence": {
            "planning_state": presence,
            "product_role": "HERO" if presence == "REQUIRED" else "ABSENT",
            "source_reference_role": "TRUTH_REFERENCE_ONLY",
            "presence_why": why,
        },
    }


def _request(project_id, *, market, locale, scope, goal, why, chosen, rejected,
             composition, presence, carrier, budget):
    art = _direction(composition, presence=presence, visual_carrier=carrier, why=why)
    return {
        "project_id": project_id,
        "sku": "C01",
        "scope_mode": scope,
        "planning_only": True,
        "compile_assets": True,
        "product": copy.deepcopy(PRODUCT),
        "sources": [{"source_id": "SRC-C01", "kind": "PRODUCT_TRUTH",
                     "description": "Synthetic, test-scoped product facts only"}],
        "assumptions": [
            "Fixture only: no verified market share, platform performance, sales or local legal assertion."
        ],
        "goal": goal,
        "budget": budget,
        "target": {
            "target_id": "T-SK01",
            "market": market,
            "jurisdiction": market,
            "platform_family": "sk01_test_platform",
            "site": "TEST",
            "primary_locale": locale,
            "visible_copy_locales": [locale],
            "delivery_locale": "zh-CN",
            "surfaces": ["GALLERY"],
        },
        "content_families": ["VISUAL"],
        "shopper_questions": [QUESTION],
        "asset_jobs": [{
            "family": "VISUAL",
            "surface": "GALLERY",
            "consumer_question": QUESTION,
            "decision_intent": "DECISION_SUPPORT",
            "strategic_job": "Resolve the specific choice barrier in the goal",
            "reason_to_exist": why,
            "production_mode": "GRAPHIC_DESIGN",
        }],
        "agent_plan": {
            "decision_trace": [{
                "goal": goal,
                "chosen_route": chosen,
                "rejected_route": rejected,
                "why": why,
                "evidence_boundary": "Only supplied synthetic product facts; no market-effect claims",
                "resource_tradeoff": budget,
            }],
            "research_requirements": [],
            "content_scope": {"families": ["VISUAL"]},
            "creative_exploration": {
                "portfolio_curation": {"portfolio_thesis": chosen},
                "asset_art_directions": [art],
            },
            "iteration_policy": {"stop": False},
        },
    }


def _artifact(folder, name):
    return json.loads((folder / "artifacts" / name).read_text(encoding="utf-8"))


def test_missing_host_plan_is_fallback_not_agent_authoring():
    request = _request(
        "sk01-fallback", market="US", locale="en-US", scope="FULL",
        goal="Explain product fit without unsupported dimensions",
        why="The buyer must inspect the real physical interface",
        chosen="physical fit interface", rejected="unproven performance badge",
        composition=FIT_COMPOSITION, presence="REQUIRED",
        carrier="FUNCTIONAL_INTERFACE_VIEW", budget="one still asset",
    )
    request.pop("agent_plan")
    compiled = compile_agent_autonomy_plan(request)
    assert compiled["status"] == "AUTONOMY_FALLBACK_READY"
    assert compiled["host_agent_trace"] == []
    assert (compiled["research"]["authority"] != "HOST_AGENT_AUTHORED")


def test_two_full_goals_change_actual_asset_and_prompt_consumers_without_changing_product_truth(tmp_path):
    packs = _pack(tmp_path)
    fit = _request(
        "sk01-fit", market="United States", locale="en-US", scope="FULL",
        goal="Conversion: resolve physical placement doubt with one low-cost informational image",
        why="An actual product-to-desk relationship is more actionable than a stylish desk mood",
        chosen="functional interface proof", rejected="atmospheric desk awareness",
        composition=FIT_COMPOSITION, presence="REQUIRED",
        carrier="FUNCTIONAL_INTERFACE_VIEW", budget="P0 one still, no paid creator shoot",
    )
    tension = _request(
        "sk01-awareness", market="Malaysia", locale="en-MY", scope="FULL",
        goal="Reach: depict the pre-solution desk annoyance, not a fabricated product effect",
        why="A recognizable visual problem is more suited to this awareness job than premature pack-detail",
        chosen="problem-context visual", rejected="functional product close-up",
        composition=TENSION_COMPOSITION, presence="FORBIDDEN",
        carrier="ENVIRONMENTAL_TENSION_STILL", budget="P0 one context still, no model, no video",
    )
    first = tmp_path / "fit"
    second = tmp_path / "tension"
    build_project(first, fit, packs)
    build_project(second, tension, packs)
    fa = _artifact(first, "asset_architecture.json")
    ta = _artifact(second, "asset_architecture.json")
    assert fa["asset_count"] == ta["asset_count"] == 1
    af, at = fa["assets"][0], ta["assets"][0]
    assert af["art_direction_status"] == at["art_direction_status"] == "AUTHORED"
    assert af["asset_art_direction"]["composition_grammar"] == FIT_COMPOSITION
    assert at["asset_art_direction"]["composition_grammar"] == TENSION_COMPOSITION
    assert af["product_presence"]["planning_state"] == "REQUIRED"
    assert at["product_presence"]["planning_state"] == "FORBIDDEN"
    assert af["creative_brief"]["composition"] != at["creative_brief"]["composition"]
    assert _artifact(first, "product_truth.json")["product"] == _artifact(second, "product_truth.json")["product"]
    assert _artifact(first, "target_context.json")["market"] != _artifact(second, "target_context.json")["market"]

    for folder, expected in [(first, FIT_COMPOSITION), (second, TENSION_COMPOSITION)]:
        plan = _artifact(folder, "agent_autonomy_plan.json")
        assert plan["status"] == "AGENT_AUTHORED"
        assert plan["host_agent_trace"][0]["why"]
        assert plan["creative_exploration"]["asset_art_directions"][0]["composition_grammar"] == expected
        next_action = _artifact(folder, "agent_next_action.json")
        assert "recommended_next_action" in next_action
        package = folder / "artifacts" / "asset_packages" / _artifact(folder, "asset_architecture.json")["assets"][0]["asset_id"]
        prompt_contract = json.loads((package / "13_prompt_contract.json").read_text(encoding="utf-8"))
        assert "product_presence" in prompt_contract["design_card"], prompt_contract.get("prompt_consumption_audit")
    tension_pkg = second / "artifacts" / "asset_packages" / at["asset_id"]
    tension_prompt = (tension_pkg / "06_prompt_EN.txt").read_text(encoding="utf-8")
    assert "Product is intentionally absent in this asset." in tension_prompt


def test_task_scoped_one_image_does_not_become_full_campaign(tmp_path):
    request = _request(
        "sk01-scoped", market="US", locale="en-US", scope="TASK_SCOPED",
        goal="Revise only the layout of one existing graphic asset",
        why="The user asked for one local composition change, not new market strategy or media",
        chosen="localized crop and copy-safe margin", rejected="full campaign re-curation",
        composition=LOCAL_REVISION_COMPOSITION, presence="FORBIDDEN",
        carrier="INFORMATION_GRAPHIC", budget="one existing asset revision",
    )
    request["compile_assets"] = False
    folder = tmp_path / "scoped"
    build_project(folder, request, _pack(tmp_path))
    arch = _artifact(folder, "asset_architecture.json")
    assert arch["asset_count"] == 1
    assert arch["assets"][0]["asset_art_direction"]["composition_grammar"] == LOCAL_REVISION_COMPOSITION
    plan = _artifact(folder, "agent_autonomy_plan.json")
    assert plan["content_scope"]["families"] == ["VISUAL"]
    assert plan["host_agent_trace"][0]["rejected_route"] == "full campaign re-curation"
    assert _artifact(folder, "asset_compile.json")["status"] == "NOT_REQUESTED"
    assert _artifact(folder, "product_truth.json")["product"] == PRODUCT
