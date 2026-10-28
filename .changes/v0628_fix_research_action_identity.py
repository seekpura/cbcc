from pathlib import Path

p=Path('runtime/cbcc/agent_autonomy.py')
s=p.read_text(encoding='utf-8')
s=s.replace("'action':'OPTIONAL_RESEARCH_OR_EVIDENCE_REFRESH',\n            'reason':'Additional evidence may improve confidence or a future scope, but is not required to close the current deliverable.'","'action':'RESEARCH_OR_EVIDENCE_RESOLUTION',\n            'reason':'Additional evidence may improve confidence or a future scope, but is not required to close the current deliverable.'",1)
p.write_text(s,encoding='utf-8')

p=Path('tests/test_v0628_agent_frontier_scope.py')
s=p.read_text(encoding='utf-8')
s=s.replace("assert out['advisory_frontier'][0]['action']=='OPTIONAL_RESEARCH_OR_EVIDENCE_REFRESH'","assert out['advisory_frontier'][0]['action']=='RESEARCH_OR_EVIDENCE_RESOLUTION'\n    assert out['advisory_frontier'][0]['blocking'] is False",1)
s=s.replace("'advisory_frontier':[{'action':'OPTIONAL_RESEARCH_OR_EVIDENCE_REFRESH','blocking':False}]","'advisory_frontier':[{'action':'RESEARCH_OR_EVIDENCE_RESOLUTION','blocking':False}]",1)
s=s.replace("'advisory_frontier':[{'action':'OPTIONAL_RESEARCH_OR_EVIDENCE_REFRESH','reason':'可选补充研究'}]","'advisory_frontier':[{'action':'RESEARCH_OR_EVIDENCE_RESOLUTION','reason':'可选补充研究','blocking':False}]",1)
p.write_text(s,encoding='utf-8')
print('v0.6.28 research action identity compatibility repaired')
