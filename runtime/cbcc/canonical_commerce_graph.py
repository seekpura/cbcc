from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable, Mapping
import json


GRAPH_VERSION = "cbcc-canonical-commerce-graph-v1"


@dataclass(frozen=True)
class NodeSpec:
    node_id: str
    label: str
    candidates: tuple[str, ...]
    json_pointer: str = ""
    optional: bool = False
    children: tuple[str, ...] = ()


NODE_SPECS: tuple[NodeSpec, ...] = (
    NodeSpec("PROJECT", "Project", ("../meta/request.json",)),
    NodeSpec("SOURCES", "Sources", ("evidence.json",), "/sources"),
    NodeSpec("INFORMATION_AUDIT", "Information Audit", ("strategy_authority.json",), "/sections/01_information_completeness_assumptions_decisions"),
    NodeSpec("PRODUCT_TRUTH", "Product Truth", ("product_truth_evidence_authority.json", "product_truth.json")),
    NodeSpec("RESEARCH", "Research", ("research_gate.json",)),
    NodeSpec("AUDIENCE_CULTURE", "Audience / Culture / Intersectionality", ("culture_context.json", "strategy_authority.json"), optional=True),
    NodeSpec("ECONOMICS_OFFER", "Economics / Offer", ("pricing_economics_authority.json", "economics.json"), optional=True),
    NodeSpec("STRATEGY", "Strategy", ("strategy_authority.json",)),
    NodeSpec("LISTING_SEARCH", "Listing / Search", ("listing.json", "listing_compile.json"), optional=True),
    NodeSpec("CONTENT_MATRIX", "Content Matrix", ("strategy_authority.json",), "/sections/06_platform_content_matrix", optional=True),
    NodeSpec("RACE", "RACE", ("strategy_authority.json",), "/sections/07_race_execution_table", optional=True),
    NodeSpec("CULTURE_CHECK", "Culture Check", ("strategy_authority.json",), "/sections/08_culture_adaptation_checklist", optional=True),
    NodeSpec("VISUAL_MASTER", "Visual Master", ("strategy_authority.json", "creative_contract.json"), "/sections/05_visual_photography_strategy", optional=True),
    NodeSpec("ASSET_UNIVERSE", "Asset Universe", ("asset_architecture.json", "ASSET_UNIVERSE.json"), optional=True),
    NodeSpec(
        "ASSET_EXECUTION_OBJECTS",
        "Image / Graphic / Scene / IP / Negative / Video / Creator / LIVE Objects",
        ("asset_architecture.json", "video_creator_plan.json", "creative_contract.json"),
        optional=True,
        children=("IMAGE", "GRAPHIC", "SCENE", "IP", "NEGATIVE", "VIDEO", "CREATOR", "LIVE"),
    ),
    NodeSpec("ADS", "Ads", ("ad_analysis.json", "paid_campaign_architecture.json"), optional=True),
    NodeSpec("REVIEWS", "Reviews", ("feedback_analysis.json",), optional=True),
    NodeSpec("COMPLIANCE", "Compliance", ("compliance_report.json",), optional=True),
    NodeSpec("MEASUREMENT", "Measurement", ("strategy_authority.json", "experiment_analysis.json"), "/sections/09_risk_measurement_priority_next_steps", optional=True),
    NodeSpec("OPERATIONS", "Operations", ("operator_execution_board.json",), optional=True),
    NodeSpec("PRODUCTION_REVIEW", "Production / Review", ("production_run.json", "execution_contract.json"), optional=True),
)

PROJECTION_SURFACES = ("JSON", "MARKDOWN", "HTML", "MODEL_PROMPT", "ASSET_PACKAGE")


def _sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _json_pointer_get(value: Any, pointer: str) -> Any:
    if not pointer:
        return value
    current = value
    for raw in pointer.lstrip("/").split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(current, Mapping):
            if token not in current:
                raise KeyError(pointer)
            current = current[token]
        elif isinstance(current, list):
            current = current[int(token)]
        else:
            raise KeyError(pointer)
    return current


def _resolve_authority(artifacts_dir: Path, spec: NodeSpec) -> tuple[Path | None, str | None]:
    for candidate in spec.candidates:
        path = (artifacts_dir / candidate).resolve()
        if not path.exists() or not path.is_file():
            continue
        if spec.json_pointer:
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                _json_pointer_get(payload, spec.json_pointer)
            except Exception:
                continue
        return path, candidate
    return None, None


def _node_payload(artifacts_dir: Path, spec: NodeSpec) -> dict[str, Any]:
    path, rel = _resolve_authority(artifacts_dir, spec)
    if path is None:
        return {
            "node_id": spec.node_id,
            "label": spec.label,
            "status": "TO_VERIFY" if spec.optional else "MISSING_CANONICAL_AUTHORITY",
            "why": (
                "No dedicated canonical authority object resolved for this domain; upstream must explicitly decide NOT_ACTIVE, MISSING_INPUT or provide the missing authority before downstream projection."
                if spec.optional
                else "A required canonical authority object did not resolve; downstream projections must fail closed rather than fabricate or substitute another domain object."
            ),
            "required": not spec.optional,
            "authority_ref": None,
            "authority_sha256": None,
            "json_pointer": spec.json_pointer or None,
            "children": list(spec.children),
        }
    return {
        "node_id": spec.node_id,
        "label": spec.label,
        "status": "CANONICAL_AUTHORITY_BOUND",
        "required": not spec.optional,
        "authority_ref": rel,
        "authority_sha256": _sha256(path),
        "json_pointer": spec.json_pointer or None,
        "children": list(spec.children),
    }


def _edge_payload(nodes: Iterable[Mapping[str, Any]]) -> list[dict[str, str]]:
    ordered = [str(n["node_id"]) for n in nodes]
    return [
        {"from": ordered[i], "to": ordered[i + 1], "relationship": "CANONICAL_UPSTREAM_TO_DOWNSTREAM"}
        for i in range(len(ordered) - 1)
    ]


def build_canonical_commerce_graph(artifacts_dir: Path | str) -> dict[str, Any]:
    root = Path(artifacts_dir).resolve()
    nodes = [_node_payload(root, spec) for spec in NODE_SPECS]
    required_missing = [n["node_id"] for n in nodes if n["required"] and n["status"] != "CANONICAL_AUTHORITY_BOUND"]
    graph = {
        "schema": GRAPH_VERSION,
        "status": "CANONICAL_GRAPH_READY" if not required_missing else "CANONICAL_GRAPH_INCOMPLETE",
        "authority_rule": "JSON business objects are canonical authorities; Markdown, HTML, model prompts and asset packages are projections and may not re-author conflicting business truth.",
        "canonical_payload_policy": "REFERENCE_AND_HASH_ONLY",
        "projection_surfaces": [
            {"surface": surface, "role": "CANONICAL_AUTHORITY" if surface == "JSON" else "PROJECTION_ONLY"}
            for surface in PROJECTION_SURFACES
        ],
        "node_order": [spec.node_id for spec in NODE_SPECS],
        "nodes": nodes,
        "edges": _edge_payload(nodes),
        "required_missing": required_missing,
    }
    canonical = json.dumps(graph, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    graph["graph_sha256"] = sha256(canonical).hexdigest()
    return graph


def materialize_canonical_commerce_graph(artifacts_dir: Path | str, output_path: Path | str | None = None) -> dict[str, Any]:
    root = Path(artifacts_dir).resolve()
    graph = build_canonical_commerce_graph(root)
    out = Path(output_path) if output_path else root / "canonical_commerce_graph.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(graph, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return graph
