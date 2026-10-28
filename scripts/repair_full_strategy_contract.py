#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / 'runtime/cbcc/strategy_depth.py'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise SystemExit(f'pattern not found: {label}')
    return text.replace(old, new, 1)


def main() -> int:
    text = PATH.read_text(encoding='utf-8')

    text = replace_once(
        text,
        """def _v0624_framework_names(request:dict[str,Any]) -> list[str]:\n    plan=request.get('_agent_autonomy_plan') or {}\n    raw=plan.get('strategy_frameworks') if isinstance(plan,dict) else None\n    if raw is None: raw=request.get('marketing_frameworks') if request.get('marketing_frameworks') is not None else request.get('persuasion_frameworks')\n    if raw is None: return []\n""",
        """def _v0624_full_mode(request:dict[str,Any]) -> bool:\n    return bool(request.get('full_strategy') or request.get('full_delivery')) or str(request.get('strategy_delivery_mode') or request.get('delivery_mode') or '').upper() in {'FULL','FULL_STRATEGY','SIGNATURE'}\n\n\ndef _v0624_framework_names(request:dict[str,Any]) -> list[str]:\n    plan=request.get('_agent_autonomy_plan') or {}\n    raw=plan.get('strategy_frameworks') if isinstance(plan,dict) else None\n    if raw is None: raw=request.get('marketing_frameworks') if request.get('marketing_frameworks') is not None else request.get('persuasion_frameworks')\n    if raw is None: raw=[]\n""",
        'full mode helper',
    )

    text = replace_once(
        text,
        """    out=[]\n    for x in raw:\n        key=str(x or '').strip().upper().replace(' ','_')\n        name=aliases.get(key,str(x).strip())\n        if name and name not in out: out.append(name)\n    return out\n""",
        """    out=[]\n    for x in raw:\n        key=str(x or '').strip().upper().replace(' ','_')\n        name=aliases.get(key,str(x).strip())\n        if name and name not in out: out.append(name)\n    if _v0624_full_mode(request):\n        for name in ['RACE','STP','JTBD','AIDA','FABE','4P','Funnel']:\n            if name not in out: out.append(name)\n    return out\n""",
        'full frameworks',
    )

    text = replace_once(
        text,
        """def build_risk_priority_depth(info:dict[str,Any], request:dict[str,Any], compliance:dict[str,Any], research_gate:dict[str,Any], positioning:dict[str,Any], assets:list[dict[str,Any]], experiment:dict[str,Any]|None, market_depth:dict[str,Any]|None=None):\n    base=_V0624_ORIG_RISK(info,request,compliance,research_gate,positioning,assets,experiment,market_depth)\n    frameworks=_v0624_framework_names(request)\n""",
        """def build_risk_priority_depth(info:dict[str,Any], request:dict[str,Any], compliance:dict[str,Any], research_gate:dict[str,Any], positioning:dict[str,Any], assets:list[dict[str,Any]], experiment:dict[str,Any]|None, market_depth:dict[str,Any]|None=None):\n    base=_V0624_ORIG_RISK(info,request,compliance,research_gate,positioning,assets,experiment,market_depth)\n    frameworks=_v0624_framework_names(request)\n    if _v0624_full_mode(request):\n        base['full_strategy_hard_contract']=True\n        base['agent_stop_eligible']=not any(\n            row.get('severity')=='P0' and row.get('status') in {'OPEN','HOLD','BLOCKED'}\n            for row in (base.get('risk_register') or []) if isinstance(row,dict)\n        )\n        return base\n""",
        'full priority contract',
    )

    text = replace_once(
        text,
        """    full=bool(request.get('full_strategy') or request.get('full_delivery')) or str(request.get('strategy_delivery_mode') or request.get('delivery_mode') or '').upper() in {'FULL','FULL_STRATEGY','SIGNATURE'}\n""",
        """    full=_v0624_full_mode(request)\n""",
        'full mode reuse',
    )

    text = replace_once(
        text,
        """      'fixed_human_section_quota':False,\n      'principle':'Machine schema stays complete for compatibility and lineage. Human strategy only renders material decisions for the current commerce task.'\n""",
        """      'fixed_human_section_quota':bool(full),\n      'principle':('FULL commerce strategy uses the nine-domain hard delivery contract requested by the user; page/layout expression remains semantic and non-template.' if full else 'Machine schema stays complete for compatibility and lineage. Human strategy only renders material decisions for the current commerce task.')\n""",
        'projection authority',
    )

    text = replace_once(
        text,
        """    insert=f\"\\n> 人类策略投影：{hp.get('mode') or 'TASK_SCOPED'}；当前显示 {len(active)} 个相关决策域；固定九段人类配额：无。\\n\"\n""",
        """    if str(hp.get('mode') or '').upper()=='FULL':\n        insert=\"\\n> 人类策略投影：FULL；完整商品项目按 9 个硬交付域全部物化；RACE=Research → Action → Communication → Evaluation。页面/交互仍按业务对象设计，不等于固定页面模板。\\n\"\n    else:\n        insert=f\"\\n> 人类策略投影：{hp.get('mode') or 'TASK_SCOPED'}；当前显示 {len(active)} 个相关决策域；固定九段人类配额：无。\\n\"\n""",
        'full render note',
    )

    PATH.write_text(text, encoding='utf-8')
    print('FULL strategy hard-contract repair applied')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
