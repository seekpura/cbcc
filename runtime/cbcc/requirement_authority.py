from __future__ import annotations
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping
import json, re

AUTHORITY_CLASSES=("USER_CANONICAL","USER_LATER_CLARIFICATION","DERIVED_PRODUCT_PRINCIPLE","ENGINEERING_GUARD","REJECTED_DEPRECATED")
ACTIVE_CLASSES=AUTHORITY_CLASSES[:-1]
AUTHORITY_PATH=Path("references/REQUIREMENT_AUTHORITY_CURRENT.json")
_TEST=re.compile(r"^(?:tests/|\.github/workflows/)",re.I)
_HUMAN=re.compile(r"(human|delivery|workspace|html|projection|strategy|listing|culture|visual|content)",re.I)

def _root(root=None)->Path:
    return Path(root).resolve() if root is not None else Path(__file__).resolve().parents[2]

def _json(path:Path)->dict[str,Any]:
    value=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value,dict): raise ValueError(f"{path} must contain an object")
    return value

def _semantic(req:str)->str:
    n=int(req.split("-")[1])
    src="CONVERSATION_REQUIREMENT_AUDIT.md" if n<=50 else ("CONVERSATION_REQUIREMENT_LEDGER_EXTENSION_01.md" if n<=60 else "CONVERSATION_REQUIREMENT_LEDGER_EXTENSION_02.md")
    return f"references/{src}#{req}"

def _consumer_file_path(value:str)->str:
    return re.split(r"::|#",str(value or ""),maxsplit=1)[0]

def _consumer_index(root:Path,raw:Mapping[str,Any])->dict[str,list[str]]:
    base=_json(root/"references/REQUIREMENT_CONSUMER_MAP_V0664.json")
    over=_json(root/"references/REQUIREMENT_CONSUMER_MAP_CURRENT_OVERRIDES.json")
    rows={str(x.get("req")):dict(x) for x in base.get("requirements",[]) if isinstance(x,Mapping) and x.get("req")}
    for x in over.get("overrides",[]):
        if isinstance(x,Mapping) and x.get("req"): rows[str(x["req"])]=dict(x)
    out={req:[str(v) for v in row.get("consumers",[]) if str(v)] for req,row in rows.items()}
    def walk(node):
        if isinstance(node,Mapping):
            req=str(node.get("req") or node.get("requirement_id") or "")
            if req.startswith("REQ-") and isinstance(node.get("consumers"),list):
                bucket=out.setdefault(req,[])
                for v in node["consumers"]:
                    v=str(v)
                    if v and v not in bucket: bucket.append(v)
            for v in node.values(): walk(v)
        elif isinstance(node,list):
            for v in node: walk(v)
    for path in sorted((root/"references").glob("REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE*.json")):
        try: walk(_json(path))
        except Exception: pass
    for profile in raw.get("consumer_profiles",[]):
        if not isinstance(profile,Mapping): continue
        ids=[str(x) for x in profile.get("ids",[])]
        m=re.match(r"REQ-(\d{3})\.\.REQ-(\d{3})$",str(profile.get("range") or ""))
        if m: ids += [f"REQ-{i:03d}" for i in range(int(m.group(1)),int(m.group(2))+1)]
        for req in ids:
            bucket=out.setdefault(req,[])
            for v in profile.get("paths",[]):
                v=str(v)
                if v and v not in bucket: bucket.append(v)
    return out

def load_current_requirement_authority(root=None)->dict[str,Any]:
    base=_root(root); raw=_json(base/AUTHORITY_PATH)
    assignments={}
    for cls,reqs in raw.get("authority_assignments",{}).items():
        for req in reqs:
            if req in assignments: raise ValueError(f"duplicate assignment {req}")
            assignments[str(req)]=str(cls)
    anchors=raw.get("user_source_anchors",{})
    origins={}
    if isinstance(anchors,Mapping):
        for sid,a in anchors.items():
            if isinstance(a,Mapping):
                for req in a.get("bound_requirements",[]): origins.setdefault(str(req),[]).append(str(sid))
    consumers=_consumer_index(base,raw)
    derived=raw.get("derived_from_overrides",{}); interp=raw.get("current_interpretation_overrides",{}); human_over=raw.get("human_projection_overrides",{})
    requirements=[]
    for i in range(1,91):
        req=f"REQ-{i:03d}"; cls=assignments.get(req)
        d=[str(x) for x in derived.get(req,[])]
        if cls in {"DERIVED_PRODUCT_PRINCIPLE","ENGINEERING_GUARD"} and not d: d=["PG-CBCC-01"]
        business=[str(x) for x in consumers.get(req,[]) if str(x)]
        human=[str(x) for x in human_over.get(req,[]) if str(x)]
        for p in business:
            if _HUMAN.search(p) and p not in human: human.append(p)
        if not human: human=["NOT_DIRECT_HUMAN_FACING"]
        source=_semantic(req)
        requirements.append({
            "req":req,"authority_class":cls,"origin_refs":origins.get(req,[]),"derived_from":d,
            "semantic_source":source,
            "current_interpretation":str(interp.get(req) or f"Apply {req} from {source} with attribution {cls}; this overlay adds no business semantics."),
            "business_consumers":business,"human_projection":human,
        })
    out=deepcopy(raw)
    if isinstance(anchors,Mapping):
        meanings=out.get("later_clarification_meanings",{})
        out["user_source_anchors"]=[{"source_id":str(sid),**dict(a),**({"summary":meanings[sid]} if sid in meanings else {})} for sid,a in anchors.items() if isinstance(a,Mapping)]
    out["requirements"]=requirements
    out["direct_user_requirement_ids"]=list(raw.get("authority_assignments",{}).get("USER_CANONICAL",[]))
    out["later_user_requirement_ids"]=list(raw.get("authority_assignments",{}).get("USER_LATER_CLARIFICATION",[]))
    return out

def audit_requirement_authority(document:Mapping[str,Any],*,root=None)->dict[str,Any]:
    base=_root(root); doc=deepcopy(dict(document)); issues=[]
    def add(code,**data): issues.append({"code":code,**data})
    if tuple(doc.get("authority_classes",()))!=AUTHORITY_CLASSES: add("AUTHORITY_CLASS_SET_MISMATCH")
    rows=[dict(x) for x in doc.get("requirements",[]) if isinstance(x,Mapping)]
    ids=[str(x.get("req") or "") for x in rows]; expected=[f"REQ-{i:03d}" for i in range(1,91)]
    if ids!=expected or len(set(ids))!=90: add("ACTIVE_REQUIREMENT_ID_SET_MISMATCH")
    direct=set(doc.get("direct_user_requirement_ids",[])); later=set(doc.get("later_user_requirement_ids",[]))
    anchors={str(x.get("source_id")) for x in doc.get("user_source_anchors",[]) if isinstance(x,Mapping)}
    goals={str(x.get("source_id")) for x in doc.get("product_goal_anchors",[]) if isinstance(x,Mapping)}
    valid=anchors|goals
    for row in rows:
        req=str(row.get("req") or ""); cls=str(row.get("authority_class") or ""); origins=[str(x) for x in row.get("origin_refs",[])]; derived=[str(x) for x in row.get("derived_from",[])]; consumers=[str(x) for x in row.get("business_consumers",[])]; human=row.get("human_projection",[])
        if cls not in ACTIVE_CLASSES: add("ACTIVE_REQUIREMENT_CLASS_INVALID",req=req)
        if cls=="USER_CANONICAL" and (req not in direct or not origins or any(not x.startswith("UC-") for x in origins)): add("DIRECT_USER_ATTRIBUTION_MISMATCH",req=req)
        if cls=="USER_LATER_CLARIFICATION" and (req not in later or not origins or any(not x.startswith("UL-") for x in origins)): add("LATER_USER_ATTRIBUTION_MISMATCH",req=req)
        if cls in {"DERIVED_PRODUCT_PRINCIPLE","ENGINEERING_GUARD"} and not derived: add("DERIVED_LINEAGE_MISSING",req=req)
        for ref in origins+derived:
            if ref not in valid: add("UNKNOWN_AUTHORITY_LINEAGE_REF",req=req,ref=ref)
        if not row.get("semantic_source"): add("SEMANTIC_SOURCE_MISSING",req=req)
        if not row.get("current_interpretation"): add("CURRENT_INTERPRETATION_MISSING",req=req)
        if not consumers: add("BUSINESS_CONSUMER_BINDING_MISSING",req=req)
        if not human: add("HUMAN_PROJECTION_BINDING_MISSING",req=req)
        for p in consumers:
            if _TEST.search(p): add("TEST_PATH_AS_BUSINESS_CONSUMER",req=req,path=p)
            else:
                file_path=_consumer_file_path(p)
                if file_path.startswith(("runtime/","references/","scripts/")) and not (base/file_path).exists(): add("BUSINESS_CONSUMER_PATH_MISSING",req=req,path=p,file_path=file_path)
        for p in human:
            p=str(p); file_path=_consumer_file_path(p)
            if p!="NOT_DIRECT_HUMAN_FACING" and file_path.startswith(("runtime/","references/","scripts/")) and not (base/file_path).exists(): add("HUMAN_PROJECTION_PATH_MISSING",req=req,path=p,file_path=file_path)
    rejected=[dict(x) for x in doc.get("rejected_deprecated",[]) if isinstance(x,Mapping)]
    seen=set()
    for row in rejected:
        rid=str(row.get("authority_id") or "")
        if not rid or rid in seen: add("REJECTED_RULE_ID_INVALID",authority_id=rid)
        seen.add(rid)
        if row.get("authority_class")!="REJECTED_DEPRECATED": add("REJECTED_RULE_CLASS_INVALID",authority_id=rid)
        if row.get("active_business_consumers"): add("REJECTED_RULE_HAS_ACTIVE_BUSINESS_CONSUMER",authority_id=rid)
        if not row.get("superseded_by"): add("REJECTED_RULE_SUPERSESSION_MISSING",authority_id=rid)
    by_req={row.get("req"):row for row in rows}
    for anchor in doc.get("user_source_anchors",[]):
        if not isinstance(anchor,Mapping): continue
        sid=str(anchor.get("source_id") or ""); bound=[str(x) for x in anchor.get("bound_requirements",[])]
        if not bound: add("USER_SOURCE_ANCHOR_UNBOUND",source_id=sid)
        if anchor.get("priority")=="P0":
            br=[by_req[x] for x in bound if x in by_req]
            if not any(x.get("business_consumers") for x in br): add("P0_USER_SOURCE_RUNTIME_CONSUMER_MISSING",source_id=sid)
            if not any(any(str(p)!="NOT_DIRECT_HUMAN_FACING" for p in x.get("human_projection",[])) for x in br): add("P0_USER_SOURCE_HUMAN_PROJECTION_MISSING",source_id=sid)
    for key in ("authority_overlay_does_not_author_business_strategy","existing_requirement_ledgers_remain_semantic_sources","consumer_maps_remain_execution_wiring_authority","derived_may_not_impersonate_user","rejected_deprecated_may_not_have_active_business_consumers","test_and_workflow_paths_are_proof_only"):
        if (doc.get("rules") or {}).get(key) is not True: add("AUTHORITY_RULE_DISABLED",rule=key)
    return {"status":"PASS" if not issues else "FAIL","requirement_count":len(rows),"rejected_deprecated_count":len(rejected),"issue_count":len(issues),"issues":issues,"authority_classes":list(AUTHORITY_CLASSES),"principle":"Attribution only: ledgers author semantics; consumer maps wire execution; tests/guards do not author business."}

def current_requirement_authority_audit(root=None)->dict[str,Any]:
    base=_root(root); return audit_requirement_authority(load_current_requirement_authority(base),root=base)
