from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.compiler import build_project

FULL_ASSET_FILES={'00_asset_manifest.yaml','01_strategy.md','02_visual_spec.md','03_photography_contract.json','04_layout_contract.json','05_prompt_CN.txt','06_prompt_EN.txt','07_generation_guidance.txt','08_copy.md','09_production_notes.md','10_source_trace.md','11_strategy_authority_trace.json'}

EXPECTED={
 'food_tea.json':('FOOD_BEVERAGE',{'DIETARY_FIT','TASTE_PREP','PACK_VALUE','STORAGE_FRESHNESS'},'INGREDIENT_DIETARY'),
 'electronics_powerbank.json':('ELECTRONICS',{'COMPATIBILITY','PERFORMANCE','SERVICE','PACKAGE'},'COMPATIBILITY'),
 'apparel_tshirt.json':('APPAREL_FIT',{'SIZE_SELECTION','FIT_SHAPE','MATERIAL_CARE','RETURN_RISK'},'SIZE_FIT'),
 'high_ticket_aircon.json':('HIGH_TICKET_DURABLE',{'SITE_FIT','PERFORMANCE','DELIVERY_INSTALL','SERVICE_WARRANTY','TOTAL_COST'},'DELIVERY_INSTALLATION'),
}

def _build(tmp_path,name):
    req=json.loads((ROOT/'tests/fixtures/v059_category_commerce'/name).read_text(encoding='utf-8'))
    p=tmp_path/Path(name).stem
    build_project(p,req,ROOT/'platform_packs')
    return p,req


def test_v059_category_commerce_changes_objection_proof_offer_message_and_cadence(tmp_path):
    seen_sequences=set(); seen_cadence=set(); seen_top_proof=set(); seen_families=set()
    for name,(family,expected_objections,expected_intent) in EXPECTED.items():
        p,req=_build(tmp_path,name)
        strategy=json.loads((p/'artifacts/strategy/strategy_authority.json').read_text(encoding='utf-8'))
        assert strategy['runtime_strategy_depth'].startswith(('0.5.9-','0.5.10-','0.5.11-','0.5.12-','0.5.13-','0.5.14-'))
        assert len(strategy['sections'])==9
        core=strategy['sections']['04_marketing_core_strategy']
        commerce=core['category_commerce_profile']; listing=core['listing_strategy']; pos=core['positioning']; sku=core['product_strategy']
        assert commerce['category_family']==family
        seen_families.add(family)
        keys={x['objection_key'] for x in commerce['objection_priorities']}
        assert expected_objections.issubset(keys)
        active={x['objection_key'] for x in listing['category_objection_checks'] if x['status']=='ACTIVE_CATEGORY_DECISION_RISK'}
        assert active  # project questions/product facts activate category risks rather than leaving a static handbook
        assert listing['pdp_sequence'][0]['job']==commerce['message_architecture']['sequence'][0]
        assert listing['category_proof_hierarchy'][0]['proof_type']==commerce['proof_hierarchy'][0]['proof_type']
        assert sku['category_offer_architecture']['status']=='CATEGORY_OFFER_HYPOTHESES_REQUIRE_ECONOMICS_AND_PRODUCT_FIT'
        assert sku['category_offer_architecture']['economics_validation_status'] in {'ECONOMICS_AVAILABLE_FOR_VALIDATION','ECONOMICS_NOT_SUPPLIED_DO_NOT_LOCK_OFFER'}
        assert commerce['content_cadence']['fixed_posting_frequency'] is False
        seen_sequences.add(tuple(commerce['message_architecture']['sequence']))
        seen_cadence.add(commerce['content_cadence']['model'])
        seen_top_proof.add(commerce['proof_hierarchy'][0]['proof_type'])

        arch=json.loads((p/'artifacts/asset_architecture.json').read_text(encoding='utf-8'))
        assert arch['category_family']==family
        assert any(a['decision_intent']==expected_intent for a in arch['assets'])
        idx=json.loads((p/'artifacts/asset_packages/ASSET_PACKAGE_INDEX.json').read_text(encoding='utf-8'))
        assert idx['count']==arch['asset_count']
        for row in idx['assets']:
            d=p/'artifacts/asset_packages'/row['asset_id']
            assert FULL_ASSET_FILES.issubset({x.name for x in d.iterdir()})

        matrix=strategy['sections']['06_platform_content_matrix']
        assert matrix and all(x['content_cadence']['fixed_posting_frequency'] is False for x in matrix)
        targeted=[x for x in matrix if next(a for a in arch['assets'] if a['asset_id']==x['asset_id'])['decision_intent']==expected_intent]
        assert targeted and all(x['script_structure'] for x in targeted)
        assert all(x['category_message_sequence']==commerce['message_architecture']['sequence'] for x in matrix)

        ctx=json.loads((p/'artifacts/strategy_reasoning_context.json').read_text(encoding='utf-8'))
        assert 'PROMPT-CATEGORY-COMMERCE-DEPTH' in {x['id'] for x in ctx['selected_prompts']}
        assert 'KNOW-CATEGORY-COMMERCE-DEPTH' in {x.get('id') for x in ctx['selected_knowledge'] if x.get('id')}
        assert {'CategoryCommerceProfile','ObjectionPriority','ProofHierarchy','OfferArchitecture','ContentCadence'}.issubset(set(ctx['ontology']['entities']))

    assert seen_families=={'FOOD_BEVERAGE','ELECTRONICS','APPAREL_FIT','HIGH_TICKET_DURABLE'}
    assert len(seen_sequences)==4
    assert len(seen_cadence)==4
    assert len(seen_top_proof)==4


def test_v059_category_profile_never_becomes_product_fact(tmp_path):
    p,req=_build(tmp_path,'high_ticket_aircon.json')
    strategy=json.loads((p/'artifacts/strategy/strategy_authority.json').read_text(encoding='utf-8'))
    commerce=strategy['sections']['04_marketing_core_strategy']['category_commerce_profile']
    assert 'never creates' in commerce['boundary'].lower()
    # Candidate patterns may mention financing/service bundles, but they stay hypotheses and must not leak into current product fields.
    fields=strategy['sections']['04_marketing_core_strategy']['listing_strategy']['current_fields']
    raw=json.dumps(fields,ensure_ascii=False).casefold()
    assert 'financing' not in raw and 'free installation' not in raw
