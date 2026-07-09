"""
onchain-proof — verify any wallet's on-chain holdings trustlessly.

Read-only. Reconstructs native + ERC-20 balances and concentrated-liquidity
(Uniswap-V3 / Aerodrome-Slipstream) positions directly from chain state, then
reconciles a canonical, no-double-count view with provenance on every value.

Public good: powers the BABA Capital proof page, open-sourced so anyone can
independently verify a track record instead of trusting a screenshot.
"""
from . import abi, rpc, erc20, positions, nav, provenance, venues

__version__ = "0.1.0"
__all__ = ["abi", "rpc", "erc20", "positions", "nav", "provenance", "venues",
           "verify_wallet"]


def verify_wallet(rpc_url: str, wallet: str, chain: str = "base",
                  tokens=None, npms=None) -> dict:
    """
    Build a full, reconciled, provenance-stamped holdings report for a wallet.

    rpc_url : an EVM JSON-RPC endpoint for `chain`
    wallet  : the address to verify
    tokens  : optional list of ERC-20 addresses to check balances for
    npms    : optional list of NonfungiblePositionManager addresses
              (defaults to the known venues for `chain`)
    """
    client = rpc.JsonRpc(rpc_url)
    block = client.block_number()
    holdings = []

    # Native balance
    nat_raw = client.get_balance(wallet)
    holdings.append({
        "kind": "native", "chain": chain,
        "symbol": venues.NATIVE_SYMBOL.get(chain, "ETH"),
        "address": "native", "amount_raw": nat_raw, "amount": nat_raw / 1e18,
    })

    # ERC-20 balances (only the tokens the caller asks about)
    for t in (tokens or []):
        try:
            h = erc20.holding(client, t, wallet)
            h["chain"] = chain
            holdings.append(h)
        except Exception as e:
            holdings.append({"kind": "erc20", "chain": chain, "address": t,
                             "error": str(e)})

    # LP positions across each NPM
    npm_list = npms if npms is not None else [a for _, a in venues.npms_for(chain)]
    for npm in npm_list:
        try:
            for pos in positions.discover_positions(client, npm, wallet):
                pos["chain"] = chain
                holdings.append(pos)
        except Exception as e:
            holdings.append({"kind": "lp", "chain": chain, "npm": npm,
                             "error": str(e)})

    report = nav.reconcile(holdings)
    return provenance.stamp_report(report, rpc_url, chain, block)
