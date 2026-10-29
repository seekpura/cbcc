#!/usr/bin/env python3
from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

HOST_REQUIRED = [
    'Host-Native FULL Delivery Anti-Regression Authority',
    'FULL 项目深度合同',
    'Agent Creative Authority',
    'Production Parameter Closure',
    'Model-Native Prompt',
    'Design Card',
    'Model Prompt CN',
    'Model Prompt EN',
    'Visible Copy',
    'Production / Assembly Notes',
]
CANONICAL_REQUIRED = [
    'Autonomous Integrated Render + Operator Density Authority',
    'Seven First-Class Commerce Tools',
    'Reference-Guided Native Product',
    'Production Parameter Closure',
    'Agent Creative Authority',
    'Model-Native Prompt + Human Depth Authority',
    'Host-Native FULL Delivery Anti-Regression Authority',
]


def _read(zf: zipfile.ZipFile, suffix: str) -> str:
    matches = [n for n in zf.namelist() if n.endswith(suffix)]
    if len(matches) != 1:
        raise AssertionError(f'expected one {suffix}, got {matches}')
    return zf.read(matches[0]).decode('utf-8')


def check(plugin_zip: Path) -> None:
    with zipfile.ZipFile(plugin_zip) as zf:
        host = _read(zf, '/skills/cross-border-commerce-creative/SKILL.md')
        canonical = _read(zf, '/skills/cross-border-commerce-creative/resources/SKILL.md')
        manifest = _read(zf, '/plugin.json')
    host_bytes = len(host.encode('utf-8'))
    canonical_bytes = len(canonical.encode('utf-8'))
    if host_bytes < 12000:
        raise AssertionError(f'host Skill authority regression: only {host_bytes} bytes')
    if canonical_bytes < 70000:
        raise AssertionError(f'canonical Skill authority regression: only {canonical_bytes} bytes')
    for phrase in HOST_REQUIRED:
        if phrase not in host:
            raise AssertionError(f'host Skill missing required authority: {phrase}')
    for phrase in CANONICAL_REQUIRED:
        if phrase not in canonical:
            raise AssertionError(f'canonical Skill missing required authority: {phrase}')
    if '"version": "0.6.38"' not in manifest:
        raise AssertionError('plugin manifest is not v0.6.38')
    if 'v0.6.38 最高权威' not in manifest:
        raise AssertionError('manifest defaultPrompt does not activate host anti-regression authority')
    print(f'PASS host={host_bytes} canonical={canonical_bytes} plugin={plugin_zip.name}')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('plugin_zip', type=Path)
    args = ap.parse_args()
    check(args.plugin_zip)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
