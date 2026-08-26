# Live evidence procedure

The rules require the submitted deployment (not a mock) to be exercised with two
funded wallets. Run this procedure only after manual deployment on Studionet.

For each call record: network/chain, contract address, commit SHA, SDK/runner
versions, caller, exact arguments, attached value in wei, transaction hash,
finality, contract return/error, readback state, contract balance, recipient
balance, and transfer identifier.

Required cases are listed in `verification/lifecycle-matrix.md`: authorized happy
path, unauthorized caller, zero/wrong value, out-of-order call, duplicate action,
double settlement, evidence substitution, unavailable evidence recovery, economic
conservation, and recipient correctness.

Do not place private keys or tokens in this directory.
