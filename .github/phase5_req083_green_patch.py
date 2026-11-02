from pathlib import Path

path=Path('runtime/cbcc/video_creator.py')
text=path.read_text(encoding='utf-8')

old="""        authored_motion_fields=[k for k in ('shots','narrative_carrier') if k in j and j.get(k) not in (None,'',[],{})]
        authored_timing_fields=(['duration_seconds'] if j.get('shots') and 'duration_seconds' in j and j.get('duration_seconds') not in (None,'',[],{}) else [])
        authored_audio_fields=[k for k in ('voice_locale','subtitle_locales','voiceover_style','audio') if k in j and j.get(k) not in (None,'',[],{})]
        dynamic_authorship={
            'motion':bool(j.get('shots')),
            'timing':bool(j.get('shots')) and bool(authored_timing_fields),
            'audio':bool(authored_audio_fields),
        }
"""
new="""        # Only Agent-authored temporal decisions become canonical authority. Runtime fallback
        # shots/default locale/default duration remain execution conveniences and never gain authorship.
        authored_motion_fields=[
            k for k in (
                'shots','narrative_carrier','subject_motion','camera_motion','transitions',
                'product_identity_continuity','first_frame_logic','cover_logic',
            )
            if k in j and j.get(k) not in (None,'',[],{})
        ]
        authored_timing_fields=[
            k for k in ('text_timing',)
            if k in j and j.get(k) not in (None,'',[],{})
        ]
        if j.get('shots') and 'duration_seconds' in j and j.get('duration_seconds') not in (None,'',[],{}):
            authored_timing_fields.insert(0,'duration_seconds')
        authored_audio_fields=[
            k for k in ('voice_locale','subtitle_locales','voiceover_style','vo_role','subtitle_role','audio')
            if k in j and j.get(k) not in (None,'',[],{})
        ]
        dynamic_authorship={
            'motion':bool(authored_motion_fields),
            'timing':bool(authored_timing_fields),
            'audio':bool(authored_audio_fields),
        }
"""
if text.count(old)!=1:
    raise SystemExit(f'authorship block mismatch: {text.count(old)}')
text=text.replace(old,new,1)

old="""            'creator_contract':creator_contract,'live_contract':live_contract,'source_asset_id':source.get('asset_id'),
            'audio':deepcopy(j.get('audio')) if isinstance(j.get('audio'),dict) else None,
            'dynamic_art_direction_authorship':dynamic_authorship,'authored_dynamic_fields':authored_dynamic_fields,
"""
new="""            'creator_contract':creator_contract,'live_contract':live_contract,'source_asset_id':source.get('asset_id'),
            'subject_motion':deepcopy(j.get('subject_motion')),'camera_motion':deepcopy(j.get('camera_motion')),
            'transitions':deepcopy(j.get('transitions')),'product_identity_continuity':deepcopy(j.get('product_identity_continuity')),
            'first_frame_logic':deepcopy(j.get('first_frame_logic')),'cover_logic':deepcopy(j.get('cover_logic')),
            'text_timing':deepcopy(j.get('text_timing')),'vo_role':deepcopy(j.get('vo_role')),'subtitle_role':deepcopy(j.get('subtitle_role')),
            'audio':deepcopy(j.get('audio')) if isinstance(j.get('audio'),dict) else None,
            'dynamic_art_direction_authorship':dynamic_authorship,'authored_dynamic_fields':authored_dynamic_fields,
"""
if text.count(old)!=1:
    raise SystemExit(f'row block mismatch: {text.count(old)}')
text=text.replace(old,new,1)

old="""        if authored.get('motion'):
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
"""
new="""        if authored.get('motion'):
            motion={
                'authority':'EXPLICIT_AGENT_VIDEO_JOB',
                'video_id':row.get('video_id'),
                'family':row.get('family'),
                'surface':row.get('surface'),
                'authored_fields':deepcopy(fields.get('motion') or []),
            }
            for key in fields.get('motion') or []:
                if key=='shots':
                    motion['shots']=deepcopy(row.get('shots') or [])
                elif key=='narrative_carrier':
                    motion['narrative_carrier']=row.get('narrative_carrier')
                elif key in row and row.get(key) not in (None,'',[],{}):
                    motion[key]=deepcopy(row.get(key))
            art['motion']=motion
        else:
            missing.append('motion')
        if authored.get('timing'):
            timing_contract={
                'authority':'EXPLICIT_AGENT_VIDEO_JOB',
                'authored_fields':deepcopy(fields.get('timing') or []),
            }
            if 'duration_seconds' in (fields.get('timing') or []):
                timing_contract['duration_seconds']=row.get('duration_seconds')
                timing_contract['shot_timing']=deepcopy(row.get('timing') or [])
            for key in fields.get('timing') or []:
                if key!='duration_seconds' and key in row and row.get(key) not in (None,'',[],{}):
                    timing_contract[key]=deepcopy(row.get(key))
            art['timing']=timing_contract
        else:
            missing.append('timing')
"""
if text.count(old)!=1:
    raise SystemExit(f'projection block mismatch: {text.count(old)}')
text=text.replace(old,new,1)

path.write_text(text,encoding='utf-8')
print('REQ-083 GREEN patch applied')
