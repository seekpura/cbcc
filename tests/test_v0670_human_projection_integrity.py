from __future__ import annotations
import json
from runtime.cbcc.human_projection_integrity import audit_human_projection_html


def _html(data, renderer):
    return '<script>const DATA='+json.dumps(data,ensure_ascii=False)+';'+renderer+'</script>'


def _full_data():
    return {
      'listing':{
        'description_en':'English description','key_points':[{'bm':'a','en':'b','cn':'c'}],
        'attributes':{'Brand':'X'},'package_contents':{'bm':'x','en':'y','cn':'z'},'faq':[{'q_bm':'q','a_bm':'a','cn':'中'}],
      },
      'strategy':{'strategy':{'value_proposition':'v','message_hierarchy':['m'],'priority_tradeoff':[{'level':'P0'}]}},
      'market':{'platform_rules':[{'rule':'r'}],'why':{'platform':'p','region':'r','audience':'a','race_ethnicity_culture':'c'}},
      'visual':{'palette':{'x':'#fff'},'contrast':'c','typography':'t','platform':'p','inclusive':'i','shot_list':['s']},
      'content':{'rows':[{'cover':'c','subtitle':'s','music':'m','traffic':'t','landing':'l'}]},
      'race':{'rows':[{'stage':x,'platform':'TikTok Shop Malaysia'} for x in ('Research','Action','Communication','Evaluation')]},
      'culture':{'rows':[{'script_check':'PASS','casting_check':'PASS','wardrobe_grooming_check':'PASS','color_check':'PASS','cta_check':'PASS','validation_result':'PASS','modification_action':'NONE'}]},
      'compliance':{'other_risks':[{'risk':'r'}],'self_check':[
        {'item':'是否编造事实'},{'item':'WHY是否完整'},{'item':'文化/族裔校验'},{'item':'合规检查'},{'item':'指标是否给出'},{'item':'假设是否标注'}]},
      'ads':{'objective':'o','economics_boundary':'e','landing':'l','attribution':'a','failure_diagnosis':['f']},
      'reviews':{'status':'NO_FIRST_PARTY_REVIEW_DATA'},
      'sources':{'sources':[{'url':'https://example.com'}]},
      'assets':[{'id':'A1','card':{'visual_carrier':'v','output_surface':'1600×1600 sRGB','culture_inclusion':'c','truth_boundary':'t','product_presence':{'state':'REQUIRED','role':'hero','why':'purchase task'}}}],
    }


def test_actual_v069_style_renderer_is_incomplete_even_when_data_contains_fields():
    data=_full_data()
    renderer='''
    function malaysia(){let l=DATA.listing,m=DATA.market; return l.description_bm+l.description_cn;}
    function campaign(){return DATA.content.rows.map(x=>x.attribution)+DATA.race.rows.map(x=>x.stage);}
    function assetDetail(){let c=DATA.assets[0].card;return c.camera_optics+c.product_presence.state;}
    $('#search').addEventListener('input',e=>{let found=DATA.assets.filter(a=>JSON.stringify(a.card).includes(e.target.value));});
    function copyText(x){navigator.clipboard.writeText(x)}
    '''
    codes={x['code'] for x in audit_human_projection_html(_html(data,renderer))}
    assert 'HTML_LISTING_PROJECTION_INCOMPLETE' in codes
    assert 'HTML_STRATEGY_PROJECTION_INCOMPLETE' in codes
    assert 'HTML_MARKET_PROJECTION_INCOMPLETE' in codes
    assert 'HTML_VISUAL_PROJECTION_INCOMPLETE' in codes
    assert 'HTML_CONTENT_MATRIX_PROJECTION_INCOMPLETE' in codes
    assert 'HTML_CULTURE_PROJECTION_INCOMPLETE' in codes
    assert 'HTML_ASSET_ART_DIRECTION_PROJECTION_INCOMPLETE' in codes
    assert 'WORKSPACE_COPY_BINDING_MISSING' in codes
    assert 'WORKSPACE_SEARCH_SCOPE_INCOMPLETE' in codes


def test_complete_project_authored_renderer_can_pass_without_fixed_page_taxonomy():
    data=_full_data()
    # The checker cares about semantic consumption, not page names or fixed navigation.
    renderer='''
    function renderAny(){let l=DATA.listing,m=DATA.market,v=DATA.visual,s=DATA.strategy.strategy,a=DATA.ads;
      return l.description_en+l.key_points+l.attributes+l.package_contents+l.faq+
      s.value_proposition+s.message_hierarchy+s.priority_tradeoff+
      m.platform_rules+m.why+v.palette+v.contrast+v.typography+v.platform+v.inclusive+v.shot_list+
      DATA.content.rows.map(x=>x.cover+x.subtitle+x.music+x.traffic+x.landing)+
      DATA.race.rows.map(x=>x.platform)+DATA.culture.rows.map(x=>x.script_check+x.casting_check+x.wardrobe_grooming_check+x.color_check+x.cta_check+x.validation_result+x.modification_action)+
      DATA.compliance.other_risks+a.objective+a.economics_boundary+a.landing+a.attribution+a.failure_diagnosis+
      DATA.reviews.status+DATA.sources.sources.map(x=>x.url)+
      DATA.assets.map(a=>a.card.visual_carrier+a.card.output_surface+a.card.culture_inclusion+a.card.truth_boundary+a.card.product_presence.role+a.card.product_presence.why);
    }
    function copyText(x){navigator.clipboard.writeText(x)}
    function block(){return `<button onclick="copyText('x')">Copy</button>`}
    const workspaceSearchIndex=[DATA.listing,DATA.strategy,DATA.compliance,DATA.sources,...DATA.assets];
    $('#search').addEventListener('input',e=>workspaceSearchIndex.filter(x=>JSON.stringify(x).includes(e.target.value)));
    '''
    assert audit_human_projection_html(_html(data,renderer))==[]


def test_race_platform_and_culture_execution_columns_are_data_contracts_not_just_html_labels():
    data=_full_data();
    for row in data['race']['rows']: row.pop('platform')
    for row in data['culture']['rows']:
        row.pop('script_check');row.pop('cta_check')
    renderer='platform script_check cta_check onclick="copyText(\'x\')" WORKSPACE_SEARCH_INDEX'
    codes={x['code'] for x in audit_human_projection_html(_html(data,renderer))}
    assert 'RACE_PLATFORM_FIELD_MISSING' in codes
    assert 'CULTURE_EXECUTION_COLUMNS_MISSING' in codes
