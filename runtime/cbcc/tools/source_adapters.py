from __future__ import annotations
from pathlib import Path
from typing import Any
from collections import defaultdict
from hashlib import sha256
import json,re
from ..io import load_tabular, apply_field_map

_SUPPORTED_DATASETS={'market_rows','market_keyword_rows','market_review_rows','competitor_listing_rows'}
_ADAPTER_FAMILIES={
    'MARKETPLACE_LISTINGS':'competitor_listing_rows',
    'SEARCH_DEMAND':'market_keyword_rows',
    'REVIEW_VOICE':'market_review_rows',
    'MARKET_SNAPSHOT':'market_rows',
}


def _stable(v:Any)->str:
    return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),default=str)

def _hash(v:Any)->str:
    return sha256(_stable(v).encode('utf-8')).hexdigest()

def _norm_text(v:Any)->str:
    s=re.sub(r'\s+',' ',str(v or '').strip().casefold())
    return re.sub(r'[^\w\s%+.-]',' ',s)

def _tokens(row:dict[str,Any], fields:list[str])->set[str]:
    blob=' '.join(_norm_text(row.get(f)) for f in fields if row.get(f) not in (None,''))
    return {x for x in blob.split() if len(x)>=2}

def _jaccard(a:set[str],b:set[str])->float:
    if not a or not b: return 0.0
    return len(a&b)/len(a|b)

def _key(row:dict[str,Any], keys:list[str])->str|None:
    vals=[]
    for k in keys:
        if row.get(k) in (None,''): return None
        vals.append(str(row.get(k)))
    return '|'.join(vals)

def _rows_from_spec(spec:dict[str,Any])->list[dict[str,Any]]:
    if isinstance(spec.get('rows'),list): rows=[dict(x) for x in spec.get('rows') if isinstance(x,dict)]
    elif spec.get('file'):
        rows=load_tabular(Path(spec['file']),spec.get('sheet'))
    else: rows=[]
    return apply_field_map(rows,spec.get('field_map'))

def _semantic_review(rows:list[dict[str,Any]], fields:list[str], threshold:float=0.88, max_pairs:int=200)->list[dict[str,Any]]:
    """Report likely near duplicates. Never delete or merge rows."""
    token_rows=[_tokens(r,fields) for r in rows]
    out=[]
    # Bound deterministic O(n^2) review work; large datasets should pre-bucket upstream.
    limit=min(len(rows),500)
    for i in range(limit):
        for j in range(i+1,limit):
            sim=_jaccard(token_rows[i],token_rows[j])
            if sim>=threshold and token_rows[i] and token_rows[j]:
                out.append({'row_index_a':i,'row_index_b':j,'similarity':round(sim,4),'status':'SEMANTIC_NEAR_DUPLICATE_REVIEW','decision':'REPORT_ONLY_NEVER_AUTO_DELETE','why':'Lexical similarity can reflect copied listings, syndication, templating or legitimate repeated facts. Human/domain review is required before merge/delete.'})
                if len(out)>=max_pairs: return out
    return out

def compile_source_adapters(adapter_specs:list[dict[str,Any]]|None=None, previous_state:dict[str,Any]|None=None)->dict[str,Any]:
    """Normalize source adapters and compile an incremental refresh change-set.

    This runtime does not call remote systems. Adapters consume rows/files already supplied by the host.
    ``previous_state`` is an optional prior adapter snapshot used only for deterministic change detection.
    """
    previous_state=previous_state or {}; prev_by_id={x.get('adapter_id'):x for x in previous_state.get('adapters',[]) or [] if x.get('adapter_id')}
    merged=defaultdict(list); cards=[]; source_records=[]
    for seq,spec in enumerate(adapter_specs or []):
        if not isinstance(spec,dict): continue
        aid=str(spec.get('adapter_id') or f'ADAPTER-{seq+1}')
        family=str(spec.get('adapter_family') or spec.get('family') or '').upper()
        dataset=str(spec.get('dataset') or _ADAPTER_FAMILIES.get(family) or '')
        if dataset not in _SUPPORTED_DATASETS:
            cards.append({'adapter_id':aid,'dataset':dataset,'status':'UNSUPPORTED_DATASET','supported_datasets':sorted(_SUPPORTED_DATASETS)})
            continue
        rows=_rows_from_spec(spec)
        defaults=spec.get('row_defaults') or {}
        source_id=spec.get('source_id')
        enriched=[]
        for r in rows:
            row={**defaults,**r}
            if source_id and row.get('source_id') in (None,''): row['source_id']=source_id
            enriched.append(row)
        keys=spec.get('primary_key') or spec.get('primary_keys') or []
        if isinstance(keys,str): keys=[keys]
        updated_field=spec.get('updated_at_field') or spec.get('observed_at_field')
        cursor_field=spec.get('cursor_field') or updated_field
        prev_checkpoint=((prev_by_id.get(aid) or {}).get('checkpoint') or {})
        previous_cursor=spec.get('previous_cursor') if spec.get('previous_cursor') not in (None,'') else prev_checkpoint.get('next_cursor')
        current_index={}
        unresolved_keys=0
        for i,r in enumerate(enriched):
            rk=_key(r,keys) if keys else None
            if rk is None:
                unresolved_keys += 1
                rk=f'ROW-{i}:{_hash(r)[:16]}'
            current_index[rk]={'row_hash':_hash(r),'updated_at':r.get(updated_field) if updated_field else None,'row':r}
        prev=prev_by_id.get(aid) or {}; prev_index=prev.get('_row_index') or {}
        added=[]; changed=[]; unchanged=[]; removed=[]
        for rk,cur in current_index.items():
            old=prev_index.get(rk)
            if not old: added.append(rk)
            elif old.get('row_hash')!=cur.get('row_hash'): changed.append(rk)
            else: unchanged.append(rk)
        for rk in prev_index:
            if rk not in current_index: removed.append(rk)
        # Incremental refresh means the supplied batch represents changes unless host explicitly marks a full snapshot.
        refresh_mode=str(spec.get('refresh_mode') or 'FULL_SNAPSHOT').upper()
        if refresh_mode=='INCREMENTAL_BATCH' and prev_index:
            combined={k:v.get('row') for k,v in prev_index.items() if v.get('row') is not None}
            for k,v in current_index.items(): combined[k]=v['row']
            for k in spec.get('deleted_keys') or []: combined.pop(str(k),None)
            analytical_rows=list(combined.values())
        else:
            analytical_rows=enriched
        merged[dataset].extend(analytical_rows)
        semantic_fields=spec.get('semantic_duplicate_fields') or []
        if isinstance(semantic_fields,str): semantic_fields=[semantic_fields]
        near=_semantic_review(analytical_rows,semantic_fields,float(spec.get('semantic_duplicate_threshold') or 0.88)) if semantic_fields else []
        watermark=None
        if updated_field:
            vals=[str(r.get(updated_field)) for r in enriched if r.get(updated_field) not in (None,'')]
            watermark=max(vals) if vals else None
        cursor_vals=[str(r.get(cursor_field)) for r in enriched if cursor_field and r.get(cursor_field) not in (None,'')]
        next_cursor=(spec.get('next_cursor') if spec.get('next_cursor') not in (None,'') else (max(cursor_vals) if cursor_vals else previous_cursor))
        checkpoint={
            'adapter_id':aid,'adapter_family':family or None,'dataset':dataset,'previous_cursor':previous_cursor,'next_cursor':next_cursor,
            'cursor_field':cursor_field,'high_watermark':watermark,'batch_id':spec.get('batch_id'),'page_token':spec.get('page_token'),
            'has_more':spec.get('has_more'),'refresh_mode':refresh_mode,'input_rows':len(enriched),
            'principle':'Checkpoint/cursor metadata records host-supplied pagination progress. It is not proof that the upstream source was fully enumerated.'
        }
        card={'adapter_id':aid,'adapter_family':family or None,'dataset':dataset,'status':'ADAPTER_COMPILED','refresh_mode':refresh_mode,'input_rows':len(enriched),'analytical_rows':len(analytical_rows),'primary_key':keys,'updated_at_field':updated_field,'high_watermark':watermark,'unresolved_primary_keys':unresolved_keys,'change_set':{'added':added[:1000],'changed':changed[:1000],'unchanged_count':len(unchanged),'removed':removed[:1000]},'semantic_near_duplicate_review':near,'semantic_duplicate_policy':'REPORT_ONLY_NEVER_AUTO_DELETE','source_id':source_id,'source_kind':spec.get('source_kind'),'schema_map':spec.get('field_map') or {},'checkpoint':checkpoint,'adapter_contract':{'family':family or 'GENERIC','dataset':dataset,'supports_cursor':bool(cursor_field),'remote_execution':False,'input_authority':'HOST_SUPPLIED_ROWS_OR_FILE'},'_row_index':current_index}
        cards.append(card)
        src=spec.get('source_record')
        if isinstance(src,dict): source_records.append({**src,**({'source_id':source_id} if source_id and not src.get('source_id') else {})})
    public_cards=[]
    for c in cards:
        public_cards.append({k:v for k,v in c.items() if k!='_row_index'})
    state_cards=[]
    for c in cards:
        state_cards.append(c)
    return {
        'status':'SOURCE_ADAPTERS_COMPILED' if cards else 'NO_SOURCE_ADAPTERS',
        'adapter_families':_ADAPTER_FAMILIES,
        'adapters':public_cards,
        'refresh_state':{'adapters':state_cards,'checkpoints':{c.get('adapter_id'):c.get('checkpoint') for c in state_cards if c.get('adapter_id')}},
        'datasets':dict(merged),
        'source_records':source_records,
        'principles':[
            'Adapters map supplied host data into explicit research datasets; runtime does not silently scrape or invent rows.',
            'Incremental refresh preserves previous keyed rows only when the adapter explicitly declares INCREMENTAL_BATCH.',
            'Semantic near-duplicate detection is review-only and never deletes evidence automatically.',
            'A high-watermark is provenance metadata, not proof that the upstream source is complete or fresh.',
            'Cursor/checkpoint state is resumability metadata. Hosts must still declare source scope, page coverage and completion semantics.'
        ]
    }
