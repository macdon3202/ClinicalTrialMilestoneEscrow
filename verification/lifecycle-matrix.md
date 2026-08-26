# ClinicalTrialMilestoneEscrow local verification matrix

| Case | Expected result |
|---|---|
| Create Phase I/II/III trial | Sequential trial ID; `ACTIVE` |
| Add milestone with recipient and exact amount | `PENDING` |
| Payable funding with zero value | `ZERO_VALUE`; no custody transition |
| Payable funding with wrong value | `WRONG_ESCROW_VALUE`; no custody transition |
| Payable funding with exact value | `FUNDED`; attached GEN recorded |
| Submit duplicate digest | `DIGEST_REUSED`; no new report |
| Validate compliant low/medium-risk report | `APPROVED` |
| Validate high-risk/non-compliant report | `REJECTED` |
| Release approved milestone twice | first `RELEASED`, second rejected |
| Refund rejected milestone twice | first `REFUNDED`, second `NOT_REFUNDABLE` |

The live evidence phase must additionally record attached value, contract balance,
recipient balance, transfer identifier, and post-state for every value-bearing call.

Reference recipient for the local fixture:
`0xf7498AE4cade4226c11fc38E1AddF1A7Ec453E93`
