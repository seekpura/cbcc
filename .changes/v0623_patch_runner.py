from pathlib import Path
import runpy
p=Path('.changes/v0623_patch.py')
s=p.read_text(encoding='utf-8')
s=s.replace("else '待补中文释义')),\n        })", "else '待补中文释义'))),\n        })")
p.write_text(s,encoding='utf-8')
runpy.run_path(str(p),run_name='__main__')
