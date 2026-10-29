from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def patch(path:str,old:str,new:str, count:int=-1):
    p=ROOT/path
    text=p.read_text(encoding='utf-8')
    if old not in text:
        if new in text:
            return
        raise SystemExit(f'missing anchor {path}: {old[:140]!r}')
    text=text.replace(old,new,count) if count!=-1 else text.replace(old,new)
    p.write_text(text,encoding='utf-8')

(ROOT/'VERSION').write_text('0.6.34-native-reference-authority-cleanup\n',encoding='utf-8')
patch('SKILL.md','version: 0.6.33-reference-guided-native-asset-universe','version: 0.6.34-native-reference-authority-cleanup')

patch('SKILL.md',
'''- **LOCKED_SOURCE_COMPOSITE 不是空背景生成。** 不重画商品只锁定商品身份层；环境底片仍必须围绕最终商品 envelope/occupancy、相对位置、纵深、透视、接触面、接触阴影、反射接收、环境光向/光比、CCT/WB、grade-match、前景遮挡与 copy/evidence safe zone 来生成。Prompt 必须描述最终合成空间/光线系统，同时明确不生成锁定商品本体。''',
'''- **真实商品锁定默认是 Reference-Guided Native Generation，不是后期像素合成。** 当 Product Presence 要求商品可见时，真实商品图必须作为强模型 Reference Input，商品本体在完整最终画面中原生生成；所有已作者化的 envelope/occupancy、相对位置、纵深、透视、接触面、接触阴影、反射、环境光向/光比、CCT/WB、grade、前景遮挡与 copy/evidence safe zone 都必须共同进入模型执行。只有用户明确要求原始源图像素层不可改变时才启用 `EXACT_PIXEL_COMPOSITE`。''')

p=ROOT/'scripts/build_plugin_dist.py'
text=p.read_text(encoding='utf-8')
block='''## Dynamic Asset Universe + Native Product Reference\n资产总量由购买决策、Surface、创意假设、测试与运营需求决定，不受平台 Gallery 槽位总数限制。Hero、卖点、广告、A+/PDP/详情、Store/Banner、Social/Creator、Video 等均可存在多方案；同一消费者问题和同一 Surface 也允许 H01/H02/H03 等显式 Variant，不得因为 question/surface/family 相同而合并。人类工作区区分上线候选、测试池、轮换池、广告、PDP/A+详情、归档与其他资产。\n\n当 Product Presence 要求真实商品可见时，真实商品图默认作为强模型 Reference Input，使用 `REFERENCE_GUIDED_NATIVE_LOCK` 原生生成完整最终画面中的商品，并保持真实商品身份；`EXACT_PIXEL_COMPOSITE` 仅在用户明确要求源图像素层不可改变时启用。\n\n'''
if text.count(block) > 1:
    first=text.find(block)
    second=text.find(block,first+len(block))
    text=text[:second]+text[second+len(block):]

old='''- 商品规格、成分、功能、认证、Claim 与其他已验证事实必须 source-bound；产品图、包装图和源文件默认是设计参考，可按已选创意方向重绘/重渲染/风格化，除非当前子任务显式锁定源图。Claim、Compliance、平台当前证据、Review 与 Completion 按 `resources/SKILL.md` 和 Runtime 合同执行。'''
new='''- 商品规格、成分、功能、认证、Claim 与其他已验证事实必须 source-bound；当 Product Presence 要求真实商品可见时，真实商品图/包装图作为强模型 Reference Input，按已选 Art Direction 原生生成完整成图并保持商品身份；当资产不要求商品出现时，源图可仅作为 Truth/Identity/Design Reference。只有用户明确要求原始像素层不变时才使用 `EXACT_PIXEL_COMPOSITE`。Claim、Compliance、平台当前证据、Review 与 Completion 按 `resources/SKILL.md` 和 Runtime 合同执行。'''
if old in text:
    text=text.replace(old,new)
elif new not in text:
    raise SystemExit('missing commercial continuity authority anchor')
p.write_text(text,encoding='utf-8')

print('v0.6.34 native-reference authority cleanup applied')
