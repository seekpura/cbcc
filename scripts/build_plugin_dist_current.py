#!/usr/bin/env python3
from __future__ import annotations

# CURRENT_BUILDER_TARGET must match the semantic release family in ../VERSION.
CURRENT_BUILDER_TARGET = '0.6.72'

from scripts.build_plugin_dist_v0672 import build, main  # noqa: E402,F401


if __name__ == '__main__':
    raise SystemExit(main())
