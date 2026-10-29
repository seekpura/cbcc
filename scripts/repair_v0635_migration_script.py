from pathlib import Path

p=Path(__file__).resolve().parent/'apply_v0635_native_reference_provider_integrity.py'
text=p.read_text(encoding='utf-8')
old='''patch('runtime/cbcc/provider_bridge.py',
"                'AI_HUMAN_REAL_PRODUCT', 'AI_GENERATIVE', 'GRAPHIC_DESIGN', 'THREE_D', 'VIDEO',\\n            ),\\n            capabilities=('IDEMPOTENT_SUBMIT', 'RESUMABLE_POLL', 'OUTPUT_RESOLVE', 'ASSET_HANDLE_LIFECYCLE'),\\n",
"                'AI_HUMAN_REAL_PRODUCT', 'AI_REFERENCE_PRODUCT', 'AI_REFERENCE_HUMAN_PRODUCT', 'AI_GENERATIVE', 'GRAPHIC_DESIGN', 'THREE_D', 'VIDEO',\\n            ),\\n            capabilities=('IDEMPOTENT_SUBMIT', 'RESUMABLE_POLL', 'OUTPUT_RESOLVE', 'ASSET_HANDLE_LIFECYCLE', 'REFERENCE_IMAGE_INPUT'),\\n")
'''
new='''patch('runtime/cbcc/provider_bridge.py',
"            capabilities=('IDEMPOTENT_SUBMIT', 'RESUMABLE_POLL', 'OUTPUT_RESOLVE', 'ASSET_HANDLE_LIFECYCLE'),\\n",
"            capabilities=('IDEMPOTENT_SUBMIT', 'RESUMABLE_POLL', 'OUTPUT_RESOLVE', 'ASSET_HANDLE_LIFECYCLE', 'REFERENCE_IMAGE_INPUT'),\\n")
'''
if old in text:
    text=text.replace(old,new)
elif new not in text:
    raise SystemExit('v0.6.35 migration-order repair anchor missing')
p.write_text(text,encoding='utf-8')
print('v0.6.35 migration ordering repaired')
