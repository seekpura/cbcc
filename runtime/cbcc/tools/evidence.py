from __future__ import annotations
from collections import defaultdict
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any
import json

_VOLATILE={'_row_index','ingested_at','fetched_at','loaded_at','runtime_ingested_at'}
_LINEAGE_KEYS={'version_id','supersedes','supersedes_version_id','content_hash','logical_source_id'}

def _stable(value:Any)->str:
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),default=str)

def _fingerprint(row:dict[str,Any], *, include_source:bool=False)->str:
    payload={}
    for k,v in row.items():
        if k in _VOLATILE or k in _LINEAGE_KEYS: continue
        if not include_source and k in {'source_id','source_url','url','collected_at','observed_at','published_at','verified_at'}: continue
        payload[k]=v
    return sha256(_stable(payload).encode('utf-8')).hexdigest()

def _parse_dt(v:Any):
    if v in (None,''): return None
    try:
        dt=datetime.fromisoformat(str(v).strip().replace('Z','+00:00'))
        if dt.tzinfo is None: dt=dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None

def _entity_key(row:dict[str,Any]):
    for key in ['entity_key','listing_id','review_id','keyword_id','query_id','item_id','product_id']:
        if row.get(key) not in (None,''): return f'{key}:{row.get(key)}'
    return None

def compile_research_ingestion(datasets:dict[str,list[dict[str,Any]]], source_records:list[dict[str,Any]]|None=None, config:dict[str,Any]|None=None)->dict[str,Any]:
    """Compile exact-row dedup, source version lineage and conflict-review metadata.

    Default mode is REPORT_ONLY. Canonical rows replace analytical inputs only when the project
    explicitly sets ``dedup_mode=EXACT_SOURCE_ROW``. Cross-source content matches are reported but
    never silently deduplicated because two sources may independently observe the same fact.
    """
    config=config or {}; source_records=list(source_records or [])
    mode=str(config.get('dedup_mode') or 'REPORT_ONLY').upper()
    canonical={}; dataset_cards=[]; cross_content=defaultdict(list); conflict_groups=[]
    for name,raw in (datasets or {}).items():
        rows=list(raw or []); seen={}; out=[]; dup=[]; entity_versions=defaultdict(list)
        for idx,row in enumerate(rows):
            row=dict(row); sid=str(row.get('source_id') or '')
            content_fp=_fingerprint(row,include_source=False); source_fp=_fingerprint(row,include_source=True)
            exact_key=(sid,source_fp) if sid else ('NO_SOURCE',source_fp)
            cross_content[content_fp].append({'dataset':name,'row_index':idx,'source_id':sid or None})
            ek=_entity_key(row)
            if ek:
                entity_versions[ek].append({'row_index':idx,'source_id':sid or None,'content_fingerprint':content_fp,'observed_at':row.get('observed_at') or row.get('collected_at')})
            if exact_key in seen:
                dup.append({'row_index':idx,'duplicate_of_row_index':seen[exact_key],'source_id':sid or None,'source_fingerprint':source_fp,'reason':'EXACT_SAME_SOURCE_ROW_FINGERPRINT'})
                if mode=='EXACT_SOURCE_ROW': continue
            else:
                seen[exact_key]=idx
            out.append(row)
        for ek,items in entity_versions.items():
            if len({x['content_fingerprint'] for x in items})>1:
                conflict_groups.append({'dataset':name,'entity_key':ek,'observations':items,'status':'VERSION_OR_CONFLICT_REVIEW','why':'The same explicit entity key has multiple content fingerprints. Treat as version/change evidence until time/order/source context resolves it.'})
        canonical[name]=out
        dataset_cards.append({'dataset':name,'input_rows':len(rows),'canonical_rows':len(out),'exact_duplicates':len(dup),'dedup_mode':mode,'duplicates':dup[:100],'decision_boundary':'Only exact same-source row fingerprints are eligible for deterministic dedup. Semantic/fuzzy duplicates remain review items.'})
    cross=[]
    for fp,items in cross_content.items():
        sources={x.get('source_id') for x in items if x.get('source_id')}
        if len(items)>1 and len(sources)>1:
            cross.append({'content_fingerprint':fp,'observations':items[:30],'source_ids':sorted(sources),'status':'CROSS_SOURCE_DUPLICATE_CANDIDATE','decision':'REPORT_ONLY_NEVER_AUTO_DEDUP','why':'Independent sources can legitimately report the same fact; cross-source equality is provenance evidence, not permission to delete rows.'})
    versions=defaultdict(list)
    for i,src in enumerate(source_records):
        logical=str(src.get('logical_source_id') or src.get('source_id') or f'UNRESOLVED-{i}')
        version=str(src.get('version_id') or src.get('content_hash') or src.get('observed_at') or src.get('collected_at') or f'VERSION-{i}')
        versions[logical].append({'logical_source_id':logical,'source_id':src.get('source_id'),'version_id':version,'content_hash':src.get('content_hash'),'observed_at':src.get('observed_at') or src.get('collected_at') or src.get('verified_at') or src.get('published_at'),'supersedes':src.get('supersedes') or src.get('supersedes_version_id'),'kind':src.get('kind'),'url':src.get('url')})
    lineages=[]; edges=[]
    for logical,items in versions.items():
        items.sort(key=lambda x:(_parse_dt(x.get('observed_at')) or datetime.min.replace(tzinfo=timezone.utc),str(x.get('version_id'))))
        for j,x in enumerate(items):
            prev=items[j-1] if j else None
            if x.get('supersedes'):
                edges.append({'logical_source_id':logical,'from_version':x.get('supersedes'),'to_version':x.get('version_id'),'relation':'EXPLICIT_SUPERSEDES'})
            elif prev and x.get('version_id')!=prev.get('version_id'):
                edges.append({'logical_source_id':logical,'from_version':prev.get('version_id'),'to_version':x.get('version_id'),'relation':'OBSERVED_VERSION_SEQUENCE_NOT_EXPLICIT_SUPERSEDES'})
        lineages.append({'logical_source_id':logical,'version_count':len(items),'versions':items,'latest_version_id':items[-1].get('version_id') if items else None})
    return {
        'status':'RESEARCH_INGESTION_COMPILED','dedup_mode':mode,'datasets':dataset_cards,
        'cross_source_duplicate_candidates':cross[:100],'entity_version_or_conflict_review':conflict_groups[:100],
        'source_version_lineage':lineages,'lineage_edges':edges,
        'principles':['Exact deterministic dedup is opt-in and limited to same-source exact row fingerprints.','Cross-source duplicates are reported, not deleted.','Version lineage is provenance; later does not automatically mean better.','Fuzzy/semantic dedup requires domain review and is outside deterministic runtime authority.'],
        '_canonical_datasets':canonical,
    }
