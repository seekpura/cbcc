from pathlib import Path

p=Path('runtime/cbcc/compiler.py')
s=p.read_text(encoding='utf-8')

anchor="from .decision import compile_persuasion_frameworks\n"
insert="""from .decision import compile_persuasion_frameworks
from .decision_authority import (
    derive_task_content_families,
    selected_decision_frameworks,
    compile_decision_question_authority,
    compile_decision_trace_rows,
    augment_agent_next_action,
)
"""
if anchor not in s:
    raise SystemExit('decision import anchor not found')
s=s.replace(anchor,insert,1)

old_version="st.data['request_hash']=stable_hash(request); st.data['runtime_version']='0.6.24-task-scoped-strategy-asset'; st.save(); _write(st.meta/'request.json',request)"
new_version="st.data['request_hash']=stable_hash(request); st.data['runtime_version']='0.6.25-decision-question-authority'; st.save(); _write(st.meta/'request.json',request)"
if old_version not in s:
    raise SystemExit('runtime version anchor not found')
s=s.replace(old_version,new_version,1)

old_block="""    questions=request.get('shopper_questions') or ['What is it?','Why is it relevant to me?','What evidence supports the choice?','What should happen after purchase?']
    stages=['ACTION','ACTION','COMMUNICATION','EVALUATION']; traces=[]
    for i,q in enumerate(questions):
        traces.append(DecisionTrace(stages[min(i,3)],q,['IDENTIFY','RELATE','VERIFY','USE'][min(i,3)],rationale='Derived from explicit shopper question; framework is a decision aid, not a fixed asset template.').to_dict())
    persuasion=compile_persuasion_frameworks(questions,facts,domain.get('economics'),request.get('persuasion_frameworks'))
    dd={'traces':traces,'frameworks':request.get('decision_frameworks',['RACE','STP_JTBD','Fogg','Means-End','Signaling','FIRST','Cognitive Budget','Belief Sequence','Commerce Response Ladder']),
        'persuasion':persuasion,'culture_status':culture.get('status'),'race_ethnicity':culture.get('race_ethnicity'),'intersectionality':culture.get('intersectionality'),
        'domain_inputs':{'market':domain.get('market',{}).get('status'),'economics':domain.get('economics',{}).get('status'),'ads':domain.get('ads',{}).get('status'),'feedback':domain.get('feedback',{}).get('status'),'experiment':domain.get('experiment',{}).get('status')}}
    dp=_write(p/'artifacts/decision_trace.json',dd); st.set_gate('DECISION','READY_REVIEW',[dp],dd); st.checkpoint('DECISION','READY_REVIEW')

"""
new_block="""    # v0.6.25: decision questions/frameworks are compiled after Listing/current task signals are known.
    # No generic four-question journey or all-framework list is injected here.
    questions=[]

"""
if old_block not in s:
    raise SystemExit('legacy question/framework block not found')
s=s.replace(old_block,new_block,1)

old_families="    families=derive_content_families(request,agent_plan,family_surface=FAMILY_SURFACE,available_families=DEFAULT_FAMILIES)\n"
new_families="""    families=derive_task_content_families(request,agent_plan,available_families=DEFAULT_FAMILIES)
    selected_frameworks=selected_decision_frameworks(request,agent_plan)
    agent_plan['strategy_frameworks']=selected_frameworks
    agent_plan['content_scope_authority']='EXPLICIT_TASK_SIGNALS_ONLY'
    agent_plan['target_surfaces_are_constraints_not_content_quotas']=True
    question_authority=compile_decision_question_authority(
        request,agent_plan,
        listing=((domain.get('listing') or {}).get('compiled') or {}),
        active_families=families,
    )
    questions=list(question_authority.get('shopper_questions') or [])
    agent_plan['decision_question_authority']={
        'status':question_authority.get('status'),
        'question_count':question_authority.get('question_count',0),
        'decision_gap_count':len(question_authority.get('decision_gaps') or []),
        'synthetic_default_questions':False,
    }
    _write(p/'artifacts/agent_autonomy_plan.json',agent_plan)
    dqa=_write(p/'artifacts/decision_question_authority.json',question_authority)
    traces=compile_decision_trace_rows(question_authority,selected_frameworks)
    persuasion_requested=[x for x in selected_frameworks if x in {'AIDA','FABE','4P'}]
    persuasion=compile_persuasion_frameworks(questions,facts,domain.get('economics'),persuasion_requested)
    dd={
        'status':'DECISION_TRACE_COMPILED' if traces else 'NO_DECISION_TRACE_REQUIRED',
        'traces':traces,
        'frameworks':selected_frameworks,
        'framework_selection_authority':'EXPLICIT_AGENT_OR_USER_ONLY',
        'fixed_framework_quota':False,
        'synthetic_default_questions':False,
        'question_authority_artifact':dqa,
        'persuasion':persuasion,
        'culture_status':culture.get('status'),'race_ethnicity':culture.get('race_ethnicity'),'intersectionality':culture.get('intersectionality'),
        'domain_inputs':{'market':domain.get('market',{}).get('status'),'economics':domain.get('economics',{}).get('status'),'ads':domain.get('ads',{}).get('status'),'feedback':domain.get('feedback',{}).get('status'),'experiment':domain.get('experiment',{}).get('status')},
        'principle':'Decision Trace records current authored/grounded decision jobs. Question order does not assign funnel/RACE stage, and runtime capability does not select a framework.'
    }
    dp=_write(p/'artifacts/decision_trace.json',dd)
    st.set_gate('DECISION','READY_REVIEW',[dp,dqa],dd); st.checkpoint('DECISION','READY_REVIEW')
"""
if old_families not in s:
    raise SystemExit('families anchor not found')
s=s.replace(old_families,new_families,1)

old_next="""    agent_next_action=compile_agent_next_action(
        agent_plan,request=request,research_gate=research_gate,asset_architecture=architecture,
        creative_council=council,compliance=compliance,production_run=production_run,
    )
    _write(p/'artifacts/agent_next_action.json',agent_next_action)
"""
new_next="""    agent_next_action=compile_agent_next_action(
        agent_plan,request=request,research_gate=research_gate,asset_architecture=architecture,
        creative_council=council,compliance=compliance,production_run=production_run,
    )
    agent_next_action=augment_agent_next_action(agent_next_action,question_authority)
    _write(p/'artifacts/agent_next_action.json',agent_next_action)
"""
if old_next not in s:
    raise SystemExit('agent next action anchor not found')
s=s.replace(old_next,new_next,1)

p.write_text(s,encoding='utf-8')
print('v0.6.25 compiler patch applied')
