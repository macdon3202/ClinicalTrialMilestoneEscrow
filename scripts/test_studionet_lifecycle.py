"""Studionet two-wallet lifecycle runner using genlayer_py."""
import json, os, sys, time
from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet

ADDRESS = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("CLINICAL_ESCROW_ADDRESS", "")
TRIAL_KEY = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("CLINICAL_TRIAL_KEY", "oncology-phase-ii-demo-2")
MODE = sys.argv[3] if len(sys.argv) > 3 else os.environ.get("CLINICAL_TEST_MODE", "fresh")
TRIAL_ID = int(os.environ.get("CLINICAL_TRIAL_ID", "0"))
MILESTONE_ID = int(os.environ.get("CLINICAL_MILESTONE_ID", "0"))
REPORT_ID = int(os.environ.get("CLINICAL_REPORT_ID", "0"))
RPC = "https://studio.genlayer.com/api"
WEI = 10**16
URI = "ipfs://QmPQZ1UDSFdxH9wLdERbMN8xQHwbQWYmhQWXA9ffYZc23w"
DIGEST = "sha256:3a924048a1e5ffc7157c99bfc5cda2f768f89aeaab4f644e4f7469e6521ca5aa"

def parse(x):
    if not isinstance(x, str):
        return x
    try:
        return json.loads(x)
    except (TypeError, ValueError):
        return x

def main():
    if not ADDRESS: raise RuntimeError("Set CLINICAL_ESCROW_ADDRESS or pass address")
    k1, k2 = os.environ.get("DEPLOYER_PRIVATE_KEY", ""), os.environ.get("OPERATOR_PRIVATE_KEY", "")
    if not k1 or not k2: raise RuntimeError("Set DEPLOYER_PRIVATE_KEY and OPERATOR_PRIVATE_KEY")
    a1, a2 = create_account(k1), create_account(k2)
    client = create_client(chain=studionet, account=a1, endpoint=RPC)
    def read(name, args=None): return parse(client.read_contract(address=ADDRESS, function_name=name, args=args or [], account=a1))
    def send(account, method, args, value=0):
        tx = client.write_contract(address=ADDRESS, function_name=method, account=account, args=args, value=value)
        h = str(tx); print(json.dumps({"event":"SUBMITTED","method":method,"tx":h}, sort_keys=True), flush=True); return h
    def wait(tx, label):
        last = None
        for _ in range(120):
            info = client.get_transaction(tx)
            status = info.get("status_name") or info.get("status")
            result = info.get("tx_execution_result_name") or info.get("result_name") or info.get("execution_result")
            snapshot = (status, result)
            if snapshot != last:
                print(json.dumps({"event": label, "tx": tx, "status": status, "result": result}, sort_keys=True), flush=True)
                last = snapshot
            if status in ("REJECTED", "FAILED", "CANCELLED"):
                raise RuntimeError(f"{label} failed: status={status}, result={result}")
            if status in ("ACCEPTED", "FINALIZED"):
                # ACCEPTED is sufficient for the next write; FINALIZED is retained
                # when returned by the node. Do not require a version-specific
                # execution-result field, which is absent on some Studio builds.
                return info
            time.sleep(3)
        raise TimeoutError(f"{label}: transaction did not reach ACCEPTED/FINALIZED")
    print(json.dumps({"event":"START","contract":ADDRESS,"deployer":a1.address,"operator":a2.address}, sort_keys=True))
    if MODE == "fresh":
        wait(send(a1, "create_trial", [TRIAL_KEY, "PHASE_II", WEI, a2.address]), "TRIAL")
        trial_id = TRIAL_ID
        wait(send(a1, "add_milestone", [trial_id, "interim-safety-review", WEI, a2.address]), "MILESTONE")
        milestone_id = MILESTONE_ID
    elif MODE == "existing":
        trial_id, milestone_id = TRIAL_ID, MILESTONE_ID
        print(json.dumps({"event": "USING_EXISTING", "trial_id": trial_id, "milestone_id": milestone_id}, sort_keys=True), flush=True)
    else:
        raise ValueError("mode must be 'fresh' or 'existing'")
    wait(send(a1, "fund_milestone", [milestone_id], WEI), "FUND")
    wait(send(a2, "submit_report", [milestone_id, URI, DIGEST]), "REPORT")
    wait(send(a2, "validate_report", [REPORT_ID]), "VALIDATE")
    print(json.dumps({"event":"READBACK","trial_id": trial_id, "milestone_id": milestone_id, "status":read("read_milestone", [milestone_id])}, sort_keys=True))

if __name__ == "__main__": main()
