from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_master_construction_contract_exists_and_locks_user_hard_requirements():
    p = ROOT / 'references' / 'MASTER_CONSTRUCTION_CONTRACT.md'
    assert p.exists()
    text = p.read_text(encoding='utf-8')
    required = [
        '真实卖点', '可感知利益', '情绪价值', '不可宣称项',
        'A=检测报告/官方认证/可复现实测',
        'B=供应链或成分机理支持',
        'C=主观体验/待验证',
        '平台 × 区域 × 人群 × 族裔文化',
        '族裔 × 性别 × 年龄 × 收入 × 地域',
        '视觉包容性摄影为 P0',
        '尺寸、时长、封面、字幕、音乐版权、流量机制、CTA、落地页、UTM 与归因',
        '语言回译、节日日历、支付物流、宗教禁忌、当地法规',
        'P0=不做会翻车', 'P1=影响效果', 'P2=加分项',
        '依据 + 取舍',
        'RACE = Research → Action → Communication → Evaluation',
        'STP + JTBD', 'AIDA / FABE', '4P / 内容漏斗',
        'RACE传播框架执行表', '族裔文化适配检查表',
        '信息审计 → 待确认清单 → 明确假设 → 再输出',
        '假设与决策日志',
        '视觉总策略与拍摄执行清单',
        '分平台内容矩阵表',
        '升级只能做加法',
        '修复一个维度不得压缩另一个维度',
    ]
    for token in required:
        assert token in text, token


def test_master_contract_preserves_commercial_density_and_production_depth():
    text = (ROOT / 'references' / 'MASTER_CONSTRUCTION_CONTRACT.md').read_text(encoding='utf-8')
    required = [
        '七大一等能力', 'Pricing / Economics / Offer',
        'Asset Universe 不受平台槽位总数限制',
        '逐资产 Art Direction', 'Production Parameter Closure',
        'Model Prompt CN', 'Model Prompt EN', 'Visible Copy Block', 'Production / Assembly Notes',
        '构图', '相对位置', '尺度', '焦点路径', '负空间',
        '焦段', '工作距离', '机位', '景深', 'CCT / WB', '光比', '反射 / 偏振', 'Prelight',
        'CMF / 材质', '色彩管理', 'finishing',
        '商业级高密度', '不得压缩为摘要式 Prompt',
        '产品是否出现由逐资产策展决定',
        'REFERENCE_GUIDED_NATIVE_LOCK', 'EXACT_PIXEL_COMPOSITE',
        'Video / Creator / LIVE', 'Advertising Optimization', 'Review Analysis',
        'cbcc-commercial-v1', '自包含 HTML',
    ]
    for token in required:
        assert token in text, token


def test_prompt_contract_is_full_commercial_world_not_camera_parameter_dump():
    text = (ROOT / 'references' / 'MASTER_CONSTRUCTION_CONTRACT.md').read_text(encoding='utf-8')
    required = [
        'Prompt ≠ 摄影参数集合',
        '人物 / 主体', '人物角色', '年龄', '肤色', '发型 / 发质', '妆容', '服装 / 配饰',
        '姿态', '表情', '视线', '手部动作', '人物与产品交互',
        '动作', '行为', '时间瞬间', 'decisive moment',
        '元素', '场景', '环境', '前景', '中景', '背景', '道具', '表面 / 承托',
        '视觉钩子', '情绪节奏', '信息密度', '视觉载体',
        '商品角色', '商品出现节奏', '产品占画', '身份锚点',
        '构图语法', '空间关系', '尺度层级', '深度关系', '焦点路径', '负空间',
        '证据层级', '主证据', '次级证据', 'Proof Hierarchy',
        '文案', '字体', '字重', '字号层级', '行数', '对齐', '排版关系', 'safe zone',
        '目标市场语言', '本地化排版', 'RTL', 'CJK', '文化语境', '禁忌', '包容性表征',
        'CMF', '材质', '微表面', '透明 / 半透明', '反射', '高光', '颜色系统', 'HEX',
        '平台', '站点', 'Surface', '设备', '画幅', '尺寸', '色彩空间', '缩略图可读性',
        '动态', '镜头序列', 'beat', '主体运动', '相机运动', '转场', '字幕', 'VO', '音频',
        '商业决策', '购买障碍', '信念转变', '增量信息', '商业假设', '成功指标',
        '差异化签名', '与相邻资产的 rhythm delta',
        'QA', '最小责任层修复', 'Local Revision',
        '只含摄影参数', '必须判为不合格',
    ]
    for token in required:
        assert token in text, token


def test_v0652_builder_consumes_master_contract_and_preserves_previous_authorities():
    p = ROOT / 'scripts' / 'build_plugin_dist_v0652.py'
    assert p.exists()
    text = p.read_text(encoding='utf-8')
    for token in [
        'MASTER_CONSTRUCTION_CONTRACT.md',
        'build_plugin_dist_v0651',
        '0.6.52',
        'master_construction_contract_required',
        'commercial_density_non_regression_required',
        'prompt_and_art_direction_density_non_regression_required',
        'v0651_chinese_canonical_preserved',
        'mature_commercial_creative_capabilities_preserved',
    ]:
        assert token in text, token


def test_release_regression_matrix_covers_cross_dimension_loss():
    p = ROOT / 'references' / 'RELEASE_NON_REGRESSION_MATRIX.yaml'
    assert p.exists()
    text = p.read_text(encoding='utf-8')
    for token in [
        'language_without_strategy_loss',
        'compliance_without_creative_loss',
        'prompt_cleanliness_without_parameter_loss',
        'ui_without_business_object_loss',
        'media_portability_without_source_truth_loss',
        'full_density_without_fixed_template',
    ]:
        assert token in text, token
