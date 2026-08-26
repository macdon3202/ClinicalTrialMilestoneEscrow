from pathlib import Path


def test_evidence_fixture_is_present_and_anonymized():
    fixture = Path(__file__).parents[1] / "samples" / "milestone-report.json"
    assert fixture.exists()
    text = fixture.read_text(encoding="utf-8")
    assert "patient_name" not in text
    assert "adverse_events" in text
