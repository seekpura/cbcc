#!/usr/bin/env python3
from pathlib import Path
import sys
text=Path(sys.argv[1]).read_text(encoding='utf-8').lower()
keys=['race','stp','jtbd','intersectionality','race/ethnicity','listing','photography','dynamic asset','causal iteration']
miss=[k for k in keys if k not in text]
print({'pass':not miss,'missing':miss}); sys.exit(1 if miss else 0)
