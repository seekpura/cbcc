from __future__ import annotations

from pathlib import Path


def test_asset_art_direction_is_the_single_source_for_card_and_both_prompts():
    from runtime.cbcc.commercial_continuity_bootstrap import install
    install()
    from runtime.cbcc import prompt_compiler

    asset={
        'asset_id':'G08','asset_name':'三步使用法','asset_type':'IMAGE','surface':'TIKTOK_GALLERY','family':'HOW_TO',
        'product_presence':{'planning_state':'REQUIRED','presence_why':'usage demonstration needs the pack'},
        'product_fidelity':'REFERENCE_GUIDED_NATIVE_LOCK',
        'visible_copy':{
            'copy_render_route':'MODEL_RENDER_INTEGRATED',
            'primary_locale':'ms-MY',
            'target_copy':'3 LANGKAH MUDAH',
            'english_baseline':'3 SIMPLE STEPS',
            'chinese_meaning':'3步简单使用',
        },
        'asset_art_direction':{
            'consumer_question':'怎么用？','purchase_barrier':'步骤看起来复杂','entry_state':'uncertain',
            'target_belief':'三步即可完成','strategic_job':'降低使用摩擦','incremental_information':'三步动作连续关系',
            'business_hypothesis':'连续动作比三张卡片更易理解','success_metric':'PDP CVR / FAQ reduction',
            'visual_carrier':'continuous gesture sequence','subject':'adult hand + K01 tube','action':'press pump then spread gently',
            'environment':'warm-white vanity','props':['towel edge'],'composition':'horizontal continuous action path',
            'evidence_hierarchy':'usage + daytime sun-protection reminder','copy_render_route':'MODEL_RENDER_INTEGRATED',
            'camera_position':{'working_distance':'1.2m','camera_height':'20cm above surface','pitch':'15° top-down','shot_size':'medium close-up','perspective':'natural'},
            'focal_length_mm':'60mm','focus_dof':{'focus_plane':'hand + pump contact','aperture':'f/7.1','dof':'hands and pump crisp'},
            'lighting':{'key':'large soft key from upper left','fill':'neutral bounce','cct':'5200K','light_ratio':'2:1','prelight':'verify hand/product highlights'},
            'cmf':{'material':'warm-white stone + clear pump','finish':'satin/matte','palette_hex':['#F7F6F1','#0B3D2E']},
            'output_surface':'1600×1600 sRGB','portfolio_rhythm_delta':'action sequence after lifestyle still',
            'typography':{'family':'neo-grotesk','weight':'700/500','hierarchy':'headline > steps > caution','safe_zone':'mobile safe area'},
        },
    }
    out=prompt_compiler.compile_asset_prompt(
        asset,
        product={'name':'K01'},
        target={'market':'Malaysia','platform_family':'TikTok Shop','site':'MY','category':'Beauty'},
        culture={},
        language_contract={'primary_locale':'ms-MY'},
    )
    card=out['design_card']
    assert (card['commerce_task']['consumer_question']) == '怎么用？'
    assert str(card['composition_camera'].get('focal_length_mm')) == '60mm'
    assert '15°' in str(card['composition_camera'])
    assert 'f/7.1' in str(card['composition_camera'])
    assert '5200K' in str(card['lighting_material_cmf'])
    assert 'neutral bounce' in str(card['lighting_material_cmf'])
    assert '1600×1600 sRGB' in str(card)
    for token in ('60mm','f/7.1','15°','5200K','neutral bounce','1600×1600 sRGB'):
        assert token in out['prompt_cn'], token
        assert token in out['prompt_en'], token
    lineage=out.get('canonical_prompt_lineage') or {}
    assert lineage.get('canonical_art_direction_sha256')
    assert lineage.get('prompt_cn_source_sha256') == lineage.get('canonical_art_direction_sha256')
    assert lineage.get('prompt_en_source_sha256') == lineage.get('canonical_art_direction_sha256')


def test_human_workspace_positive_projection_exposes_complete_objects_and_real_tools(tmp_path:Path):
    from runtime.cbcc.canonical_human_workspace_projection import apply_canonical_human_projection_to_existing_html
    html=tmp_path/'index.html'
    html.write_text('''<!doctype html><html><body><input id="search" placeholder="搜索资产 / 配方 / 风险 / Hook…"><div id="searchResults"></div><div id="content"></div><script>
const DATA={}; function esc(x){return String(x??'')} function section(x){return '<h2>'+x+'</h2>'} function table(){return ''}
function malaysia(){return ''} function campaign(){return ''} function universe(){return ''} function evidence(){return ''} function assetDetail(){return ''}
function render(){} function copyText(t){navigator.clipboard.writeText(t)}
</script></body></html>''',encoding='utf-8')
    data={
      'listing':{
        'title':{'bm':'BM TITLE','en':'EN TITLE','cn':'中文标题'},'description_bm':'BM DESC','description_en':'EN DESC UNIQUE','description_cn':'中文描述',
        'key_points':[{'bm':'BM KP','en':'EN KP','cn':'中文卖点'}],
        'attributes':{'Brand':'KIYUU','Net Content':'30g'},
        'package_contents':{'bm':'BM BOX','en':'EN BOX','cn':'中文实收'},
        'faq':[{'q_bm':'FAQ BM Q','a_bm':'FAQ BM A','cn':'FAQ 中文'}],
      },
      'market':{'platform_rules':[{'rule':'LISTING ACCURACY','status':'EVIDENCED','effect':'accurate','source':'TikTok'}], 'why':{'platform':'WHY PLATFORM','region':'WHY REGION','audience':'WHY AUDIENCE','race_ethnicity_culture':'WHY CULTURE'}},
      'strategy':{'strategy':{'value_proposition':'VALUE PROP','message_hierarchy':['M1','M2'],'priority_tradeoff':[{'level':'P0','keep':'KEEP P0','defer':'CUT P0','why':'WHY P0','restore':'RESTORE'}]}},
      'visual':{'palette':{'forest':'#0B3D2E'},'contrast':'HIGH CONTRAST RULE','typography':'TYPE RULE','platform':'1600×1600 sRGB','inclusive':'INCLUSIVE RULE','shot_list':['SHOT ONE']},
      'content':{'rows':[{'surface':'TikTok','audience':'adult','topic':'oil balance','hook':'HOOK','structure':'STRUCT','visual':'VISUAL','cta':'CTA','metric':'CTR','race':'Communication','culture':'CULTURE CHECK','dimension':'1080×1920','duration':'15s','cover':'COVER RULE','subtitle':'BM SUB','music':'MUSIC RIGHTS','traffic':'PAID','landing':'PDP','attribution':'UTM','why':'WHY'}]},
      'race':{'rows':[{'stage':'Research','objective':'OBJ','actions':['ACT'],'outputs':['OUT'],'platform':'TikTok Shop MY','culture':'CULTURE','metric':'KPI','why':'WHY'}]},
      'culture':{'rows':[{'dimension':'族裔文化','status':'CHECK','basis':'BASIS','inclusive':'INCLUSIVE','risk':'RISK','action':'ACTION','script_check':'SCRIPT CHECK','casting_check':'CAST CHECK','wardrobe_grooming_check':'WARDROBE CHECK','color_check':'COLOR CHECK','cta_check':'CTA CHECK','verification_result':'RESULT','modification_action':'MODIFY'}]},
      'compliance':{'other_risks':[{'risk':'RISK UNIQUE','severity':'P1','action':'REPAIR'}]},
      'ads':{'objective':'ADS OBJECTIVE','economics_boundary':'ADS ECON BOUNDARY','landing':'ADS LANDING','attribution':'ADS ATTRIBUTION','failure_diagnosis':['ADS FAILURE RULE'],'tests':[]},
      'sources':{'sources':[{'id':'S1','type':'official','title':'SOURCE TITLE','url':'https://example.test/source','use':'SOURCE USE','recency':'current'}]},
      'assets':[{'id':'G01','card':{'title_cn':'资产','family':'Gallery','surface':'TikTok','visual_carrier':'VISUAL CARRIER','product_presence':{'state':'REQUIRED','role':'PRODUCT ROLE','why':'PRODUCT WHY'},'output_surface':'1600×1600','culture_inclusion':'ASSET CULTURE','truth_boundary':'TRUTH BOUNDARY'},'prompt_cn':'PROMPT CN UNIQUE','prompt_en':'PROMPT EN UNIQUE','visible_copy':'VISIBLE COPY UNIQUE','production_notes':'PRODUCTION NOTES UNIQUE','review':{}}]
    }
    result=apply_canonical_human_projection_to_existing_html(html,data)
    assert result['status']=='PASS'
    text=html.read_text(encoding='utf-8')
    for token in ('EN DESC UNIQUE','BM KP','EN KP','Brand','BM BOX','FAQ BM Q','LISTING ACCURACY','WHY PLATFORM','VALUE PROP','KEEP P0','#0B3D2E','SHOT ONE','COVER RULE','MUSIC RIGHTS','TikTok Shop MY','SCRIPT CHECK','CAST CHECK','WARDROBE CHECK','COLOR CHECK','CTA CHECK','RISK UNIQUE','ADS OBJECTIVE','ADS FAILURE RULE','https://example.test/source','VISUAL CARRIER','PRODUCT ROLE','PRODUCT WHY','TRUTH BOUNDARY'):
        assert token in text, token
    assert 'CBCC_GLOBAL_SEARCH_INDEX' in text
    assert 'PROMPT CN UNIQUE' in text and 'PROMPT EN UNIQUE' in text
    assert 'data-copy-payload' in text
    assert 'navigator.clipboard.writeText' in text
