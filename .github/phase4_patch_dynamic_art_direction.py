from pathlib import Path

video_path = Path('runtime/cbcc/video_creator.py')
video = video_path.read_text(encoding='utf-8')

if 'from copy import deepcopy\n' not in video:
    video = video.replace('from typing import Any\n', 'from typing import Any\nfrom copy import deepcopy\n', 1)

build_start = video.index('def build_video_creator_plan(')
rows_needle = '        rows.append({\n'
rows_pos = video.index(rows_needle, build_start)
authorship_block = '''        authored_motion_fields=[k for k in ('shots','narrative_carrier') if k in j and j.get(k) not in (None,'',[],{})]\n        authored_timing_fields=(['duration_seconds'] if j.get('shots') and 'duration_seconds' in j and j.get('duration_seconds') not in (None,'',[],{}) else [])\n        authored_audio_fields=[k for k in ('voice_locale','subtitle_locales','voiceover_style','audio') if k in j and j.get(k) not in (None,'',[],{})]\n        dynamic_authorship={\n            'motion':bool(j.get('shots')),\n            'timing':bool(j.get('shots')) and bool(authored_timing_fields),\n            'audio':bool(authored_audio_fields),\n        }\n        authored_dynamic_fields={\n            'motion':authored_motion_fields if dynamic_authorship['motion'] else [],\n            'timing':authored_timing_fields if dynamic_authorship['timing'] else [],\n            'audio':authored_audio_fields if dynamic_authorship['audio'] else [],\n        }\n'''
if 'authored_dynamic_fields={' not in video[build_start:rows_pos]:
    video = video[:rows_pos] + authorship_block + video[rows_pos:]

old_tail = "            'creator_contract':creator_contract,'live_contract':live_contract,'source_asset_id':source.get('asset_id')\n        })"
new_tail = "            'creator_contract':creator_contract,'live_contract':live_contract,'source_asset_id':source.get('asset_id'),\n            'audio':deepcopy(j.get('audio')) if isinstance(j.get('audio'),dict) else None,\n            'dynamic_art_direction_authorship':dynamic_authorship,'authored_dynamic_fields':authored_dynamic_fields,\n        })"
if old_tail in video:
    video = video.replace(old_tail, new_tail, 1)
elif "'dynamic_art_direction_authorship':dynamic_authorship" not in video:
    raise SystemExit('video plan row shape changed; refusing blind patch')

helper = r'''

def project_dynamic_art_direction_to_assets(architecture:dict[str,Any], video_plan:dict[str,Any])->dict[str,Any]:
    """Project only explicitly authored dynamic decisions back into the same asset Art Direction.

    Runtime fallback shots/default locale/default duration remain execution conveniences only. They
    are never promoted to creative authority. Existing visual-master, product, photography and
    inclusion fields are merged by addition, never replaced.
    """
    out=deepcopy(architecture or {})
    by_asset={
        row.get('source_asset_id'):row
        for row in (video_plan or {}).get('assets') or []
        if isinstance(row,dict) and row.get('source_asset_id')
    }
    assets=[]
    for raw in out.get('assets') or []:
        asset=deepcopy(raw)
        row=by_asset.get(asset.get('asset_id'))
        if not row:
            assets.append(asset)
            continue
        authored=row.get('dynamic_art_direction_authorship') or {}
        fields=row.get('authored_dynamic_fields') or {}
        art=deepcopy(asset.get('asset_art_direction') or {})
        missing=[]
        if authored.get('motion'):
            art['motion']={
                'authority':'EXPLICIT_AGENT_VIDEO_JOB',
                'video_id':row.get('video_id'),
                'family':row.get('family'),
                'surface':row.get('surface'),
                'narrative_carrier':row.get('narrative_carrier'),
                'shots':deepcopy(row.get('shots') or []),
                'authored_fields':deepcopy(fields.get('motion') or []),
            }
        else:
            missing.append('motion')
        if authored.get('timing'):
            art['timing']={
                'authority':'EXPLICIT_AGENT_VIDEO_JOB',
                'duration_seconds':row.get('duration_seconds'),
                'shot_timing':deepcopy(row.get('timing') or []),
                'authored_fields':deepcopy(fields.get('timing') or []),
            }
        else:
            missing.append('timing')
        if authored.get('audio'):
            audio={'authority':'EXPLICIT_AGENT_VIDEO_JOB','authored_fields':deepcopy(fields.get('audio') or [])}
            for key in fields.get('audio') or []:
                if key=='audio' and isinstance(row.get('audio'),dict):
                    audio.update(deepcopy(row.get('audio') or {}))
                elif key in row and row.get(key) not in (None,'',[],{}):
                    audio[key]=deepcopy(row.get(key))
            art['audio']=audio
        else:
            missing.append('audio')
        asset['asset_art_direction']=art
        asset['dynamic_art_direction_status']='AUTHORED' if not missing else 'TO_VERIFY'
        asset['dynamic_art_direction_missing']=missing
        asset['dynamic_art_direction_source_video_id']=row.get('video_id')
        asset['runtime_may_invent_missing_dynamic_art_direction']=False
        assets.append(asset)
    out['assets']=assets
    return out
'''
if 'def project_dynamic_art_direction_to_assets(' not in video:
    insert_at = video.index('\ndef _vmerge(', build_start)
    video = video[:insert_at] + helper + video[insert_at:]

video_path.write_text(video, encoding='utf-8')

compiler_path = Path('runtime/cbcc/compiler.py')
compiler = compiler_path.read_text(encoding='utf-8')
old_import = 'from .video_creator import build_video_creator_plan, enrich_video_plan_with_strategy'
new_import = 'from .video_creator import build_video_creator_plan, enrich_video_plan_with_strategy, project_dynamic_art_direction_to_assets'
if old_import in compiler:
    compiler = compiler.replace(old_import, new_import, 1)
elif 'project_dynamic_art_direction_to_assets' not in compiler.split('\n', 60):
    raise SystemExit('video_creator import shape changed; refusing blind patch')

build_call = "    video_plan=build_video_creator_plan(request.get('project_id','project'),objects,questions,lang.to_dict(),request.get('video_jobs'),assets=architecture.get('assets'),creative_council=council)\n"
projection_call = '    architecture=project_dynamic_art_direction_to_assets(architecture,video_plan)\n'
aap_needle = "    aap=_write(p/'artifacts/asset_architecture.json',architecture); st.set_gate('ASSET_ARCHITECTURE','READY_REVIEW',[aap],architecture); st.checkpoint('ASSET_ARCHITECTURE','READY_REVIEW')\n"
if projection_call not in compiler:
    if aap_needle not in compiler:
        raise SystemExit('asset architecture write/gate shape changed; refusing blind patch')
    compiler = compiler.replace(aap_needle, build_call + projection_call + aap_needle, 1)

# Reuse the same base plan later instead of rebuilding after the architecture authority was frozen.
positions=[]
start=0
while True:
    pos=compiler.find(build_call,start)
    if pos<0: break
    positions.append(pos); start=pos+len(build_call)
if len(positions)>1:
    second=positions[1]
    compiler=compiler[:second]+compiler[second+len(build_call):]
elif len(positions)==0:
    raise SystemExit('base video plan call missing after projection patch')

# Structural guard: the authority write must occur after the base video plan and its projection.
video_pos=compiler.index(build_call)
projection_pos=compiler.index(projection_call,video_pos)
aap_pos=compiler.index(aap_needle,projection_pos)
if not (video_pos < projection_pos < aap_pos):
    raise SystemExit('dynamic Art Direction projection is not before ASSET_ARCHITECTURE write/gate')

compiler_path.write_text(compiler, encoding='utf-8')
