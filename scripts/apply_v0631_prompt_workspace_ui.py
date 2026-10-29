from __future__ import annotations

from pathlib import Path


def replace(path:Path, old:str, new:str, *, count:int=1) -> None:
    text=path.read_text(encoding='utf-8')
    if new in text and old not in text:
        return
    if old not in text:
        raise SystemExit(f'{path}: UI anchor missing: {old[:100]!r}')
    path.write_text(text.replace(old,new,count),encoding='utf-8')


def main() -> None:
    path=Path('runtime/cbcc/delivery_html.py')
    text=path.read_text(encoding='utf-8')

    text=text.replace(
        "views.append({'key':'model-prompt-cn','title':'Model Prompt CN','html':'<div class=\"asset-file\"><div class=\"file-label\">直接给生成模型的中文提示词</div><pre><code>'+html.escape(prompt_cn)+'</code></pre></div>'})\n",
        "",
        1,
    )
    text=text.replace(
        "views.append({'key':'model-prompt-en','title':'Model Prompt EN','html':'<div class=\"asset-file\"><div class=\"file-label\">直接给生成模型的英文提示词</div><pre><code>'+html.escape(prompt_en)+'</code></pre></div>'})\n",
        "",
        1,
    )
    text=text.replace("views.append({'key':'production-notes','title':'生产 / 装配说明'", "views.append({'key':'production','title':'生产 / 装配说明'", 1)

    old="""body=f'''<div class=\"prompt-workbench\"><section class=\"prompt-primary\"><div class=\"prompt-head\"><div><span>中文生产说明</span><h3>中文规范生产提示词</h3></div><button class=\"copy-btn mini\" data-copy=\"{cid}\">复制中文</button></div><pre id=\"{cid}\"><code>{html.escape(cn)}</code></pre></section><section class=\"prompt-secondary\"><div class=\"prompt-head\"><div><span>发送生成模型（按模型 / 生产策略）</span><h3>英文 / 目标模型提示词</h3></div><button class=\"copy-btn mini\" data-copy=\"{eid}\">复制生成提示词</button></div><pre id=\"{eid}\"><code>{html.escape(en)}</code></pre></section></div><div class=\"language-note\">规则：人类交付默认中文；英文提示词是生产执行载体，不替代中文说明。目标市场可见文案若非中文，也必须在资产文案区提供中文释义。</div>'''"""
    new="""body=f'''<div class=\"prompt-workbench\"><section class=\"prompt-primary\"><div class=\"prompt-head\"><div><span>直接给生成模型</span><h3>Model Prompt CN｜中文模型提示词</h3></div><button class=\"copy-btn mini\" data-copy=\"{cid}\">复制中文 Prompt</button></div><pre id=\"{cid}\"><code>{html.escape(cn)}</code></pre></section><section class=\"prompt-secondary\"><div class=\"prompt-head\"><div><span>Direct model input</span><h3>Model Prompt EN｜英文模型提示词</h3></div><button class=\"copy-btn mini\" data-copy=\"{eid}\">复制英文 Prompt</button></div><pre id=\"{eid}\"><code>{html.escape(en)}</code></pre></section></div><div class=\"language-note\">这里只展示模型输入。目标市场可见文案与中文释义在“可见文案”对象中管理；锁图、文字装配、可编辑层、Provider 与后期规则在“生产 / 装配说明”中管理，不混入 Model Prompt。</div>'''"""
    if old not in text:
        raise SystemExit('global prompt workspace anchor missing')
    text=text.replace(old,new,1)

    old_cn="""parts.append(f'''<section class=\"prompt-primary\"><div class=\"prompt-head\"><div><span>人类生产说明</span><h3>中文规范生产提示词</h3></div><button class=\"copy-btn mini\" data-copy=\"{cid}\">复制中文</button></div><pre id=\"{cid}\"><code>{html.escape(a['prompt_cn'])}</code></pre></section>''')"""
    new_cn="""parts.append(f'''<section class=\"prompt-primary\"><div class=\"prompt-head\"><div><span>直接给生成模型</span><h3>Model Prompt CN｜中文模型提示词</h3></div><button class=\"copy-btn mini\" data-copy=\"{cid}\">复制中文 Prompt</button></div><pre id=\"{cid}\"><code>{html.escape(a['prompt_cn'])}</code></pre></section>''')"""
    if old_cn not in text: raise SystemExit('asset CN prompt label anchor missing')
    text=text.replace(old_cn,new_cn,1)

    old_en="""parts.append(f'''<section class=\"prompt-secondary\"><div class=\"prompt-head\"><div><span>发送生成模型</span><h3>英文 / 目标模型提示词</h3></div><button class=\"copy-btn mini\" data-copy=\"{eid}\">复制生成提示词</button></div><pre id=\"{eid}\"><code>{html.escape(a['prompt_en'])}</code></pre></section>''')"""
    new_en="""parts.append(f'''<section class=\"prompt-secondary\"><div class=\"prompt-head\"><div><span>Direct model input</span><h3>Model Prompt EN｜英文模型提示词</h3></div><button class=\"copy-btn mini\" data-copy=\"{eid}\">复制英文 Prompt</button></div><pre id=\"{eid}\"><code>{html.escape(a['prompt_en'])}</code></pre></section>''')"""
    if old_en not in text: raise SystemExit('asset EN prompt label anchor missing')
    text=text.replace(old_en,new_en,1)

    old_note="""body='<div class=\"asset-prompt-console\"><div class=\"prompt-workbench\">'+''.join(parts)+'</div><div class=\"language-note\">只核对当前资产实际相关的决策、画面、摄影 / CMF、文案和保真约束。缺失或不相关的维度不应为了“字段完整”被补造；Prompt 是执行合同，不是独立创意来源。</div></div>'"""
    new_note="""body='<div class=\"asset-prompt-console\"><div class=\"prompt-workbench\">'+''.join(parts)+'</div><div class=\"language-note\">Model Prompt 只承载当前资产真正需要进入生成模型的视觉、空间、摄影 / CMF、动态与文字行为。产品锁定、图层、文字装配、Provider、QA 与修订规则请到“生产说明”查看；这些工程合同不进入模型提示词。</div></div>'"""
    if old_note not in text: raise SystemExit('asset prompt note anchor missing')
    text=text.replace(old_note,new_note,1)

    text=text.replace("add('prompt','Prompt 执行','EXECUTION','执行当前已编译的生产 Prompt；不补造无关参数。',body)", "add('prompt','Model Prompt','MODEL INPUT','查看当前资产真正发送给图像 / 视频生成模型的 CN / EN 提示词。',body)", 1)

    # Return model-prompt readiness from the compiled contract so the human workspace does not equate file existence with readiness.
    old_return="""return {'id':aid,'title':display_title,'original_title':original_title,'summary':summary,'prompt_cn':prompt_cn,'prompt_en':prompt_en,'views':views,'source_files':src,'surface':surface,'intent':intent,'asset_type':asset_type,'agent_view_order':design.get('workspace_view_order') or design.get('agent_view_order') or []}"""
    new_return="""return {'id':aid,'title':display_title,'original_title':original_title,'summary':summary,'prompt_cn':prompt_cn,'prompt_en':prompt_en,'model_prompt_status':prompt_contract.get('model_prompt_status'),'views':views,'source_files':src,'surface':surface,'intent':intent,'asset_type':asset_type,'agent_view_order':design.get('workspace_view_order') or design.get('agent_view_order') or []}"""
    if old_return not in text: raise SystemExit('formal asset return anchor missing')
    text=text.replace(old_return,new_return,1)

    old_ready="""if a.get('prompt_cn'): readiness.append('中文 Prompt 已就绪')
    if a.get('prompt_en'): readiness.append('生成模型 Prompt 已就绪')"""
    new_ready="""if a.get('model_prompt_status'):
        readiness.append('Model Prompt：'+str(a.get('model_prompt_status')))
    else:
        if a.get('prompt_cn'): readiness.append('中文 Model Prompt 已生成')
        if a.get('prompt_en'): readiness.append('英文 Model Prompt 已生成')"""
    if old_ready not in text: raise SystemExit('asset readiness anchor missing')
    text=text.replace(old_ready,new_ready,1)

    path.write_text(text,encoding='utf-8')
    print('Applied v0.6.31 model-prompt workspace UI separation.')


if __name__=='__main__':
    main()
