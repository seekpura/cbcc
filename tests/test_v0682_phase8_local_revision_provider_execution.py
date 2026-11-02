from __future__ import annotations

from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))

from cbcc.asset_compiler import compile_asset_packages
from cbcc.production import build_production_run, materialize_provider_jobs
from cbcc.provider_bridge import ExecutionPolicy, build_default_adapter_registry
from cbcc.provider_executor import ReferenceMemoryExecutor
from cbcc.provider_surface import ProviderExecutionSurface


def _asset() -> dict:
    return {
        "asset_id": "AST-PHASE8-REV",
        "asset_name": "Phase 8 local revision provider execution",
        "asset_type": "IMAGE",
        "status": "ACTIVATE",
        "surface": "GALLERY",
        "family": "VISUAL",
        "consumer_question": "What is this product?",
        "strategic_job": "Preserve product identity while changing only approved copy",
        "production_mode": "REAL_PRODUCT_COMPOSITE",
        "product_fidelity": "LOCKED_PIXEL",
        "priority": "P0",
        "dependencies": [],
        "source_ids": ["SRC-1"],
        "claim_ids": [],
        "listing_reference": [],
        "success_metric": "identity clarity",
    }


def _materialize_revision_envelope(tmp_path: Path) -> tuple[Path, Path, str]:
    project = tmp_path / "project"
    packages = project / "artifacts/asset_packages"
    master = tmp_path / "master.bin"
    master_bytes = b"phase8-local-revision-real-product-master"
    master.write_bytes(master_bytes)
    master_sha = hashlib.sha256(master_bytes).hexdigest()

    compile_asset_packages(
        packages,
        [_asset()],
        {"name": "P"},
        {"platform_family": "x", "site": "MY", "market": "Malaysia"},
        {"visual_implications": []},
        {"visible_copy_locales": ["en-MY"]},
        {"profiles": []},
        source_product_assets=[{
            "asset_id": "MASTER-PHASE8",
            "role": "FRONT_MASTER",
            "path": str(master),
            "sha256": master_sha,
            "ingest_status": "HASH_VERIFIED_LOCAL",
            "pixel_lock": True,
            "allowed_transforms": ["PROPORTIONAL_SCALE", "PLACEMENT", "MASK_OR_CROP", "COMPOSITE"],
            "identity_features": ["logo", "packaging_print", "color", "geometry", "proportions"],
        }],
    )

    revision_id = "LR-PHASE8-EXECUTION"
    revision_scope = {
        "asset_id": "AST-PHASE8-REV",
        "allowed_fields": ["headline"],
        "allowed_layers": ["typography_copy"],
        "requested_change": "tighten the headline only",
        "revision_request_id": "LRQ-PHASE8-EXECUTION",
    }
    run = build_production_run(
        packages,
        provider_preferences={"REAL_PRODUCT_COMPOSITE": "EPV_ADAPTER"},
        requested_asset_ids=["AST-PHASE8-REV"],
        revision_scope=revision_scope,
    )
    revision_root = project / "artifacts/local_revisions" / revision_id
    jobs_root = revision_root / "provider_jobs"
    index = materialize_provider_jobs(packages, run, jobs_root)
    assert index["job_count"] == 1
    run["provider_jobs"] = index
    run["revision_id"] = revision_id
    run["revision_request_id"] = "LRQ-PHASE8-EXECUTION"
    revision_root.mkdir(parents=True, exist_ok=True)
    (revision_root / "production_run.json").write_text(
        json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return project, jobs_root, revision_id


def _callbacks(reference: ReferenceMemoryExecutor) -> dict:
    return {
        "ensure_asset": reference.ensure_asset,
        "submit": reference.submit,
        "poll": reference.poll,
        "collect": reference.collect,
        "resolve": reference.resolve,
    }


def test_local_revision_jobs_execute_through_same_provider_surface(tmp_path: Path):
    project, jobs_root, revision_id = _materialize_revision_envelope(tmp_path)
    reference = ReferenceMemoryExecutor(poll_sequence=("COMPLETED",))
    registry = build_default_adapter_registry()

    def resolver(adapter_id, job_dir, job):
        assert adapter_id == "EPV_HOST_CALLBACK_V1"
        return {"callbacks": _callbacks(reference), "api_key": "phase8-test-secret"}

    surface = ProviderExecutionSurface(registry, context_resolver=resolver)
    out = surface.execute_local_revision(
        project,
        revision_id,
        adapter_id="EPV_HOST_CALLBACK_V1",
        policy=ExecutionPolicy(max_attempts=2, max_polls_per_attempt=2),
    )

    assert out["status"] == "LOCAL_REVISION_PROVIDER_EXECUTION_COMPLETE"
    assert out["revision_id"] == revision_id
    assert out["jobs"][0]["status"] == "COMPLETE"
    assert (jobs_root / "AST-PHASE8-REV/result.json").exists()
    # Revision execution must not pretend that the root provider job surface handled this envelope.
    assert not (project / "artifacts/provider_jobs/AST-PHASE8-REV/result.json").exists()
