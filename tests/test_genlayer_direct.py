import json
import pytest
import gltest.direct.loader as direct_loader


CONTRACT_PATH = "contracts/ClinicalTrialMilestoneEscrow.py"
REPORT_URI = "ipfs://QmPQZ1UDSFdxH9wLdERbMN8xQHwbQWYmhQWXA9ffYZc23w"
DIGEST = "sha256:3a924048a1e5ffc7157c99bfc5cda2f768f89aeaab4f644e4f7469e6521ca5aa"


@pytest.fixture(autouse=True)
def _windows_fd0_workaround(monkeypatch):
    original = direct_loader._inject_message_to_fd0
    def inject(vm):
        try:
            original(vm)
        except PermissionError:
            pass
    monkeypatch.setattr(direct_loader, "_inject_message_to_fd0", inject)


def _addr(value):
    if isinstance(value, bytes):
        return "0x" + value.hex()
    return getattr(value, "as_hex", str(value))


def test_role_lifecycle_and_wrong_value(direct_vm, direct_deploy, direct_owner, direct_alice):
    direct_vm.sender = direct_owner
    contract = direct_deploy(CONTRACT_PATH)
    direct_vm.sender = direct_owner
    assert contract.create_trial("oncology-phase-ii-demo", "PHASE_II", 10**16, str(direct_alice)) == 0
    assert contract.add_milestone(0, "interim-safety-review", 10**16, _addr(direct_alice)) == 0
    direct_vm.sender = direct_alice
    direct_vm.value = 1
    assert contract.fund_milestone(0) == "SPONSOR_ONLY"
    direct_vm.sender = direct_owner
    assert contract.fund_milestone(0) == "WRONG_ESCROW_VALUE"
    direct_vm.value = 10**16
    assert contract.fund_milestone(0) == "FUNDED"
    direct_vm.value = 0
    direct_vm.sender = direct_alice
    assert contract.submit_report(0, REPORT_URI, DIGEST) == 0
    direct_vm.mock_web("https://ipfs.io/ipfs/" + REPORT_URI[7:], {"status": 200, "body": "synthetic anonymized report"})
    direct_vm.mock_llm(".*", json.dumps({"compliant": True, "risk": "LOW", "reason": "All protocol gates pass."}))
    assert contract.validate_report(0) == "APPROVED"
    assert contract.release_milestone(0) == "RELEASED"
    assert contract.read_milestone(0) == "RELEASED"
