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

## Required live evidence

Before claiming a production-ready escrow, execute the adversarial matrix against
the deployed contract with two funded wallets and record real balance/transfer
proof. The evidence template is in `docs/live-evidence/`; its initial result is
`NOT_RUN` until a manual Studionet deployment exists.

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
