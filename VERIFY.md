# Verifying BABA Capital's on-chain proof anchors

Every week the BABA engine commits a `keccak256` hash of its public
track-record snapshot to the **BabaProofRegistry** contract on Base, and
publishes the exact bytes it hashed in `proofs/`. Anyone can reproduce the hash
and confirm the record was not edited after the fact.

- **Contract:** `0x9932AEd609692d3C512B69bbE1090AE3BF9356d9` (Base, chain 8453) — source-verified on BaseScan
- **Event:** `Anchored(index, hash, anchorer, timestamp, label)`, where `label = nav-YYYY-Www`
- **Anchorer (operational):** `0x69fcb9ed839269403A5112d56e2AA0d692071De2` (authorized by owner `alaye.base.eth`)

## Verify a week
1. Fetch the exact bytes: `proofs/proof-YYYY-Www.json`.
2. Compute `keccak256` of the raw bytes.
3. On BaseScan, open the contract → **Events** → find the `Anchored` entry whose `label == nav-YYYY-Www`.
4. Its `hash` must equal your computed value. Match = the snapshot is byte-for-byte what was committed on-chain at that block time.

```python
from web3 import Web3
b = open("proofs/proof-2026-W28.json", "rb").read()
print("0x" + Web3.keccak(b).hex())
```

`proofs/index.json` lists every published week with its expected `keccak256`.
