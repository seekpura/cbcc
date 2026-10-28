from pathlib import Path

path=Path('tests/test_v0611_provider_source_binding.py')
text=path.read_text(encoding='utf-8')
old="""        'production_contract_ack':True,'source_binding_hash':job['source_binding_hash'],\n        'quality_observations':_quality(job),\n    }\n"""
new="""        'production_contract_ack':True,'source_binding_hash':job['source_binding_hash'],\n        'quality_observations':_quality(job),\n        'production_receipt':{\n            'job_id':job['job_id'],'asset_id':job['asset_id'],'provider':job['provider'],'package_hash':job['package_hash'],\n            'portable_manifest_hash':job['portable_package']['portable_manifest_hash'],'source_binding_hash':job['source_binding_hash'],\n            'output_artifacts':[{'uri':'fixture://provider-output/'+job['asset_id'],'sha256':'b'*64,'role':'FINAL'}],\n            'layer_manifest':[{'layer_id':'product-'+str(i),'role':'PRODUCT_MASTER','source_asset_id':x['asset_id'],'source_sha256':x['sha256'],'operation':'COMPOSITE_LOCKED','frozen':True} for i,x in enumerate(job.get('source_product_bindings') or [])],\n            'capture_metadata':{},\n        },\n        '_provider_job_ingest':True,\n    }\n"""
if old not in text:
    raise SystemExit('v0.6.11 result helper anchor not found')
path.write_text(text.replace(old,new,1),encoding='utf-8')
