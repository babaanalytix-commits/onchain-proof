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
            "npm": "0x03a520b32C04BF3bEEf7BEb72E919cf822Ed34f1",
            "verify": "https://docs.uniswap.org/contracts/v3/reference/deployments/base-deployments",
        },
        "aerodrome_slipstream": {
            "npm": "0x827922686190790b37229fd06084350E74485b72",
            "verify": "https://aerodrome.finance/ (Slipstream NPM — verify before trusting)",
        },
    },
}

NATIVE_SYMBOL = {"base": "ETH", "ethereum": "ETH", "arbitrum": "ETH", "polygon": "POL"}


def npms_for(chain: str) -> list:
    out = []
    for venue, cfg in VENUES.get(chain, {}).items():
        out.append((venue, cfg["npm"]))
    return out
