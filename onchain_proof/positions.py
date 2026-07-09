"""
Concentrated-liquidity LP positions (Uniswap-V3 / Aerodrome-Slipstream style).

Discovery is CONFIG-FREE per wallet: enumerate the NonfungiblePositionManager
(NPM) NFTs the wallet holds, then read each position's on-chain state. The only
config is the NPM contract address per venue (see venues.py) — overridable on
the CLI.

positions(uint256) on a V3-style NPM returns 12 words:
  0 nonce  1 operator  2 token0  3 token1  4 fee/tickSpacing
  5 tickLower  6 tickUpper  7 liquidity  8 feeGrowth0  9 feeGrowth1
  10 tokensOwed0  11 tokensOwed1
We decode the economically meaningful ones.
"""
from . import abi


def tick_to_price(tick: int) -> float:
    """Raw price of token0 in token1 at a tick (before decimal adjustment).
    price = 1.0001 ** tick. Pure + testable (tick 0 -> 1.0)."""
    return 1.0001 ** tick


def adjusted_price(tick: int, dec0: int, dec1: int) -> float:
    """Human price of token0 in token1, decimal-adjusted."""
    return tick_to_price(tick) * (10 ** (dec0 - dec1))


def nft_count(rpc, npm: str, owner: str) -> int:
    data = abi.encode_call(abi.SELECTORS["balanceOf(address)"], owner)
    return abi.dec_uint(rpc.eth_call(npm, data))


def token_id_at(rpc, npm: str, owner: str, index: int) -> int:
    data = abi.encode_call(abi.SELECTORS["tokenOfOwnerByIndex(address,uint256)"], owner, index)
    return abi.dec_uint(rpc.eth_call(npm, data))


def read_position(rpc, npm: str, token_id: int) -> dict:
    data = abi.encode_call(abi.SELECTORS["positions(uint256)"], token_id)
    ret = rpc.eth_call(npm, data)
    return {
        "kind": "lp",
        "npm": npm.lower(),
        "token_id": token_id,
        "token0": abi.dec_address(ret, 2),
        "token1": abi.dec_address(ret, 3),
        "fee_or_tick_spacing": abi.dec_int(ret, 4),
        "tick_lower": abi.dec_int(ret, 5),
        "tick_upper": abi.dec_int(ret, 6),
        "liquidity": abi.dec_uint(ret, 7),
        "tokens_owed0": abi.dec_uint(ret, 10),
        "tokens_owed1": abi.dec_uint(ret, 11),
    }


def discover_positions(rpc, npm: str, owner: str) -> list:
    """All LP positions a wallet holds on one NPM. Active = liquidity > 0."""
    out = []
    n = nft_count(rpc, npm, owner)
    for i in range(n):
        tid = token_id_at(rpc, npm, owner, i)
        pos = read_position(rpc, npm, tid)
        pos["active"] = pos["liquidity"] > 0
        out.append(pos)
    return out
