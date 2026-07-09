import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from onchain_proof import nav, positions, abi


def test_reconcile_dedup():
    holdings = [
        {"chain": "base", "kind": "erc20", "address": "0xAAA", "amount": 1},
        {"chain": "base", "kind": "erc20", "address": "0xaaa", "amount": 2},  # dup (case)
        {"chain": "base", "kind": "lp", "npm": "0xN", "token_id": 7, "active": True},
        {"chain": "base", "kind": "lp", "npm": "0xN", "token_id": 8, "active": False},
        {"chain": "base", "kind": "native", "address": "native", "amount": 0.5},
    ]
    r = nav.reconcile(holdings)
    assert r["count"] == 4                      # the two 0xAAA collapse to one
    assert r["by_kind"]["erc20"] == 1
    assert r["by_kind"]["lp"] == 2
    assert r["lp_active"] == 1


def test_tick_to_price():
    assert abs(positions.tick_to_price(0) - 1.0) < 1e-12
    assert positions.tick_to_price(100) > 1.0
    assert positions.tick_to_price(-100) < 1.0


def _word(hexword):
    return hexword.rjust(64, "0")


def test_read_position_decode():
    # Build a synthetic positions() return: 12 words.
    token0 = "0x" + "11" * 20
    token1 = "0x" + "22" * 20
    tick_lower = format((1 << 256) - 200, "064x")   # -200
    tick_upper = _word("12c")                        # 300
    blob = "0x" + "".join([
        _word("0"),                                  # 0 nonce
        _word("0"),                                  # 1 operator
        _word(token0[2:]),                           # 2 token0
        _word(token1[2:]),                           # 3 token1
        _word("64"),                                 # 4 fee/tickSpacing = 100
        tick_lower,                                  # 5 tickLower = -200
        tick_upper,                                  # 6 tickUpper = 300
        _word("3e8"),                                # 7 liquidity = 1000
        _word("0"), _word("0"),                      # 8,9 feeGrowth
        _word("5"), _word("7"),                      # 10,11 tokensOwed
    ])

    class FakeRpc:
        def eth_call(self, to, data, block="latest"):
            return blob
    pos = positions.read_position(FakeRpc(), "0xNPM", 42)
    assert pos["token_id"] == 42
    assert pos["token0"].endswith("11" * 20)
    assert pos["token1"].endswith("22" * 20)
    assert pos["tick_lower"] == -200
    assert pos["tick_upper"] == 300
    assert pos["liquidity"] == 1000
    assert pos["tokens_owed0"] == 5 and pos["tokens_owed1"] == 7


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn(); print("ok", name)
