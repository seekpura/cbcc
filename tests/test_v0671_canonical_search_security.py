from runtime.cbcc.canonical_full_parity_v0671 import _script


def test_canonical_search_never_injects_untrusted_values_via_innerhtml():
    script = _script({'listing': {'title': '<img src=x onerror=alert(1)>'}})
    assert 'out.innerHTML=rows.map' not in script
    assert 'textContent' in script
    assert 'createElement' in script
