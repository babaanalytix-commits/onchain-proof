"""
Tiny JSON-RPC client over the standard library (urllib). No deps.
Read-only: only eth_call / eth_getBalance / eth_blockNumber are used.
"""
import json
import urllib.request


class JsonRpc:
    def __init__(self, url: str, timeout: float = 20.0):
        self.url = url
        self.timeout = timeout
        self._id = 0

    def _call(self, method: str, params: list):
        self._id += 1
        payload = json.dumps({
            "jsonrpc": "2.0", "id": self._id, "method": method, "params": params,
        }).encode()
        req = urllib.request.Request(
            self.url, data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            out = json.loads(r.read().decode())
        if "error" in out and out["error"]:
            raise RuntimeError(f"RPC error: {out['error']}")
        return out.get("result")

    def block_number(self) -> int:
        return int(self._call("eth_blockNumber", []), 16)

    def get_balance(self, address: str, block: str = "latest") -> int:
        return int(self._call("eth_getBalance", [address, block]), 16)

    def eth_call(self, to: str, data: str, block: str = "latest") -> str:
        return self._call("eth_call", [{"to": to, "data": data}, block])
