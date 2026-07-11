"""
Verified venue addresses (NonfungiblePositionManager per chain).

IMPORTANT: addresses are config, not logic. The values below are the commonly
published NPM addresses, but you MUST verify them against each protocol's
official docs before trusting a report — and you can always override with
--npm on the CLI. Wrong address = empty/garbage, never a wrong balance (an
unknown NPM simply returns no positions).

Contributions welcome via PR: add a chain/venue with a cited source.
"""

# chain -> { venue -> {"npm": address, "verify": doc_url} }
VENUES = {
    "base": {
        "uniswap_v3": {
            # verified 2026-07-10 against BaseScan
            "npm": "0x03a520b32C04BF3bEEf7BEb72E919cf822Ed34f1",
            "verify": "https://basescan.org/address/0x03a520b32c04bf3beef7beb72e919cf822ed34f1",
        },
        "aerodrome_slipstream": {
            # verified 2026-07-10 against BaseScan (Slipstream initial deployment)
            "npm": "0x827922686190790b37229fd06084350E74485b72",
            "verify": "https://basescan.org/address/0x827922686190790b37229fd06084350e74485b72",
        },
    },
}

NATIVE_SYMBOL = {"base": "ETH", "ethereum": "ETH", "arbitrum": "ETH", "polygon": "POL"}


def npms_for(chain: str) -> list:
    out = []
    for venue, cfg in VENUES.get(chain, {}).items():
        out.append((venue, cfg["npm"]))
    return out
