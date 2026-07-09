# onchain-proof

Verify any wallet's DeFi holdings **trustlessly** — native + ERC-20 balances and
concentrated-liquidity (Uniswap-V3 / Aerodrome-Slipstream) positions, reconstructed
directly from on-chain state and reconciled into one canonical, no-double-count view,
with **provenance and freshness on every value**. No API keys, no screenshots, no trust.
Read-only. Zero dependencies (Python standard library only).

## Why
Most DeFi "track records" are screenshots — unverifiable and easy to fake. `onchain-proof`
rebuilds positions from chain state so **anyone can independently verify them**. It powers the
public proof page at [babacapital.app/proof](https://babacapital.app/proof) and is open-sourced
as a public good so the same verification is available to everyone.

## Install
```bash
git clone https://github.com/<you>/onchain-proof
cd onchain-proof
pip install -e .        # or just run it in place — no third-party deps
```

## Use
```bash
python -m onchain_proof verify 0xYourWallet \
  --chain base \
  --rpc https://mainnet.base.org \
  --tokens 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913   # (USDC on Base, optional)
```
Add `--json` for machine-readable output. Override the LP venue with `--npm 0x...`.

Each holding is printed with its on-chain source and the block it was read at — a native
balance, each ERC-20 you ask about, and every concentrated-liquidity NFT position (tick range,
liquidity, tokens owed), reconciled so nothing is counted twice.

## How it works
- **Discovery is config-free per wallet**: it enumerates the position-manager NFTs the wallet
  holds and reads each position's state. The only config is the NPM contract address per venue
  (`venues.py`), which you can override on the CLI.
- **No keccak / no crypto deps**: it uses the standard, published 4-byte function selectors
  (`balanceOf`, `decimals`, `symbol`, `positions`, `tokenOfOwnerByIndex`), so there's nothing to
  trust in the toolchain either.
- **Pure, tested core**: ABI encode/decode, tick→price math, and NAV reconciliation are pure
  functions with unit tests (`tests/`).

## Verify the addresses
`venues.py` ships the commonly-published NonfungiblePositionManager addresses, but you should
confirm them against each protocol's official docs before trusting a report (links are in the
file). An unknown NPM simply returns no positions — it can never produce a *wrong* balance.

## Supported
- **Base**: Uniswap V3, Aerodrome Slipstream. More chains/venues welcome via PR.

## Tests
```bash
python tests/test_abi.py && python tests/test_nav_positions.py
```

## License
MIT — see [LICENSE](LICENSE).
