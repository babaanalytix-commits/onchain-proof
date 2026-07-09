"""ERC-20 reads: balance, decimals, symbol. Read-only, via eth_call."""
from . import abi


def balance_of(rpc, token: str, owner: str) -> int:
    data = abi.encode_call(abi.SELECTORS["balanceOf(address)"], owner)
    return abi.dec_uint(rpc.eth_call(token, data))


def decimals(rpc, token: str) -> int:
    try:
        data = abi.encode_call(abi.SELECTORS["decimals()"])
        d = abi.dec_uint(rpc.eth_call(token, data))
        return d if 0 <= d <= 36 else 18
    except Exception:
        return 18


def symbol(rpc, token: str) -> str:
    try:
        data = abi.encode_call(abi.SELECTORS["symbol()"])
        return abi.dec_string(rpc.eth_call(token, data)) or "?"
    except Exception:
        return "?"


def holding(rpc, token: str, owner: str) -> dict:
    """Full ERC-20 holding for a wallet: raw + human amount, symbol, decimals."""
    raw = balance_of(rpc, token, owner)
    dec = decimals(rpc, token)
    return {
        "kind": "erc20",
        "address": token.lower(),
        "symbol": symbol(rpc, token),
        "decimals": dec,
        "amount_raw": raw,
        "amount": raw / (10 ** dec) if dec >= 0 else raw,
    }
