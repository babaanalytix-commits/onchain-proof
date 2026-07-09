"""
Provenance + freshness tagging — every value carries where it came from and
when it was read. This is the whole point of "trustless": a number you can
trace back to an on-chain source and a block, not a screenshot.
"""
import time


def tag(value, source: str, block: int = None, fetched_at: float = None) -> dict:
    return {
        "value": value,
        "source": source,                       # e.g. "eth_call balanceOf @ base"
        "block": block,
        "fetched_at": fetched_at if fetched_at is not None else time.time(),
    }


def stamp_report(report: dict, rpc_url: str, chain: str, block: int) -> dict:
    report["provenance"] = {
        "chain": chain,
        "rpc": rpc_url,
        "block": block,
        "fetched_at": time.time(),
        "method": "read-only eth_call / eth_getBalance",
        "note": "Reconstructed from on-chain state. Independently verifiable; no screenshots.",
    }
    return report
