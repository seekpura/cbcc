from pathlib import Path
import runpy
p=Path('.changes/v0624_patch.py')
lines=p.read_text(encoding='utf-8').splitlines()
start=next(i for i,line in enumerate(lines) if "(pack/'test.yaml').write_text(" in line)
end=next(i for i in range(start+1,len(lines)) if lines[i].strip()=="''\"''')")
yaml="pack_id: test\nplatform_family: test_platform\nsite: \"*\"\nstatus: TEST_FIXTURE_VERIFIED\nsynthetic_for_test: true\ncapabilities: [LISTING, SEARCH, VISUAL, VIDEO, PAID, MEASUREMENT, COMPLIANCE]\nsurfaces: [PDP, GALLERY, PDP_VIDEO, PAID_AD]\nrule_atoms: []\nresearch_required_for: []\n"
replacement="    (pack/'test.yaml').write_text("+repr(yaml)+",encoding='utf-8')"
lines[start:end+1]=[replacement]
p.write_text('\n'.join(lines)+'\n',encoding='utf-8')
compile(p.read_text(encoding='utf-8'),str(p),'exec')
runpy.run_path(str(p),run_name='__main__')
