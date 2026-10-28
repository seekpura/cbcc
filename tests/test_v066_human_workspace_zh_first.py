from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.delivery_html import _human_cn_internal, _zh_heading, _split_h3_body
from cbcc.human_delivery import _category_contract
from cbcc.strategy_depth import _focal_numeric_values


def test_human_layer_is_chinese_first():
    assert _human_cn_internal('MARKET_DATA_NOT_SUPPLIED') == '市场数据未提供'
    assert _zh_heading('01_information_completeness_assumptions_decisions').startswith('信息完整度')
    assert '真实使用关键瞬间' in _human_cn_internal('Human Use Decisive Moment')


def test_strategy_chapter_splits_to_task_pages():
    body='intro\n### 定位\na\n### 价值主张\nb\n### Listing\nc\n'
    rows=_split_h3_body(body)
    assert [x[0] for x in rows] == ['概览','定位','价值主张','Listing']


def test_planning_category_is_not_exact_upload_category():
    c=_category_contract({'category':'beauty','category_id':None},{},{})
    assert c['status'] == '待查证'


def test_human_focal_ranges_are_supported():
    assert _focal_numeric_values('70–85mm full-frame equivalent') == [70.0,85.0]
    assert _focal_numeric_values('85mm equivalent') == [85.0]


def test_old_editorial_theme_is_superseded():
    p=Path(__file__).resolve().parents[1]/'references'/'REPORT_THEME_CONTRACT.md'
    text=p.read_text(encoding='utf-8')
    assert '对象化' in text or 'SaaS Workspace' in text
    assert 'premium long-form editorial reading' not in text
