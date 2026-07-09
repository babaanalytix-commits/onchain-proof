"""
Minimal ABI encode/decode — no third-party deps, no keccak needed.

We hardcode the well-known 4-byte function selectors (first 4 bytes of
keccak256(signature)) so the tool needs no crypto library. Every selector
below is a standard, widely-published value; see SELECTORS for the source
signatures.

All functions here are PURE (no I/O) so they are unit-tested directly.
"""

# Standard 4-byte selectors (keccak256(signature)[:4]). These are universal
# across every EVM chain and contract that implements the interface.
SELECTORS = {
    "balanceOf(address)":            "70a08231",  # ERC-20 + ERC-721
    "decimals()":                    "313ce567",  # ERC-20
    "symbol()":                      "95d89b41",  # ERC-20 / ERC-721
    "tokenOfOwnerByIndex(address,uint256)": "2f745c59",  # ERC-721 Enumerable
    "positions(uint256)":            "99fbab88",  # Uniswap-V3-style NPM
    "ownerOf(uint256)":              "6352211e",  # ERC-721
}


def _strip(hexstr: str) -> str:
    return hexstr[2:] if hexstr.startswith(("0x", "0X")) else hexstr


def pad_word(hexstr: str) -> str:
    """Right-align a hex value into one 32-byte (64-hex-char) word."""
    h = _strip(hexstr)
    return h.rjust(64, "0")


def enc_address(addr: str) -> str:
    a = _strip(addr).lower()
    if len(a) != 40:
        raise ValueError(f"bad address: {addr}")
    return a.rjust(64, "0")


def enc_uint(value: int) -> str:
    if value < 0:
        raise ValueError("enc_uint is unsigned")
    return format(value, "064x")


def encode_call(selector_hex: str, *args) -> str:
    """selector_hex is the 8-char selector (no 0x). args are int | address-str."""
    data = _strip(selector_hex)
    for a in args:
        if isinstance(a, int):
            data += enc_uint(a)
        elif isinstance(a, str):
            data += enc_address(a)
        else:
            raise TypeError(f"unsupported arg type: {type(a)}")
    return "0x" + data


# ── return decoders (operate on the hex return string) ──────────────────

def words(ret_hex: str):
    """Split a return blob into 32-byte (64-hex) words."""
    h = _strip(ret_hex)
    return [h[i:i + 64] for i in range(0, len(h), 64)]


def dec_uint(ret_hex: str, index: int = 0) -> int:
    w = words(ret_hex)
    if index >= len(w):
        return 0
    return int(w[index], 16)


def dec_address(ret_hex: str, index: int = 0) -> str:
    w = words(ret_hex)
    if index >= len(w):
        return "0x" + "0" * 40
    return "0x" + w[index][-40:]


def dec_int(ret_hex: str, index: int = 0, bits: int = 256) -> int:
    """Decode a signed integer (two's-complement, sign-extended to 256 bits)."""
    v = dec_uint(ret_hex, index)
    if v >= 2 ** 255:           # sign bit of the full 256-bit word set
        v -= 2 ** 256
    return v


def dec_string(ret_hex: str) -> str:
    """Decode an ABI dynamic string return (offset, length, data)."""
    w = words(ret_hex)
    if len(w) < 3:
        # Some tokens (e.g. MKR) return a bytes32 symbol instead of a string.
        try:
            return bytes.fromhex(w[0]).rstrip(b"\x00").decode("utf-8", "ignore")
        except Exception:
            return ""
    length = int(w[1], 16)
    data = "".join(w[2:])[: length * 2]
    try:
        return bytes.fromhex(data).decode("utf-8", "ignore")
    except Exception:
        return ""
