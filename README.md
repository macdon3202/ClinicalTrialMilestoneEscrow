# ClinicalTrialMilestoneEscrow

GenLayer Intelligent Contract for milestone-based clinical-trial compliance escrow.
Labs submit an immutable, anonymized IPFS report for each milestone. Validators
comparatively assess protocol compliance, sample-size evidence, adverse events, and
safety risk before a milestone can be released.

## Lifecycle

`create_trial` → `add_milestone` → `submit_report` → `validate_report` →
`release_milestone`

Only approved reports with LOW or MEDIUM risk can release funds. Every report
digest is single-use; invalid transitions return explicit error codes.

## Local build

```bash
python -c "import ast; ast.parse(open('contracts/ClinicalTrialMilestoneEscrow.py').read())"
pytest -q
```

The canonical contract file is `contracts/ClinicalTrialMilestoneEscrow.py`.
The `samples/milestone-report.json` fixture is anonymized and is used by the
evidence-oriented tests in `tests/`.

Deployment is intentionally manual. Never commit private keys or API tokens.

## Verified Studionet deployment

The contract was manually deployed and exercised on GenLayer Studionet
(chain ID `61999`) at:

```text
0x65629134FE9cc5f6BE2C8798467f5D1012e39634
```

The verified Studionet run used `0.01 GEN` escrow:

```text
create_trial      0x7eb161f71bdbc3c574ed8dd9f4f9cfd3dbe6bfbdcec0406765e479a84a7576bc
add_milestone     0x383b58de9a08dbdbb6af67de03662c0338ee5412689129b71c522fc7b83da825
fund_milestone    0xa52036a2a7fcbc603b43e183c7cc8e48f5e6fc5e5403d6b0657c17d487ab712f
submit_report     0x04629e1f367ca811554653523d7b2cbbc76ae0ae1210b79c59e3f58202893cef
validate_report   0x5fb367617a14cd549d8313f798f664d14b6c0d9af968cdee1cf338a4a79ed1e6
release_milestone 0x1b3f323fc8f910c7f92b905d658510c61e72fe1681ab680f2967d2c2f97ce2bb
```

All listed transactions reached `ACCEPTED`/`FINALIZED` with majority agreement.
The final on-chain readback was `RELEASED`. This evidence proves the lifecycle
and terminal state; it does not claim an independently recorded recipient
balance delta unless that balance evidence is added to `docs/live-evidence/`.

## Studio deployment checklist

1. Upload `contracts/ClinicalTrialMilestoneEscrow.py` with **Add From File**.
2. Confirm the editor shows `ClinicalTrialMilestoneEscrow` and all methods.
3. Deploy a new instance; record the deployment hash and address.
4. Run `create_trial` and `add_milestone`, using the recipient address supplied by
   the operator.
5. Call `fund_milestone` with the exact amount in wei and capture custody balance.
6. Submit an anonymized `ipfs://` report, then call `validate_report` and wait for
   consensus/finality.
7. Call `release_milestone` or `refund_milestone`; verify recipient/sponsor balance,
   contract balance, terminal state, and conservation.
