from runtime.cbcc.commerce_decision_context import compile_commerce_decision_context

def test_context_keeps_real_values_not_only_status_counts():
    ctx=compile_commerce_decision_context(domain={
        'market': {'price_bands':[{'min':20,'max':40}], 'customer_voice':['easy to use']},
        'pricing_economics_authority': {'pricing_decision':{'decision':35,'why':'explicit economics'}, 'scenarios':[{'price':35,'break_even_cpa':12}]},
        'listing': {'compiled': {'objection_resolution_plan':['size uncertainty']}},
        'ads': {'diagnosis':[{'route':'CLICK_PACKAGE'}]},
        'feedback': {'issues':['usage confusion']},
    })
    assert ctx['market']['price_bands'][0]['max']==40
    assert ctx['pricing_economics']['scenarios'][0]['break_even_cpa']==12
    assert ctx['listing']['objections']==['size uncertainty']
    assert ctx['ads']['diagnosis'][0]['route']=='CLICK_PACKAGE'
    assert ctx['reviews']['issues']==['usage confusion']
