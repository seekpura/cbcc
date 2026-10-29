from __future__ import annotations

from pathlib import Path


def rep(text:str, old:str, new:str, label:str)->str:
    if new in text and old not in text:
        return text
    if old not in text:
        raise SystemExit(f'missing UI anchor: {label}')
    return text.replace(old,new,1)


def main()->None:
    path=Path('runtime/cbcc/delivery_html.py')
    text=path.read_text(encoding='utf-8')

    # Remove duplicate prompt subviews atomically. The asset page owns the single Model Prompt lens.
    text=rep(text,
        "        if prompt_cn:\n            views.append({'key':'model-prompt-cn','title':'Model Prompt CN','html':'<div class=\"asset-file\"><div class=\"file-label\">直接给生成模型的中文提示词</div><pre><code>'+html.escape(prompt_cn)+'</code></pre></div>'})\n",
        '', 'formal model prompt CN view')
    text=rep(text,
        "        if prompt_en:\n            views.append({'key':'model-prompt-en','title':'Model Prompt EN','html':'<div class=\"asset-file\"><div class=\"file-label\">直接给生成模型的英文提示词</div><pre><code>'+html.escape(prompt_en)+'</code></pre></div>'})\n",
        '', 'formal model prompt EN view')
    text=rep(text,
        "views.append({'key':'production-notes','title':'生产 / 装配说明'",
        "views.append({'key':'production','title':'生产 / 装配说明'",
        'production view key')

    # Global Prompt Lab = model input only.
    text=text.replace('<span>中文生产说明</span><h3>中文规范生产提示词</h3>','<span>直接给生成模型</span><h3>Model Prompt CN｜中文模型提示词</h3>')
    text=text.replace('>复制中文</button>','>复制中文 Prompt</button>')
    text=text.replace('<span>发送生成模型（按模型 / 生产策略）</span><h3>英文 / 目标模型提示词</h3>','<span>Direct model input</span><h3>Model Prompt EN｜英文模型提示词</h3>')
    text=text.replace('>复制生成提示词</button>','>复制英文 Prompt</button>')
    text=text.replace('规则：人类交付默认中文；英文提示词是生产执行载体，不替代中文说明。目标市场可见文案若非中文，也必须在资产文案区提供中文释义。','这里只展示模型输入。目标市场可见文案与中文释义在“可见文案”对象中管理；锁图、文字装配、可编辑层、Provider 与后期规则在“生产 / 装配说明”中管理，不混入 Model Prompt。')

    # Asset page Prompt lens = same contract, no engineering-contract language.
    text=text.replace('<span>人类生产说明</span><h3>中文规范生产提示词</h3>','<span>直接给生成模型</span><h3>Model Prompt CN｜中文模型提示词</h3>')
    text=text.replace('<span>发送生成模型</span><h3>英文 / 目标模型提示词</h3>','<span>Direct model input</span><h3>Model Prompt EN｜英文模型提示词</h3>')
    text=text.replace('只核对当前资产实际相关的决策、画面、摄影 / CMF、文案和保真约束。缺失或不相关的维度不应为了“字段完整”被补造；Prompt 是执行合同，不是独立创意来源。','Model Prompt 只承载当前资产真正需要进入生成模型的视觉、空间、摄影 / CMF、动态与文字行为。产品锁定、图层、文字装配、Provider、QA 与修订规则请到“生产 / 装配说明”查看；这些工程合同不进入模型提示词。')
    text=text.replace("add('prompt','Prompt 执行','EXECUTION','执行当前已编译的生产 Prompt；不补造无关参数。',body)","add('prompt','Model Prompt','MODEL INPUT','查看当前资产真正发送给图像 / 视频生成模型的 CN / EN 提示词。',body)")
    text=text.replace("'production':('生产说明','PRODUCTION','查看与本资产执行方式直接相关的生产备注。')","'production':('生产 / 装配说明','PRODUCTION','查看锁图、文字装配、图层、Provider 与本资产执行方式直接相关的生产备注。')")

    # Human workspace readiness reflects semantic readiness, not just file existence.
    old="return {'id':aid,'title':display_title,'original_title':original_title,'summary':summary,'prompt_cn':prompt_cn,'prompt_en':prompt_en,'views':views,'source_files':src,'surface':surface,'intent':intent,'asset_type':asset_type,'agent_view_order':design.get('workspace_view_order') or design.get('agent_view_order') or []}"
    new="return {'id':aid,'title':display_title,'original_title':original_title,'summary':summary,'prompt_cn':prompt_cn,'prompt_en':prompt_en,'model_prompt_status':prompt_contract.get('model_prompt_status'),'views':views,'source_files':src,'surface':surface,'intent':intent,'asset_type':asset_type,'agent_view_order':design.get('workspace_view_order') or design.get('agent_view_order') or []}"
    text=rep(text,old,new,'formal asset return')

    text=text.replace("if a.get('prompt_cn'): readiness.append('中文 Prompt 已就绪')\n    if a.get('prompt_en'): readiness.append('生成模型 Prompt 已就绪')",
                      "if a.get('model_prompt_status'):\n        readiness.append('Model Prompt：'+str(a.get('model_prompt_status')))\n    else:\n        if a.get('prompt_cn'): readiness.append('中文 Model Prompt 已生成')\n        if a.get('prompt_en'): readiness.append('英文 Model Prompt 已生成')")

    if '中文规范生产提示词</h3>' in text or 'Prompt 是执行合同' in text:
        raise SystemExit('legacy prompt-contract UI wording remains')
    path.write_text(text,encoding='utf-8')
    print('Applied atomic v0.6.31 model-prompt workspace UI separation.')


if __name__=='__main__':
    main()
