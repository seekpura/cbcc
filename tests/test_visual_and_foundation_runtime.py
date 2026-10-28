from pathlib import Path
import sys,pytest
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.assets import FoundationAssetRecord,required_foundation_roles
from cbcc.tools.visual import validate_photography_contract,validate_visual_semantics

def good_contract(): return {
 'capture_mode':'REAL_PHOTO',
 'camera':{'focal_length_mm':85,'camera_height':'product center + 5cm','focus_plane':'front label plane'},
 'composition':{'product_occupancy':{'height_pct':70},'negative_space':{'left_pct':40}},
 'lighting':{'key':{'direction':'camera-left 35deg','modifier':'120cm diffusion'},'cct':5200,'highlight_policy':'protect printed label and glossy shoulder'},
 'color_management':{'output_space':'sRGB','product_color_fidelity':'packaging truth has priority over campaign grade'},
 'cmf':{'color':'brand-authentic green','material':'coated carton','finish':'satin'},
 'human':None}

def test_photography_contract_has_machine_precision_gate():
    o=validate_photography_contract(good_contract()); assert o['pass'] and o['precision_level']=='RELEVANCE_READY'
    # Modifier is no longer a universal mandatory field; do not force fake shoot precision when it is not required.
    flexible=good_contract(); del flexible['lighting']['key']['modifier']; assert validate_photography_contract(flexible)['pass']
    # A dimension that is actually active for truth preservation remains a hard contract.
    bad=good_contract(); del bad['color_management']['product_color_fidelity']; assert not validate_photography_contract(bad)['pass']

def test_visual_semantics_positive_conditional_model():
    o=validate_visual_semantics([{'element':'tea tree leaf','decision':'CONDITIONAL','strategic_relevance':'Use only for a verified tea-tree ingredient story when this asset needs ingredient recognition.'}]); assert o['pass']

def test_foundation_asset_lifecycle_cannot_fake_master_lock():
    a=FoundationAssetRecord('FND-01','PRODUCT_FRONT_MASTER',product_fidelity='LOCKED_PIXEL')
    a.transition('PLAN_LOCKED')
    with pytest.raises(ValueError): a.transition('SOURCE_BOUND')
    a.transition('SOURCE_BOUND',source_ids=['SRC-PRODUCT-FRONT'])
    a.transition('MASTER_PRODUCED',output_path='masters/front.tif')
    with pytest.raises(ValueError): a.transition('MASTER_QA_LOCKED',qa={'pass':False})
    a.transition('MASTER_QA_LOCKED',qa={'pass':True,'identity':'PASS','color':'PASS'})
    assert a.state=='MASTER_QA_LOCKED'

def test_foundation_roles_are_need_driven_not_fixed_list():
    assert required_foundation_roles({'front':True,'cutout':True})==['PRODUCT_FRONT_MASTER','CUTOUT_MASTER']
