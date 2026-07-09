import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from onchain_proof import abi


def w(hexword):  # pad a short hex to a 32-byte word
    return hexword.rjust(64, "0")


def test_encode_balance_of():
    addr = "0x" + "ab" * 20
    data = abi.encode_call(abi.SELECTORS["balanceOf(address)"], addr)
    assert data.startswith("0x70a08231")
    assert data[10:] == ("ab" * 20).rjust(64, "0")
    assert len(data) == 2 + 8 + 64


def test_encode_uint_arg():
    data = abi.encode_call(abi.SELECTORS["tokenOfOwnerByIndex(address,uint256)"],
                           "0x" + "11" * 20, 5)
    assert data.startswith("0x2f745c59")
    assert data.endswith(format(5, "064x"))


def test_dec_uint_and_address():
    blob = "0x" + w("de0b6b3a7640000") + w("000000000000000000000000" + "cd" * 20)[-64:]
    assert abi.dec_uint(blob, 0) == 0xde0b6b3a7640000
    assert abi.dec_address(blob, 1) == "0x" + "cd" * 20


def test_dec_int_negative():
    # -100 as 256-bit two's complement
    neg = format((1 << 256) - 100, "064x")
    assert abi.dec_int("0x" + neg, 0) == -100
    assert abi.dec_int("0x" + w("64"), 0) == 100  # +100


def test_dec_string():
    # ABI string "USDC": offset(32) + length(4) + data
    blob = "0x" + w("20") + w("4") + ("55534443".ljust(64, "0"))
    assert abi.dec_string(blob) == "USDC"


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn(); print("ok", name)
