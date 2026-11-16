from pathlib import Path

STUBS_ROOT = Path(__file__).resolve().parent.parent


def test_license_matches_the_sdk_license():
    assert (STUBS_ROOT / "LICENSE").read_bytes() == (STUBS_ROOT.parent / "LICENSE").read_bytes()
