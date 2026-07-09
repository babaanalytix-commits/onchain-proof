"""
Example: verify a wallet on Base and print a reconciled, provenance-stamped report.

    python examples/verify_wallet.py 0xYourWallet

Uses the public Base RPC by default. Pass your own RPC as the 2nd arg.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from onchain_proof import verify_wallet

USDC_BASE = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"

if __name__ == "__main__":
    wallet = sys.argv[1] if len(sys.argv) > 1 else "0x0000000000000000000000000000000000000000"
    rpc = sys.argv[2] if len(sys.argv) > 2 else "https://mainnet.base.org"
    report = verify_wallet(rpc, wallet, chain="base", tokens=[USDC_BASE])
    print(f"block {report['provenance']['block']} · {report['count']} holdings · {report['by_kind']}")
    for h in report["holdings"]:
        print(" ", {k: h[k] for k in h if k not in ("amount_raw",)})
