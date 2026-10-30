from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping
import json, re

from .canonical_human_workspace_projection import apply_canonical_human_projection_to_existing_html

MARKER='CBCC_CANONICAL_HUMAN_COMPLETION_V0670'


def _extract_data(text:str)->dict[str,Any]:
    for marker in ('const CBCC_CANONICAL_HUMAN=','const DATA='):
        i=text.find(marker)
        if i<0:continue
        start=i+len(marker)
        while start<len(text) and text[start].isspace():start+=1
        try:
            value,_=json.JSONDecoder().raw_decode(text[start:])
            if isinstance(value,dict):return value
        except Exception:pass
    return {}


def _normalize_payload(data:Mapping[str,Any])->dict[str,Any]:
    out=deepcopy(dict(data))
    culture=out.get('culture')
    if isinstance(culture,dict) and isinstance(culture.get('rows'),list):
        rows=[]
        for raw in culture['rows']:
            if not isinstance(raw,dict):rows.append(raw);continue
            row=deepcopy(raw)
            if not row.get('verification_result'):
                row['verification_result']=row.get('validation_result') or row.get('result')
            if not row.get('validation_result'):
                row['validation_result']=row.get('verification_result') or row.get('result')
            if not row.get('modification_action'):
                row['modification_action']=row.get('modification') or row.get('action')
            rows.append(row)
        culture=deepcopy(culture);culture['rows']=rows;out['culture']=culture
    return out


def apply_complete_canonical_human_projection(html_path:Path|str, data:Mapping[str,Any]|None=None)->dict[str,Any]:
    path=Path(html_path)
    if not path.exists():return {'status':'NOT_FOUND','path':str(path)}
    before=path.read_text(encoding='utf-8',errors='ignore')
    payload=_normalize_payload(dict(data or {}) or _extract_data(before))
    result=apply_canonical_human_projection_to_existing_html(path,payload)
    if result.get('status')!='PASS':return result
    text=path.read_text(encoding='utf-8',errors='ignore')
    if MARKER not in text:
        # The main projector owns route design. This wrapper only adds a visible Review evidence status
        # after that renderer, so no second workspace taxonomy is introduced.
        script=r'''
<script id="cbcc-canonical-human-completion-v0670">
/* CBCC_CANONICAL_HUMAN_COMPLETION_V0670 */
(function(){
  if(typeof evidence==='function'){
    const priorEvidence=evidence;
    evidence=function(){
      const reviews=(typeof CBCC_CANONICAL_HUMAN!=='undefined'&&CBCC_CANONICAL_HUMAN.reviews)||{};
      const status=reviews.status?`<div class="notice"><b>Review evidence status：</b>${typeof esc==='function'?esc(reviews.status):String(reviews.status)}</div>`:'';
      return status+priorEvidence();
    };
  }
  if(typeof render==='function')render();
})();
</script>
'''
        text=text.replace('</body>',script+'</body>',1) if '</body>' in text else text+script
        path.write_text(text,encoding='utf-8')
    return {'status':'PASS','path':str(path),'marker':MARKER,'base_projection':result}
