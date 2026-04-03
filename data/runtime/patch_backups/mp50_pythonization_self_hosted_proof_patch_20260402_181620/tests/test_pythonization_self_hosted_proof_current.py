from pathlib import Path


def test_mp50_self_hosted_proof_marker_exists_and_is_current():
    marker_path = Path('data/runtime/self_hosted_proof/mp50_existing_marker.txt')
    assert marker_path.exists()
    text = marker_path.read_text(encoding='utf-8')
    assert 'mp50 self-hosted proof written via patchops' in text.lower()
    assert 'backup and write helpers' in text.lower()
