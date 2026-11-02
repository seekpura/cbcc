from pathlib import Path

creative_path = Path('runtime/cbcc/creative.py')
creative = creative_path.read_text(encoding='utf-8')
old = """def compile_creative_council(directions:list[dict[str,Any]]|None, curation:dict[str,Any], product_truth:dict[str,Any], culture:dict[str,Any], platform_compile:dict[str,Any], category_family:str|None=None, decision_intents:list[str]|None=None, opportunity_universe:dict[str,Any]|None=None)->dict[str,Any]:
    supplied=bool(directions)
    source_rows=list(directions or _auto_directions(product_truth,curation,culture,platform_compile,category_family,decision_intents,opportunity_universe))
"""
new = """def compile_creative_council(directions:list[dict[str,Any]]|None, curation:dict[str,Any], product_truth:dict[str,Any], culture:dict[str,Any], platform_compile:dict[str,Any], category_family:str|None=None, decision_intents:list[str]|None=None, opportunity_universe:dict[str,Any]|None=None)->dict[str,Any]:
    supplied=directions is not None
    source_rows=list(directions) if supplied else list(_auto_directions(product_truth,curation,culture,platform_compile,category_family,decision_intents,opportunity_universe))
"""
if creative.count(old) != 1:
    raise SystemExit(f'expected creative council block once, found {creative.count(old)}')
creative_path.write_text(creative.replace(old, new), encoding='utf-8')

compiler_path = Path('runtime/cbcc/compiler.py')
compiler = compiler_path.read_text(encoding='utf-8')
old = """    _write(p/'artifacts/creative_opportunity_universe.json',creative_opportunity_universe)
    council=compile_creative_council(request.get('creative_directions') or agent_creative_directions(agent_plan),curation,truth,culture,pc,category_family,[a.get('decision_intent') for a in architecture.get('assets') or []],creative_opportunity_universe)
"""
new = """    _write(p/'artifacts/creative_opportunity_universe.json',creative_opportunity_universe)
    creative_scope=agent_plan.get('creative_exploration') if isinstance(agent_plan.get('creative_exploration'),dict) else {}
    if 'creative_directions' in request:
        creative_direction_rows=request.get('creative_directions')
    elif creative_scope:
        creative_direction_rows=agent_creative_directions(agent_plan)
    else:
        creative_direction_rows=None
    council=compile_creative_council(creative_direction_rows,curation,truth,culture,pc,category_family,[a.get('decision_intent') for a in architecture.get('assets') or []],creative_opportunity_universe)
"""
if compiler.count(old) != 1:
    raise SystemExit(f'expected compiler creative council call once, found {compiler.count(old)}')
compiler_path.write_text(compiler.replace(old, new), encoding='utf-8')
