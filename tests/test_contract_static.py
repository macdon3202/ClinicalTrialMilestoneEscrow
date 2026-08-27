from pathlib import Path
import ast


CONTRACT = Path(__file__).parents[1] / "contracts" / "ClinicalTrialMilestoneEscrow.py"


def test_contract_parses_and_has_required_header():
    text = CONTRACT.read_text(encoding="utf-8")
    assert text.startswith('# v0.2.16\n# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }\nfrom genlayer import *')
    ast.parse(text)


def test_contract_uses_comparative_consensus_and_escrow_guards():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "prompt_comparative" in text
    assert "gl.nondet.web.get" in text
    assert "DIGEST_REUSED" in text
    assert "INSUFFICIENT_ESCROW" in text
    assert "release_milestone" in text
    assert "write.payable" in text
    assert "gl.message.value" in text
    assert "_Recipient(Address" in text
    assert "emit_transfer" in text
    assert "refund_milestone" in text
    assert "NOTHING_TO_REFUND" in text
    assert "LAB_OR_DELEGATE_ONLY" in text
    assert "set_trial_delegate" in text
    assert "trial_sponsor" in text
