#!/usr/bin/env python3
"""
baba_proof_anchor.py — commit a weekly proof hash of BABA Capital's reconciled
track record to the on-chain BabaProofRegistry (Base).

This is the automation half of `onchain-proof`: each run computes a keccak256
commitment over a public feed snapshot (e.g. nav.json / a results feed) and
writes it on-chain with a label + timestamp. Anyone can later recompute the hash
from the public feed and check it matches the block-time commitment — proof the
record was not edited after the fact.

DARK BY DEFAULT. It no-ops unless ALL of these are set:
    BABA_PROOF_ANCHOR_ARM=1
    BABA_PROOF_REGISTRY_ADDR=0x...        # deployed contract address (Step 5)
    BABA_PROOF_ANCHORER_KEY=0x...         # private key of a DEDICATED low-value
                                          # operational anchorer (authorized via
                                          # setAnchorer). NOT alaye.base.eth's key.
    BASE_RPC_URL=https://mainnet.base.org # or your keyed RPC

Idempotent: if the latest on-chain hash already equals the new hash, it skips
(no duplicate anchor, no wasted gas).

Usage:
    python3 baba_proof_anchor.py --feed /path/to/nav.json --label nav-2026-07-11
    python3 baba_proof_anchor.py --feed - --label oracle-week-28   # read stdin
"""
from __future__ import annotations
import argparse, datetime as _dt, os, sys

ABI = [
    {"inputs": [{"internalType": "bytes32", "name": "hash", "type": "bytes32"},
                {"internalType": "string", "name": "label", "type": "string"}],
     "name": "anchor", "outputs": [{"internalType": "uint256", "name": "index", "type": "uint256"}],
     "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [], "name": "latest",
     "outputs": [{"internalType": "bytes32", "name": "hash", "type": "bytes32"},
                 {"internalType": "uint64", "name": "timestamp", "type": "uint64"},
                 {"internalType": "address", "name": "anchorer", "type": "address"},
                 {"internalType": "string", "name": "label", "type": "string"}],
     "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "proofCount",
     "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"},
]


def _read_feed(path: str) -> bytes:
    if path == "-":
        return sys.stdin.buffer.read()
    with open(path, "rb") as f:
        return f.read()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--feed", required=True, help="path to feed snapshot, or '-' for stdin")
    ap.add_argument("--label", default=None, help="human label; default nav-YYYY-MM-DD")
    ap.add_argument("--dry-run", action="store_true", help="compute + print hash, do not send")
    args = ap.parse_args()

    label = args.label or f"nav-{_dt.date.today().isoformat()}"

    try:
        from web3 import Web3
    except ImportError:
        print("web3 not installed; pip install web3", file=sys.stderr)
        return 2

    payload = _read_feed(args.feed)
    proof_hash = Web3.keccak(payload)  # bytes32 commitment over the snapshot
    print(f"label={label} hash=0x{proof_hash.hex()} bytes={len(payload)}")

    armed = os.getenv("BABA_PROOF_ANCHOR_ARM") == "1"
    addr = os.getenv("BABA_PROOF_REGISTRY_ADDR")
    key = os.getenv("BABA_PROOF_ANCHORER_KEY")
    rpc = os.getenv("BASE_RPC_URL", "https://mainnet.base.org")

    if args.dry_run or not (armed and addr and key):
        why = "dry-run" if args.dry_run else "DARK (set ARM=1 + REGISTRY_ADDR + ANCHORER_KEY to send)"
        print(f"[no-op] {why} — nothing sent.")
        return 0

    w3 = Web3(Web3.HTTPProvider(rpc))
    if not w3.is_connected():
        print(f"cannot reach RPC {rpc}", file=sys.stderr)
        return 3
    reg = w3.eth.contract(address=Web3.to_checksum_address(addr), abi=ABI)

    # idempotency: skip if the latest on-chain hash already matches
    try:
        if reg.functions.proofCount().call() > 0:
            last_hash = reg.functions.latest().call()[0]
            if last_hash == proof_hash:
                print("[skip] latest on-chain hash already matches this snapshot.")
                return 0
    except Exception as e:  # first anchor / transient read miss — proceed
        print(f"[warn] latest() read failed ({e}); proceeding to anchor.")

    acct = w3.eth.account.from_key(key)
    tx = reg.functions.anchor(proof_hash, label).build_transaction({
        "from": acct.address,
        "nonce": w3.eth.get_transaction_count(acct.address),
        "chainId": 8453,  # Base mainnet
    })
    # let the node estimate gas; cap fees conservatively for Base
    tx.setdefault("maxFeePerGas", w3.to_wei(0.05, "gwei"))
    tx.setdefault("maxPriorityFeePerGas", w3.to_wei(0.001, "gwei"))
    signed = acct.sign_transaction(tx)
    txh = w3.eth.send_raw_transaction(signed.raw_transaction)
    rcpt = w3.eth.wait_for_transaction_receipt(txh, timeout=180)
    print(f"[anchored] tx=0x{txh.hex()} block={rcpt['blockNumber']} status={rcpt['status']}")
    return 0 if rcpt["status"] == 1 else 4


if __name__ == "__main__":
    raise SystemExit(main())
