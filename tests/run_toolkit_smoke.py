#!/usr/bin/env python3
from pathlib import Path
import sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.tools.truth import validate_sources,validate_claims
from cbcc.tools.market import analyze_market
from cbcc.tools.economics import unit_economics
from cbcc.tools.listing import compile_listing
from cbcc.tools.visual import validate_photography_contract
from cbcc.tools.ads import analyze_ads
from cbcc.tools.feedback import analyze_feedback
from cbcc.tools.experiment import evaluate_binary_experiment
from cbcc.asset_architecture import build_asset_architecture
from cbcc.asset_compiler import compile_asset_packages,validate_asset_packages
from cbcc.locale import compile_language_profiles

truth={'sources':[{'source_id':'S1','kind':'USER_PROVIDED_FACT'}],'claims':[{'claim_id':'C1','status':'APPROVED','evidence_source_ids':['S1']}]}
assert not validate_sources(truth)
assert not validate_claims(truth)
assert analyze_market([{'seller':'A','price':10,'units':2,'revenue':20,'configuration':'x'}])['row_count']==1
assert unit_economics(100,{'landed_cost':20,'platform_fee':10,'fulfillment':5,'affiliate_commission':0,'ad_cost':10,'tax':0,'refund_allowance':2})['contribution']==53
assert compile_listing({'title':'Test 30g'},{'net':'30g'},[],{'title':{'max_chars':80}})['pass']
photo={'capture_mode':'REAL_PHOTO','camera':{'focal_length_mm':85,'camera_height':'product center','focus_plane':'front label'},'composition':{'product_occupancy':{'height_pct':70}},'lighting':{'key':{'direction':'camera-left','modifier':'large diffusion'},'cct':5200,'highlight_policy':'protect label'},'color_management':{'output_space':'sRGB','product_color_fidelity':'truth-first'}}
assert validate_photography_contract(photo)['pass']
assert analyze_ads({'impressions':100,'clicks':5,'orders':1,'spend':5,'revenue':20})['metrics']['ctr']==0.05
assert analyze_feedback([{'category':'MISUNDERSTANDING'}])['issues'][0]['category']=='MISUNDERSTANDING'
assert 'p_value_two_sided' in evaluate_binary_experiment(10,100,20,100)
arch=build_asset_architecture('SMOKE',{'target_id':'T'},[],[],[{'consumer_question':'What is it?','surface':'GALLERY','family':'VISUAL','source_ids':['S1']}])
assert arch['asset_count']==1 and arch['fixed_count_authority'] is False
with tempfile.TemporaryDirectory() as td:
    compile_asset_packages(Path(td),arch['assets'],{'name':'Test'},{'platform_family':'x','site':'T','market':'Test'},{'visual_implications':[]},{'visible_copy_locales':['en-US']},compile_language_profiles('en-US'))
    assert validate_asset_packages(Path(td))['pass']
print('toolkit smoke PASS: truth + market + economics + listing + photography + ads + feedback + experiment + dynamic assets + asset package')
