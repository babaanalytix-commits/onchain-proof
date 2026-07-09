"""
NAV reconciliation: one canonical view of a wallet's holdings, no double-count.

Pure functions (no I/O) so they are unit-tested directly. Dedupe key is the
(chain, kind, address|npm, id) tuple — the same on-chain object can only be
counted once no matter how many sources reported it.
"""


def _key(h: dict) -> tuple:
    return (
        h.get("chain", ""),
        h.get("kind", ""),
        (h.get("address") or h.get("npm") or "").lower(),
        h.get("token_id", h.get("id", "")),
    )


def reconcile(holdings: list) -> dict:
    """Deduplicate holdings into a canonical set; keep the last seen per key."""
    unique = {}
    for h in holdings:
        unique[_key(h)] = h
    items = list(unique.values())
    by_kind = {}
    for h in items:
        by_kind[h.get("kind", "?")] = by_kind.get(h.get("kind", "?"), 0) + 1
    return {
        "holdings": items,
        "count": len(items),
        "by_kind": by_kind,
        "lp_active": sum(1 for h in items if h.get("kind") == "lp" and h.get("active")),
    }
