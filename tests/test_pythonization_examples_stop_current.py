from pathlib import Path


def test_examples_doc_mentions_pythonization_alignment_stop():
    text = Path('docs/examples.md').read_text(encoding='utf-8').lower()
    assert 'pythonization maintenance alignment' in text
    assert 'opt-in' in text or 'opt in' in text
    assert 'maintenance-facing' in text
    assert 'low-risk' in text or 'low risk' in text
    assert 'not a mandatory default behavior' in text
