from pathlib import Path

p=Path('scripts/final_consistency_reference_guided.py')
s=p.read_text(encoding='utf-8')
old_marker="""marker=\"\"\"        'approved product-specific evidence':'已批准的商品特定证据',\n\"\"\"\ninsert=\"\"\"        'approved product-specific evidence':'已批准的商品特定证据',\n"""
new_marker="""marker=\"\"\"      'Use the supplied real-product master as the product subject':'以用户提供的真实商品母版作为商品主体',\n\"\"\"\ninsert=\"\"\"      'Use the supplied real-product master as the product subject':'以用户提供的真实商品母版作为商品主体',\n"""
if old_marker not in s:
    raise SystemExit('brittle prompt translation marker block not found')
s=s.replace(old_marker,new_marker,1)
exec(compile(s,str(p),'exec'),{'__name__':'__main__'})
