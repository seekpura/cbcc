from pathlib import Path

# ---------------- state.py ----------------
p=Path('runtime/cbcc/state.py')
s=p.read_text(encoding='utf-8')
old="""              'gates':{g:{'status':'PENDING','artifact_paths':[],'authority_hash':None,'updated_at':None} for g in CANONICAL_GATES},
"""
new="""              'gates':{g:{'status':'PENDING','artifact_paths':[],'authority_hash':None,'updated_at':None,
                            'required_for_current_scope':False,'blocking_for_current_scope':False,
                            'scope_status':'UNSCOPED','scope_reason':'Current task scope has not been compiled yet.'} for g in CANONICAL_GATES},
"""
if old not in s: raise SystemExit('state gate init anchor missing')
s=s.replace(old,new,1)
anchor="""    def add_action(self,action):
        if action not in self.data['pending_actions']: self.data['pending_actions'].append(action); self.save()
"""
insert="""    def set_gate_scope(self,gate,*,required_for_current_scope:bool,blocking_for_current_scope:bool|None=None,scope_reason:str='',scope_status:str|None=None):
        rec=self.data['gates'][gate]
        rec['required_for_current_scope']=bool(required_for_current_scope)
        rec['blocking_for_current_scope']=bool(required_for_current_scope if blocking_for_current_scope is None else blocking_for_current_scope)
        rec['scope_status']=scope_status or ('REQUIRED' if rec['required_for_current_scope'] else 'NOT_IN_CURRENT_SCOPE')
        rec['scope_reason']=scope_reason or ('Current task requires this gate.' if rec['required_for_current_scope'] else 'Canonical gate preserved for lineage; current task does not require it.')
        self.save()
    def add_action(self,action):
        if action not in self.data['pending_actions']: self.data['pending_actions'].append(action); self.save()
"""
if anchor not in s: raise SystemExit('state add_action anchor missing')
s=s.replace(anchor,insert,1)
p.write_text(s,encoding='utf-8')

# ---------------- review.py ----------------
p=Path('runtime/cbcc/review.py')
s=p.read_text(encoding='utf-8')
old="""            items.append({'item_id':iid,'kind':'AUTHORITY_GATE','name':gate,'status':rec.get('status'),'review_status':rv.get('status'),'review_note':rv.get('note',''),'required':gate not in {'ASSET_COMPILE','PRODUCTION'},'artifact_paths':rec.get('artifact_paths',[]),'authority_gate':gate})
"""
new="""            items.append({'item_id':iid,'kind':'AUTHORITY_GATE','name':gate,'status':rec.get('status'),'review_status':rv.get('status'),'review_note':rv.get('note',''),
                          'required':bool(rec.get('required_for_current_scope',False)),
                          'blocking_for_current_scope':bool(rec.get('blocking_for_current_scope',rec.get('required_for_current_scope',False))),
                          'scope_status':rec.get('scope_status','UNSCOPED'),'scope_reason':rec.get('scope_reason',''),
                          'artifact_paths':rec.get('artifact_paths',[]),'authority_gate':gate})
"""
if old not in s: raise SystemExit('review gate item anchor missing')
s=s.replace(old,new,1)
old="""    required_missing=[x['item_id'] for x in items if x.get('required') and (x.get('status') in {'MISSING','HOLD','INVALIDATED'} or x.get('review_status') in blocking_review)]
"""
new="""    required_missing=[]
    for x in items:
        if not x.get('required'): continue
        runtime_blocked=x.get('status') in {'MISSING','HOLD','INVALIDATED'}
        if x.get('kind')=='AUTHORITY_GATE' and not x.get('blocking_for_current_scope',True):
            runtime_blocked=False
        if runtime_blocked or x.get('review_status') in blocking_review:
            required_missing.append(x['item_id'])
"""
if old not in s: raise SystemExit('review required_missing anchor missing')
s=s.replace(old,new,1)
old="""        gate_rows.append(f"<tr><td>{html.escape(g)}</td><td>{html.escape(str(rec.get('status')))}</td><td>{len(rec.get('artifact_paths',[]))}</td></tr>")
"""
new="""        gate_rows.append(f"<tr><td>{html.escape(g)}</td><td>{html.escape(str(rec.get('status')))}</td><td>{html.escape(str(rec.get('scope_status','UNSCOPED')))}</td><td>{'yes' if rec.get('blocking_for_current_scope') else 'no'}</td><td>{len(rec.get('artifact_paths',[]))}</td></tr>")
"""
if old not in s: raise SystemExit('review html gate row anchor missing')
s=s.replace(old,new,1)
s=s.replace('<tr><th>Gate</th><th>Status</th><th>Artifacts</th></tr>','<tr><th>Gate</th><th>Runtime Status</th><th>Current Scope</th><th>Blocking</th><th>Artifacts</th></tr>',1)
old="""    md += [f"- [{ 'x' if rec.get('status')=='LOCKED' else ' ' }] {g} — {rec.get('status')}" for g,rec in state.get('gates',{}).items()]
"""
new="""    md += [f"- [{ 'x' if rec.get('status')=='LOCKED' else ' ' }] {g} — runtime={rec.get('status')} scope={rec.get('scope_status','UNSCOPED')} blocking={bool(rec.get('blocking_for_current_scope'))}" for g,rec in state.get('gates',{}).items()]
"""
if old not in s: raise SystemExit('review checklist gate anchor missing')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

# ---------------- compiler.py ----------------
p=Path('runtime/cbcc/compiler.py')
s=p.read_text(encoding='utf-8')
anchor="""from .decision_authority import (
    derive_task_content_families,
    selected_decision_frameworks,
    compile_decision_question_authority,
    compile_decision_trace_rows,
    augment_agent_next_action,
)
"""
insert=anchor+"from .scope_readiness import compile_required_content_families, compile_gate_scope\n"
if anchor not in s: raise SystemExit('compiler decision_authority import anchor missing')
s=s.replace(anchor,insert,1)
s=s.replace("st.data['runtime_version']='0.6.25-decision-question-authority'","st.data['runtime_version']='0.6.26-scope-readiness'",1)
anchor="""    dp=_write(p/'artifacts/decision_trace.json',dd)
    st.set_gate('DECISION','READY_REVIEW',[dp,dqa],dd); st.checkpoint('DECISION','READY_REVIEW')
    capabilities=set(pc.get('capabilities',[])); objects=[]
"""
insert="""    dp=_write(p/'artifacts/decision_trace.json',dd)
    st.set_gate('DECISION','READY_REVIEW',[dp,dqa],dd); st.checkpoint('DECISION','READY_REVIEW')

    content_requiredness=compile_required_content_families(request,agent_plan,families,question_authority)
    gate_scope=compile_gate_scope(request,families,content_requiredness,question_authority)
    _write(p/'artifacts/content_requiredness.json',content_requiredness)
    _write(p/'artifacts/gate_scope.json',gate_scope)
    for gate,meta in gate_scope.get('gates',{}).items():
        st.set_gate_scope(
            gate,
            required_for_current_scope=meta.get('required_for_current_scope',False),
            blocking_for_current_scope=meta.get('blocking_for_current_scope',False),
            scope_reason=meta.get('scope_reason',''),
            scope_status=meta.get('scope_status'),
        )
    required_by_family={row.get('family'):bool(row.get('required_for_current_scope')) for row in content_requiredness.get('rows',[])}
    capabilities=set(pc.get('capabilities',[])); objects=[]
"""
if anchor not in s: raise SystemExit('compiler decision->objects anchor missing')
s=s.replace(anchor,insert,1)
old="""        obj=ContentObject(oid,FAMILY_KIND.get(fam,fam.lower()),fam,'Resolve shopper decision job',target.target_id,FAMILY_SURFACE.get(fam),True,
"""
new="""        obj=ContentObject(oid,FAMILY_KIND.get(fam,fam.lower()),fam,'Resolve shopper decision job',target.target_id,FAMILY_SURFACE.get(fam),required_by_family.get(fam,False),
"""
if old not in s: raise SystemExit('compiler ContentObject required anchor missing')
s=s.replace(old,new,1)
old="""    cg={'objects':objects,'dynamic_count':len(objects),'fixed_count_authority':False,'scope_authority':'AGENT_OR_TASK_DERIVED','agent_plan_status':agent_plan.get('status')}
"""
new="""    cg={'objects':objects,'dynamic_count':len(objects),'fixed_count_authority':False,'scope_authority':'AGENT_OR_TASK_DERIVED','agent_plan_status':agent_plan.get('status'),
        'requiredness':content_requiredness,'required_object_count':sum(1 for o in objects if o.get('required')),
        'supporting_object_count':sum(1 for o in objects if not o.get('required'))}
"""
if old not in s: raise SystemExit('compiler content graph anchor missing')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

print('v0.6.26 scope readiness patch applied')
