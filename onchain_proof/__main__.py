"""CLI: python -m onchain_proof verify <wallet> --chain base --rpc <url>"""
import argparse
import json
import sys

from . import verify_wallet, venues


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="onchain_proof",
        description="Verify a wallet's on-chain holdings trustlessly (read-only).",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("verify", help="report a wallet's holdings + LP positions")
    v.add_argument("wallet", help="wallet address (0x...)")
    v.add_argument("--chain", default="base", help="chain key (default: base)")
    v.add_argument("--rpc", required=True, help="EVM JSON-RPC URL for the chain")
    v.add_argument("--tokens", default="", help="comma-separated ERC-20 addresses")
    v.add_argument("--npm", action="append", default=None,
                   help="NPM address override (repeatable); default = known venues")
    v.add_argument("--json", action="store_true", help="emit raw JSON")

    args = p.parse_args(argv)
    if args.cmd == "verify":
        tokens = [t.strip() for t in args.tokens.split(",") if t.strip()]
        report = verify_wallet(args.rpc, args.wallet, chain=args.chain,
                               tokens=tokens, npms=args.npm)
        if args.json:
            print(json.dumps(report, indent=2, default=str))
            return 0
        _print_human(args.wallet, report)
        return 0


def _print_human(wallet, report):
    prov = report.get("provenance", {})
    print(f"\nonchain-proof — {wallet}")
    print(f"  chain {prov.get('chain')} · block {prov.get('block')} · {prov.get('method')}")
    print(f"  {report['count']} holdings  {report.get('by_kind', {})}  "
          f"(active LP: {report.get('lp_active', 0)})\n")
    for h in report["holdings"]:
        if h.get("error"):
            print(f"  ! {h.get('kind')} {h.get('address') or h.get('npm')}: {h['error']}")
        elif h["kind"] == "native":
            print(f"  ◆ {h['amount']:.6f} {h['symbol']} (native)")
        elif h["kind"] == "erc20":
            print(f"  • {h['amount']:.6f} {h.get('symbol','?')}  [{h['address']}]")
        elif h["kind"] == "lp":
            state = "active" if h.get("active") else "closed"
            print(f"  ⬡ LP #{h['token_id']} {state}  ticks [{h['tick_lower']}, {h['tick_upper']}]  "
                  f"liq={h['liquidity']}  {h['token0']}/{h['token1']}")
    print(f"\n  {prov.get('note','')}\n")


if __name__ == "__main__":
    sys.exit(main())
