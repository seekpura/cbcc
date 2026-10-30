from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_business_object_density_contract_exists_and_is_global():
    p = ROOT / 'references' / 'BUSINESS_OBJECT_DENSITY_MASTER_CONTRACT.md'
    assert p.exists()
    text = p.read_text(encoding='utf-8')
    required = [
        '全业务对象密度合同',
        '不是 Prompt 专项合同',
        'Product Truth', 'Market / Audience / Culture', 'Intersectionality',
        'Strategy', 'STP / JTBD / AIDA / FABE / 4P / Funnel',
        'Pricing / Economics / Offer', 'Listing / Search', 'Content Matrix',
        'Visual Master', 'Asset Universe', 'Art Direction', 'Model Prompt',
        'Video / Creator / LIVE', 'Advertising Optimization', 'Review Analysis',
        'RACE', 'Localization', 'Compliance / Risk', 'Measurement / A-B',
        'Evidence / Sources', 'Operations', 'Human Workspace',
        '中文化不得降密度', '任何模块不得摘要替代真实业务对象',
    ]
    for token in required:
        assert token in text, token


def test_each_business_domain_has_minimum_decision_depth():
    text = (ROOT / 'references' / 'BUSINESS_OBJECT_DENSITY_MASTER_CONTRACT.md').read_text(encoding='utf-8')
    required = [
        'WHAT → WHY → EVIDENCE → TRADEOFF → EXECUTION → MEASUREMENT',
        '真实卖点 / 可感知利益 / 情绪价值 / 不可宣称项',
        '需求 / 搜索 / 竞争 / 价格带 / 评论 / 差评 / 机会 / 风险',
        '平台 × 区域 × 人群 × 族裔文化',
        '族裔 × 性别 × 年龄 × 收入 × 地域',
        '定位 / 价值主张 / 信息层级 / 传播节奏',
        'Price Bands', 'Contribution', 'Break-even', 'Offer Boundary',
        '关键词 / 标题 / 卖点 / 描述 / 属性 / FAQ / Claim Mapping',
        '平台 / 人群 / 选题 / Hook / 脚本结构 / 视觉形式 / CTA / 指标 / RACE / 文化校验',
        '风格 / moodboard / 构图 / HEX / 灯光 / 摄影 / CMF / 材质 / 人物 / 场景 / Shot List',
        '消费者问题 / 购买障碍 / 目标信念 / 增量信息 / Visual Carrier / Product Presence / Business Hypothesis',
        'CN / EN / Visible Copy / Production Notes',
        'duration / beat / shot sequence / motion / subtitle / VO / audio / CTA hold',
        '受众状态 / 创意机制 / offer / landing / 经济模型 / 归因 / 测试',
        '评论结构 / 问题分类 / 购买障碍 / 退货差评 / 责任层 / 最小修复',
        'Research → Action → Communication → Evaluation',
        '语言回译 / 节日 / 支付物流 / 宗教禁忌 / 当地法规',
        'P0 / P1 / P2', 'A/B 测试', '归因', '下一步输入',
    ]
    for token in required:
        assert token in text, token


def test_v0653_builder_consumes_business_object_density_contract():
    p = ROOT / 'scripts' / 'build_plugin_dist_v0653.py'
    assert p.exists()
    text = p.read_text(encoding='utf-8')
    required = [
        'build_plugin_dist_v0652', '0.6.53',
        'BUSINESS_OBJECT_DENSITY_MASTER_CONTRACT.md',
        'business_object_density_contract_required',
        'all_business_domains_non_regression_required',
        'v0652_master_construction_preserved',
        'v0651_chinese_canonical_preserved',
        'mature_capability_ledger_preserved',
    ]
    for token in required:
        assert token in text, token


def test_release_matrix_explicitly_blocks_business_domain_thinning():
    text = (ROOT / 'references' / 'RELEASE_NON_REGRESSION_MATRIX.yaml').read_text(encoding='utf-8')
    for token in [
        'business_object_density_without_summary_collapse',
        'strategy_depth_without_framework_theater',
        'listing_depth_without_copy_stub',
        'visual_depth_without_prompt_only_substitution',
        'ads_reviews_economics_without_omission',
        'content_matrix_without_generic_topics',
    ]:
        assert token in text, token
