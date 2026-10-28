#!/usr/bin/env python3
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / 'runtime') not in sys.path:
    sys.path.insert(0, str(ROOT / 'runtime'))

from cbcc.delivery_export import export_delivery_package


def main() -> int:
    project = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('project')
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('dist')
    out.mkdir(parents=True, exist_ok=True)
    package_dir = out / f'{project.name}_DELIVERY'
    result = export_delivery_package(project, package_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(result['zip_path'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
