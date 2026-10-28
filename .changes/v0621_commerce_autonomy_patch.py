from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise SystemExit(f'missing patch target: {label}')
    return text.replace(old, new, 1)


# ---- compiler: make Agent autonomy a first-class authority ----
p = Path('runtime/cbcc/compiler.py')
text = p.read_text(encoding='utf-8')
text = replace_once(
    text,
    "from .research import compile_research_gate, apply_host_research_response\n",
    "from .research import compile_research_gate, apply_host_research_response\nfrom .agent_autonomy import (\n    compile_agent_autonomy_plan, research_requirements_from_plan, derive_content_families,\n    agent_creative_opportunities, agent_creative_directions,\n)\n",
    'compiler import agent autonomy',
)
text = replace_once(
    text,
    "    st.data['request_hash']=stable_hash(request); st.data['runtime_version']='0.6.12-portable-provider-package-production-receipt'; st.save(); _write(st.meta/'request.json',request)\n\n    evidence={'sources':request.get('sources',[]),'assumptions':request.get('assumptions',[])}\n",
    "    st.data['request_hash']=stable_hash(request); st.data['runtime_version']='0.6.21-commerce-agent-autonomy'; st.save(); _write(st.meta/'request.json',request)\n\n    agent_plan=compile_agent_autonomy_plan(request)\n    _write(p/'artifacts/agent_autonomy_plan.json',agent_plan)\n\n    evidence={'sources':request.get('sources',[]),'assumptions':request.get('assumptions',[])}\n",
    'compiler compile autonomy plan',
)
text = replace_once(
    text,
    "    research_gate=compile_research_gate(request.get('research_requirements'),request.get('sources',[]),request.get('research_as_of'))\n",
    "    research_gate=compile_research_gate(research_requirements_from_plan(request,agent_plan),request.get('sources',[]),request.get('research_as_of'))\n    research_gate['agent_autonomy']={'plan_status':agent_plan.get('status'),'authority':(agent_plan.get('research') or {}).get('authority'),'stop_conditions':(agent_plan.get('research') or {}).get('stop_conditions') or []}\n",
    'compiler dynamic research requirements',
)
text = replace_once(
    text,
    "    families=request.get('content_families') or DEFAULT_FAMILIES\n",
    "    families=derive_content_families(request,agent_plan,family_surface=FAMILY_SURFACE,available_families=DEFAULT_FAMILIES)\n",
    'compiler dynamic content families',
)
text = replace_once(
    text,
    "    cg={'objects':objects,'dynamic_count':len(objects),'fixed_count_authority':False}\n",
    "    cg={'objects':objects,'dynamic_count':len(objects),'fixed_count_authority':False,'scope_authority':'AGENT_OR_TASK_DERIVED','agent_plan_status':agent_plan.get('status')}\n",
    'compiler content graph authority',
)
old = """    creative_opportunity_universe=compile_creative_opportunity_universe(\n        truth,product_visual_intelligence,category_family,architecture.get('assets') or [],curation,culture,tc\n    )\n"""
new = """    creative_opportunity_universe=compile_creative_opportunity_universe(\n        truth,product_visual_intelligence,category_family,architecture.get('assets') or [],curation,culture,tc,\n        agent_opportunities=agent_creative_opportunities(agent_plan),\n    )\n"""
text = replace_once(text, old, new, 'compiler agent creative opportunities')
text = replace_once(
    text,
    "    council=compile_creative_council(request.get('creative_directions'),curation,truth,culture,pc,category_family,[a.get('decision_intent') for a in architecture.get('assets') or []],creative_opportunity_universe)\n",
    "    council=compile_creative_council(request.get('creative_directions') or agent_creative_directions(agent_plan),curation,truth,culture,pc,category_family,[a.get('decision_intent') for a in architecture.get('assets') or []],creative_opportunity_universe)\n",
    'compiler agent creative directions',
)
text = replace_once(
    text,
    "              'surface_architecture':surface_architecture,'asset_expression_assignment':architecture.get('creative_system_assignment'),'product_visual_intelligence':product_visual_intelligence,'creative_anchor_plan':creative_anchors}\n",
    "              'surface_architecture':surface_architecture,'asset_expression_assignment':architecture.get('creative_system_assignment'),'product_visual_intelligence':product_visual_intelligence,'creative_anchor_plan':creative_anchors,\n              'agent_autonomy_plan':agent_plan}\n",
    'compiler creative autonomy trace',
)
text = replace_once(
    text,
    "    strategy_request=dict(request); strategy_request['claims']=claims; strategy_request['_market_evidence_fit_contract']=market_fit_contract\n",
    "    strategy_request=dict(request); strategy_request['claims']=claims; strategy_request['_market_evidence_fit_contract']=market_fit_contract; strategy_request['_agent_autonomy_plan']=agent_plan\n",
    'compiler strategy autonomy trace',
)
p.write_text(text, encoding='utf-8')


# ---- creative opportunity: agent-authored mechanisms are authoritative; library is fallback only ----
p = Path('runtime/cbcc/creative_opportunity.py')
text = p.read_text(encoding='utf-8')
text = replace_once(
    text,
    "    target:dict[str,Any]|None=None,\n)->dict[str,Any]:\n",
    "    target:dict[str,Any]|None=None, agent_opportunities:list[dict[str,Any]]|None=None,\n)->dict[str,Any]:\n",
    'creative opportunity signature',
)
marker = "    product=_product(product_truth); pvi=product_visual_intelligence or {}; curation=curation or {}; target=target or {}\n"
insert = marker + """    if agent_opportunities:\n        authored=[]\n        for index,raw in enumerate(agent_opportunities):\n            if not isinstance(raw,dict):\n                continue\n            row=dict(raw)\n            mid=str(row.get('mechanism_id') or f'AGENT-MECHANISM-{index+1:02d}')\n            row['mechanism_id']=mid\n            row.setdefault('mechanism_name',mid.replace('_',' ').replace('-',' ').title())\n            row.setdefault('domain','AGENT_DISCOVERED')\n            row.setdefault('decision_intents',[])\n            row.setdefault('direction_role','PRIMARY_MECHANISM')\n            row.setdefault('score',0.85)\n            row.setdefault('opportunity_id','COP-'+stable_hash([product.get('name'),category_family,mid,row])[:10].upper())\n            row.setdefault('activation_signals',{'agent_authored':True})\n            authored.append(row)\n        return {\n            'status':'AGENT_AUTHORED_CREATIVE_OPPORTUNITY_UNIVERSE',\n            'product_name':product.get('name'),'category_family':category_family,\n            'observed_decision_intents':[str(a.get('decision_intent') or 'DECISION_SUPPORT').upper() for a in (assets or [])],\n            'opportunity_count':len(authored),'opportunities':authored,\n            'reference_whitespace_signals':curation.get('white_space') or [],\n            'category_cliche_signals':curation.get('category_cliches') or [],\n            'search_domains':list(dict.fromkeys(str(row.get('domain') or 'AGENT_DISCOVERED') for row in authored)),\n            'selection_rule':'Host agent authored the opportunity universe from current evidence. Runtime does not impose a mechanism quota or style library.',\n            'target_context':{'market':target.get('market'),'platform_family':target.get('platform_family'),'site':target.get('site'),'category':target.get('category')},\n            'culture_boundary':'Culture/identity may change casting, language and scene when supported by evidence; never use identity as a stereotype-based style shortcut.',\n        }\n"""
text = replace_once(text, marker, insert, 'creative opportunity authored universe')
text = replace_once(
    text,
    "    activated.sort(key=lambda x:(x['score'],x['mechanism_id']),reverse=True)\n    selected=activated[:12]  # bounded 6–12 search universe; current library exposes 12 mechanisms.\n",
    "    activated.sort(key=lambda x:(x['score'],x['mechanism_id']),reverse=True)\n    if activated:\n        adaptive_floor=max(0.55,float(activated[0].get('score') or 0)-0.18)\n        selected=[row for row in activated if float(row.get('score') or 0)>=adaptive_floor]\n    else:\n        selected=[]\n",
    'creative opportunity adaptive fallback selection',
)
text = replace_once(
    text,
    "        'reference_whitespace_signals':whitespace[:5],'category_cliche_signals':cliches[:5],\n        'search_domains':['PRODUCT_STRUCTURE','EVIDENCE_SYSTEM','HUMAN_CONTEXT','MATERIAL_CMF','SPATIAL_RELATION','BEHAVIOR_FLOW','RISK_REDUCTION','SYSTEM_MAP','INFORMATION_DESIGN','CATEGORY_WHITESPACE','REMOTE_DOMAIN'],\n        'selection_rule':'Explore mechanisms first; cluster into materially different directions only after product/decision/surface fit is visible. Opportunities are mechanisms, not finished styles.',\n",
    "        'reference_whitespace_signals':whitespace,'category_cliche_signals':cliches,\n        'search_domains':list(dict.fromkeys(str(row.get('domain') or '') for row in selected if row.get('domain'))),\n        'selection_rule':'Fallback heuristics rank mechanisms by current evidence and keep the materially relevant set. No fixed mechanism count is authoritative; a host agent may replace this universe entirely.',\n",
    'creative opportunity no fixed signal/domain quota',
)
p.write_text(text, encoding='utf-8')


# ---- creative council: remove 6-12 / 3-5 direction authority and fixed expression templates ----
p = Path('runtime/cbcc/creative.py')
text = p.read_text(encoding='utf-8')
text = text.replace('    """Synthesize 3–5 materially different directions *after* mechanism search.\n', '    """Synthesize a task-dependent number of materially different directions after mechanism search.\n', 1)
text = replace_once(
    text,
    "    if len(opportunities)<6:\n        fallback=_legacy_opportunity_fallback(product_truth,decision_intents)\n        have={x.get('mechanism_id') for x in opportunities}\n        opportunities += [x for x in fallback.get('opportunities',[]) if x.get('mechanism_id') not in have]\n    opportunities=opportunities[:12]\n",
    "    if not opportunities:\n        fallback=_legacy_opportunity_fallback(product_truth,decision_intents)\n        opportunities=list(fallback.get('opportunities') or [])\n",
    'creative no fixed opportunity minimum/cap',
)
text = replace_once(
    text,
    "    primary_pool=[x for x in opportunities if x.get('direction_role')=='PRIMARY_MECHANISM']\n    if len(primary_pool)<3:\n        primary_pool=opportunities[:]\n    n_dirs=max(3,min(5,len(primary_pool)))\n    leads=primary_pool[:n_dirs]\n",
    "    primary_pool=[x for x in opportunities if x.get('direction_role')=='PRIMARY_MECHANISM']\n    if not primary_pool:\n        primary_pool=opportunities[:]\n    if primary_pool:\n        top_score=max(float(x.get('score') or 0) for x in primary_pool)\n        direction_floor=max(0.55,top_score-0.12)\n        leads=[x for x in primary_pool if float(x.get('score') or 0)>=direction_floor]\n    else:\n        leads=[]\n",
    'creative adaptive direction count',
)
text = replace_once(
    text,
    "        'search_before_selection_trace':{'rule':'Explore 6–12 product/decision/material/scene/reference-whitespace mechanisms before synthesizing 3–5 directions. Stable route labels are downstream compatibility tags, not a style template.','opportunity_status':(opportunity_universe or {}).get('status'),'opportunity_count':(opportunity_universe or {}).get('opportunity_count'),'direction_count':len(rows)},\n        'minimum_material_difference_contract':{'required_differences':4,'dimensions':['buyer_entry','creative_thesis','composition_grammar','product_role','image_language','proof_mechanism','verbal_thesis','color_world']},\n",
    "        'search_before_selection_trace':{'rule':'Explore until the agent has enough materially different, evidence-supported options to make the decision. No fixed mechanism or direction count is authoritative. Stable route labels are compatibility tags only.','opportunity_status':(opportunity_universe or {}).get('status'),'opportunity_count':(opportunity_universe or {}).get('opportunity_count'),'direction_count':len(rows)},\n        'minimum_material_difference_contract':{'required_differences':'TASK_DEPENDENT','dimensions':['buyer_entry','creative_thesis','composition_grammar','product_role','image_language','proof_mechanism','verbal_thesis','color_world'],'rule':'Differentiate on the dimensions that materially change the shopper experience; do not satisfy a numeric diversity quota.'},\n",
    'creative council no fixed exploration quotas',
)
start = text.index('def _expression_variant(')
end = text.index('\ndef apply_creative_system_to_assets', start)
replacement = '''def _expression_variant(asset:dict[str,Any], direction:dict[str,Any], ordinal:int)->dict[str,Any]:\n    """Derive expression from the actual asset decision signature; never rotate a fixed layout library."""\n    del ordinal\n    sig=dict(asset.get('visual_production_signature') or {})\n    authored=asset.get('agent_visual_expression') if isinstance(asset.get('agent_visual_expression'),dict) else {}\n    composition=authored.get('composition_grammar') or sig.get('composition_grammar') or 'Build hierarchy from the decision-critical evidence relationship.'\n    view=authored.get('preferred_view') or authored.get('camera_or_view') or sig.get('camera_or_view') or 'Choose the view that exposes the decision-critical evidence plane.'\n    context=authored.get('context_role') or sig.get('context_role') or 'Include only context that changes the shopper decision.'\n    variant_id=authored.get('variant_id') or 'EXPR-'+stable_hash([asset.get('asset_id'),asset.get('decision_intent'),composition,view,context,direction.get('direction_id')])[:8].upper()\n    return {\n        'variant_id':variant_id,\n        'spatial_rhythm':authored.get('spatial_rhythm') or 'DECISION_DERIVED',\n        'composition_grammar':composition,\n        'preferred_view':view,\n        'context_role':context,\n        'direction_id':direction.get('direction_id'),'direction_route':direction.get('route'),'direction_thesis':direction.get('creative_thesis'),\n        'authority':'AGENT_OR_ASSET_DECISION_SIGNATURE' if authored or sig else 'GENERAL_FALLBACK',\n        'same_layout_guard':'Do not inherit the previous asset composition. Rebuild hierarchy from this asset decision job and its evidence plane.',\n    }\n\n'''
text = text[:start] + replacement + text[end+1:]
p.write_text(text, encoding='utf-8')
