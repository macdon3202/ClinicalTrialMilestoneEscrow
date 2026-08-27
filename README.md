# ClinicalTrialMilestoneEscrow

GenLayer Intelligent Contract for milestone-based clinical-trial compliance escrow.
Only the registered lab address or an explicit sponsor-appointed delegate can
submit an immutable, anonymized IPFS report for each milestone. Validators
comparatively assess protocol compliance, sample-size evidence, adverse events, and
safety risk before a milestone can be released.

## Lifecycle

`create_trial` → `add_milestone` → `submit_report` → `validate_report` →
`release_milestone`

Only approved reports with LOW or MEDIUM risk can release funds. Every report
digest is single-use; invalid transitions return explicit error codes. Milestone
amounts reserve the trial budget when created, are consumed exactly once on
release, and are returned to the recorded trial sponsor when a report is rejected.

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
0xe619897700a801229ec3e1bb6f43c221dA91c28b
```

The verified Studionet run used `0.01 GEN` escrow:

```text
deployment        0x6126f09e8f8b31f57fc38029d8a4e2f1d0745f0cc0c2ef72fcdcbc7f4a78937e
create_trial      0x74e0d6b7cea84915fad6b3c5524598833d337b567d4ae84bf4b8fbb05b2c9144
add_milestone     0xe6e5b3f9d8ac609537c7a527453634b3ebd00e8f7389c1e7f5cad4718d6feaa3
fund_milestone    0xac29e426f6abc5f277940f31d2e2d5d221cb72e19d07e29340d24a98289b0268
submit_report     0xdef6477cd40e522ea48a62098bf3eafbe6638e997926b9c00ee574e637dd88bb
validate_report   0x10f9c909d00ee89418532f1b1b230188affa024eb20214898cbd236a3b2411ac
release_milestone 0xb26e0faeec340e6bab6d769f52dc1d0bdc351fb801756b8753f9dd826a402306
recipient_transfer 0xdce93b15eb3e8d8ae933cf7dd3582c1c6f8a07726f89b8234a8ba3b312d67fdd
```

All listed transactions reached `FINALIZED` with majority agreement. The final
on-chain state was `RELEASED`; Explorer showed the contract balance at `0 GEN`
and a `0.01 GEN` transfer to the recorded milestone recipient. This evidence
proves the lifecycle, terminal state, and recipient transfer.

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
