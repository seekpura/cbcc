from pathlib import Path

root=Path('tests')
patterns=[
    'test_v0676_phase3_opportunity_family_evaluation.py',
    'test_v0676_phase3_opportunity_family_runtime_binding.py',
    'test_v0662_asset_universe_and_package_regressions.py',
    'test_v0655_asset_universe_open_world.py',
    'test_v0646_asset_family_no_quota.py',
    'test_v0646_activation_state_taxonomy.py',
    'test_v0633_asset_universe_workspace.py',
    'test_v0676_canonical_commerce_graph.py',
    'test_v0670_human_projection_integrity.py',
    'test_v0635_native_reference_provider_integrity.py',
]
missing=[x for x in patterns if not (root/x).exists()]
print('missing=',missing)
print('present=',[x for x in patterns if (root/x).exists()])
