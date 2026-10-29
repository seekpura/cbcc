from __future__ import annotations

from runtime.cbcc.operator_execution_board import build_operator_execution_board


def test_operator_board_turns_commerce_objects_into_direct_actions():
    board=build_operator_execution_board(
        request={'target':{'delivery_locale':'zh-CN'}},
        strategy={'sections':{'04_marketing_core_strategy':{'positioning':{'primary_conversion_proposition':'Daily oil balance without losing hydration','target_user':'oily-skin daily users','objection_reducers':['still needs hydration']}}}},
        domain={
            'listing':{'status':'READY','compiled':{'final_copy_workflow':{'status':'FINAL_COPY_WORKFLOW_COMPILED','release_counts':{'APPROVED_FINAL':1},'packages':[{'locale':'ms-MY','status':'APPROVED_FINAL','fields':[{'locale':'ms-MY','field':'title','authored_copy':'Gel Pelembap Kawalan Minyak','delivery_translation':'控油保湿凝胶','release_status':'APPROVED_FINAL','hard_issues':[],'platform_job':'identify product'}]}]}}},
            'pricing_economics_authority':{'status':'READY','scenarios':[{'sku':'K01','price':39.9,'break_even_cpa':12.0}],'missing_inputs':[]},
            'ads':{'status':'READY','priority_actions':{'P1':['test proof-first creative']}},
            'feedback':{'status':'READY','revision_actions':[{'revision_id':'REV-01','category':'EXPECTATION_GAP','routes':['IMAGE'],'recommended_change':'Add real scale evidence','frozen_layers':['Product Truth'],'verification_metric':'size-confusion review share'}]},
        },
        architecture={'assets':[{'asset_id':'IMG-01','asset_name':'Oil/Hydration Hero','asset_type':'IMAGE','surface':'GALLERY','consumer_question':'Will it balance oil without feeling drying?','strategic_job':'Make balance legible','activation_state':'TEST','visible_copy':{'target_market_copy':'KAWAL MINYAK. KEKALKAN HIDRASI.','delivery_translation':'控油，同时保持水润。'},'asset_art_direction':{'visual_carrier':'EDITORIAL_COMMERCE_IMAGE','product_presence':{'planning_state':'SUPPORTING','production_state':'PRESENT'}}}]},
        video_plan={'status':'VIDEO_PLAN_READY','assets':[]},
        paid_campaigns={'campaigns':[{'campaign_id':'C-01','objective':'conversion','test_hypothesis':'proof-first improves qualified clicks','asset_ids':['IMG-01'],'primary_metric':'CPA'}]},
        agent_next_action={'next_action':'Generate and QA IMG-01'},
        compliance={'status':'READY'},
        asset_compile={'status':'COMPILED','index':[{'asset_id':'IMG-01','path':'artifacts/asset_packages/IMG-01','provider':'image-provider'}]},
        production_run={'status':'NOT_REQUESTED'},
    )
    assert board['status']=='OPERATOR_EXECUTION_BOARD_READY'
    assert board['delivery_locale']=='zh-CN'
    assert board['commercial_thesis']['primary_conversion_proposition'].startswith('Daily oil balance')
    assert board['listing_release']['packages'][0]['fields'][0]['final_or_current_copy']=='Gel Pelembap Kawalan Minyak'
    assert board['listing_release']['packages'][0]['fields'][0]['delivery_translation_zh']=='控油保湿凝胶'
    assert board['asset_production_board']['assets'][0]['release_status']=='PRODUCTION_READY'
    assert board['asset_production_board']['assets'][0]['visible_copy']['target_market_copy']=='KAWAL MINYAK. KEKALKAN HIDRASI.'
    assert board['paid_test_queue']['campaign_tests'][0]['hypothesis']=='proof-first improves qualified clicks'
    assert board['review_revision_queue']['revisions'][0]['exact_revision']=='Add real scale evidence'
    assert board['economics_control_panel']['scenarios'][0]['break_even_cpa']==12.0
    assert board['operator_contract']['runtime_trace_is_secondary'] is True
    assert board['operator_contract']['normal_professional_choices_are_agent_owned'] is True
    assert any(row['priority']=='P0' for row in board['launch_board'])
