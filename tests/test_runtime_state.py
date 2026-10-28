from pathlib import Path
import sys,json,tempfile
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.state import ProjectState

def test_checkpoint_and_exact_revision_invalidation(tmp_path):
    st=ProjectState.init(tmp_path/'p','P1')
    for g in ['EVIDENCE','PRODUCT_TRUTH','COMMERCE_ENTITY','TARGET_CONTEXT','DECISION','CONTENT_GRAPH']:
        st.set_gate(g,'READY_REVIEW',payload={'g':g})
    st.set_gate('EVIDENCE','LOCKED',payload={'g':'EVIDENCE'})
    affected=st.revise(['TARGET_CONTEXT'])
    assert 'TARGET_CONTEXT' in affected and 'DECISION' in affected and 'CONTENT_GRAPH' in affected
    assert 'PRODUCT_TRUTH' not in affected and st.data['gates']['PRODUCT_TRUTH']['status']=='READY_REVIEW'
    assert len(list((tmp_path/'p/.cbcc/checkpoints').glob('*.json')))>=2
