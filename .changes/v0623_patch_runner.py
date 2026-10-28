from pathlib import Path
import runpy
p=Path('.changes/v0623_patch.py')
s=p.read_text(encoding='utf-8')
s=s.replace("else '待补中文释义')),\n        })", "else '待补中文释义'))),\n        })")
s=s.replace(",new_compile+'\\n\\ndef render_upload_center_md',s,flags=re.S)", ",lambda _m:new_compile+'\\n\\ndef render_upload_center_md',s,flags=re.S)")
s=s.replace(",new_render+'\\n\\ndef build_project_hub_md',s,flags=re.S)", ",lambda _m:new_render+'\\n\\ndef build_project_hub_md',s,flags=re.S)")
s=s.replace(",new_hub,s,flags=re.S)", ",lambda _m:new_hub,s,flags=re.S)")
s=s.replace(",new_arch+'\\n\\ndef keyword_coverage',s,flags=re.S)", ",lambda _m:new_arch+'\\n\\ndef keyword_coverage',s,flags=re.S)")
p.write_text(s,encoding='utf-8')
runpy.run_path(str(p),run_name='__main__')
