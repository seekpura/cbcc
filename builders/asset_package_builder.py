#!/usr/bin/env python3
from pathlib import Path
import sys, json, shutil, zipfile, hashlib

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("project")
dist = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("dist")
dist.mkdir(parents=True, exist_ok=True)

required = [
    "source_registry.json",
    "product_facts.json",
    "claim_ledger.json",
    "master_asset_map.json",
]
missing = [x for x in required if not (src / x).exists()]
if missing:
    raise SystemExit("BLOCKED missing required files: " + ", ".join(missing))

package = dist / (src.name + "_ASSET_PACKAGE")
if package.exists():
    shutil.rmtree(package)
package.mkdir()

for name in required:
    shutil.copy2(src / name, package / name)

for optional in ["listing.json","visual_strategy.json","CURRENT_HANDOFF.md","qa_report.md"]:
    p = src / optional
    if p.exists():
        shutil.copy2(p, package / optional)

assets = src / "assets"
if assets.exists():
    shutil.copytree(assets, package / "assets")

manifest = {"files":[]}
for p in sorted(package.rglob("*")):
    if p.is_file():
        manifest["files"].append({
            "path": str(p.relative_to(package)),
            "sha256": sha256(p),
            "bytes": p.stat().st_size
        })
(package / "PACKAGE_MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

zip_path = dist / (package.name + ".zip")
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for p in package.rglob("*"):
        if p.is_file():
            z.write(p, p.relative_to(package.parent))

print(zip_path)
