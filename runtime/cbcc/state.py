from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import json, shutil
from .dependencies import CANONICAL_GATES, DependencyGraph
from .models import stable_hash

def now(): return datetime.now(timezone.utc).isoformat()

class ProjectState:
    def __init__(self, project_dir:Path, data:dict):
        self.project_dir=Path(project_dir); self.data=data
    @property
    def meta(self): return self.project_dir/'.cbcc'
    @classmethod
    def init(cls, project_dir:Path, project_id:str, version='0.6.10-visual-execution-copy-continuity'):
        p=Path(project_dir); (p/'.cbcc/checkpoints').mkdir(parents=True,exist_ok=True); (p/'artifacts/objects').mkdir(parents=True,exist_ok=True)
        data={'project_id':project_id,'runtime_version':version,'revision':0,'current_stage':'INIT','created_at':now(),'updated_at':now(),
              'gates':{g:{'status':'PENDING','artifact_paths':[],'authority_hash':None,'updated_at':None} for g in CANONICAL_GATES},
              'pending_actions':[],'history':[],'item_reviews':{},'local_revision_requests':[],'request_hash':None,'final_ready':False}
        obj=cls(p,data); obj.save(); obj.checkpoint('INIT','PROJECT_INITIALIZED'); return obj
    @classmethod
    def load(cls, project_dir:Path):
        p=Path(project_dir); return cls(p,json.loads((p/'.cbcc/project_state.json').read_text(encoding='utf-8')))
    def save(self):
        self.data['updated_at']=now(); self.meta.mkdir(parents=True,exist_ok=True)
        (self.meta/'project_state.json').write_text(json.dumps(self.data,ensure_ascii=False,indent=2),encoding='utf-8')
    def checkpoint(self,stage,outcome):
        cp={'seq':len(self.data['history'])+1,'time':now(),'stage':stage,'outcome':outcome,'revision':self.data['revision'],
            'gate_status':{g:v['status'] for g,v in self.data['gates'].items()},'pending_actions':self.data['pending_actions']}
        self.data['history'].append(cp); self.data['current_stage']=stage; self.save()
        fn=self.meta/'checkpoints'/f"{cp['seq']:04d}-{stage.lower()}.json"; fn.write_text(json.dumps(cp,ensure_ascii=False,indent=2),encoding='utf-8')
        return fn
    def set_gate(self,gate,status,artifact_paths=None,payload=None):
        rec=self.data['gates'][gate]; rec['status']=status; rec['artifact_paths']=artifact_paths or rec['artifact_paths']; rec['updated_at']=now()
        if payload is not None: rec['authority_hash']=stable_hash(payload)
        self.save()
    def add_action(self,action):
        if action not in self.data['pending_actions']: self.data['pending_actions'].append(action); self.save()
    def resolve_action(self,action_id):
        for a in self.data['pending_actions']:
            if a.get('action_id')==action_id: a['status']='RESOLVED'; a['resolved_at']=now()
        self.save()
    def revise(self,changed:list[str]):
        affected=DependencyGraph().invalidate_set(changed)
        for gate in affected:
            self.data['gates'][gate]['status']='INVALIDATED'; self.data['gates'][gate]['authority_hash']=None
        self.data['revision']+=1; self.data['final_ready']=False
        self.checkpoint('REVISE',{'changed':changed,'invalidated':affected}); return affected
    def accept(self,gates:list[str]):
        for g in gates:
            if self.data['gates'][g]['status'] not in {'READY_REVIEW','LOCKED'}: raise ValueError(f'{g} is not review-ready')
            self.data['gates'][g]['status']='LOCKED'
        self.checkpoint('REVIEW_APPLY',{'accepted':gates})
    def apply_review_decision(self, decision:dict):
        if decision.get('project_id') not in {None,self.data.get('project_id')}: raise ValueError('review project_id mismatch')
        if decision.get('revision') not in {None,self.data.get('revision')}: raise ValueError('review revision is stale')
        accepted=[]; held=[]; revised=[]; accepted_items=[]; held_items=[]; revised_items=[]
        # Gate-level review remains the authority mechanism.
        for g in decision.get('accept',[]):
            if g not in self.data['gates']: raise ValueError(f'unknown gate {g}')
            if self.data['gates'][g]['status'] not in {'READY_REVIEW','LOCKED'}: raise ValueError(f'{g} is not review-ready')
            self.data['gates'][g]['status']='LOCKED'; accepted.append(g)
        for g in decision.get('hold',[]):
            if g not in self.data['gates']: raise ValueError(f'unknown gate {g}')
            self.data['gates'][g]['status']='HOLD'; held.append(g)
        # Item-level decisions are individually addressable and do not silently lock their parent gate.
        manifest_path=self.project_dir/'.cbcc/review/delivery_manifest.json'
        manifest=json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else {'items':[]}
        valid={x.get('item_id'):x for x in manifest.get('items',[])}
        self.data.setdefault('item_reviews',{})
        item_notes=decision.get('item_notes',{}) or {}
        for iid in decision.get('accept_items',[]):
            if iid not in valid: raise ValueError(f'unknown review item {iid}')
            self.data['item_reviews'][iid]={'status':'ACCEPTED','note':item_notes.get(iid,''),'revision':self.data['revision'],'updated_at':now()}; accepted_items.append(iid)
            item=valid[iid]
            if item.get('kind')=='LOCAL_REVISION_OUTPUT' and item.get('revision_request_id'):
                for rr in self.data.get('local_revision_requests',[]):
                    if rr.get('revision_request_id')==item.get('revision_request_id'):
                        rr['status']='ACCEPTED'; rr['accepted_at']=now(); rr['accepted_revision_id']=item.get('revision_id')
        for iid in decision.get('hold_items',[]):
            if iid not in valid: raise ValueError(f'unknown review item {iid}')
            self.data['item_reviews'][iid]={'status':'HOLD','note':item_notes.get(iid,''),'revision':self.data['revision'],'updated_at':now()}; held_items.append(iid)
        revision_requests=decision.get('item_revision_requests',{}) or {}
        for raw in decision.get('revise_items',[]):
            iid=raw.get('item_id') if isinstance(raw,dict) else raw
            req=raw if isinstance(raw,dict) else revision_requests.get(iid,{})
            if iid not in valid: raise ValueError(f'unknown review item {iid}')
            item=valid[iid]; rr={'revision_request_id':'LRQ-'+stable_hash([iid,self.data['revision'],req.get('requested_change',''),req.get('allowed_fields',[])])[:12],'item_id':iid,'item_kind':item.get('kind'),'asset_id':item.get('asset_id'),'object_id':item.get('object_id'),'parent_revision_id':item.get('revision_id'),'requested_change':req.get('requested_change',''),'allowed_fields':req.get('allowed_fields',[]),'note':req.get('note') or item_notes.get(iid,''),'created_at':now(),'base_revision':self.data['revision'],'status':'OPEN'}
            self.data.setdefault('local_revision_requests',[]).append(rr)
            self.data['item_reviews'][iid]={'status':'REVISE_REQUESTED','note':rr['note'],'revision':self.data['revision'],'updated_at':now(),'revision_request':rr}
            revised_items.append(iid)
        # Broad gate revision is explicit and preserves dependency-graph semantics.
        if decision.get('revise'):
            revised=list(decision['revise']); self.revise(revised)
        self.checkpoint('REVIEW_APPLY',{'accepted':accepted,'held':held,'revised':revised,'accepted_items':accepted_items,'held_items':held_items,'revised_items':revised_items,'notes':decision.get('notes',{})})
        return {'accepted':accepted,'held':held,'revised':revised,'accepted_items':accepted_items,'held_items':held_items,'revised_items':revised_items}
