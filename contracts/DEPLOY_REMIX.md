# Deploy `BabaProofRegistry` to Base — paste-and-click guide

**Goal:** deploy the contract from **`alaye.base.eth` (`0x6c83…`)** so the deploy is credited
to your Talent/Builder identity, then verify the source on BaseScan so it counts as a
*verified* contract. Cost ≈ **$0.02** in gas. You sign **one** transaction; your private
key never leaves your wallet.

> The contract has **no imports** — it verifies as a single file, no flattening needed.

---

## Before you start
- In your browser wallet, **switch the active account to `0x6c83…` (alaye.base.eth)** and
  make sure it's on the **Base** network with a little ETH (you have ~$0.90 — plenty).

---

## Step 1 — Open Remix and paste the contract
1. Go to **https://remix.ethereum.org**
2. In the File Explorer, create a new file: `BabaProofRegistry.sol`
3. Paste the full contents of `contracts/BabaProofRegistry.sol` into it.

## Step 2 — Compile (settings matter for verification)
1. Left sidebar → **Solidity Compiler**.
2. **Compiler:** `0.8.24` (any `0.8.24+commit…` build).
3. Click **Advanced Configurations** and set:
   - **Enable optimization:** ✅ ON, **Runs:** `200`
   - **EVM version:** leave `default`
4. Click **Compile BabaProofRegistry.sol**. Should compile with **no errors**.

   ⚠️ **Write these three down — you must reuse the exact same values when verifying:**
   `Compiler 0.8.24` · `Optimization ON / 200 runs` · `EVM default`.

## Step 3 — Deploy from your wallet
1. Left sidebar → **Deploy & Run Transactions**.
2. **Environment:** select **Injected Provider - MetaMask** (or your wallet). It will
   connect your browser wallet — confirm the **account reads `0x6c83…` and network is Base**.
3. Contract dropdown: `BabaProofRegistry`. Constructor takes **no arguments**.
4. Click **Deploy** → your wallet pops up → **review and Confirm** (this is the one gas'd tx).
5. When it confirms, expand the deployed contract in Remix and **copy the contract address**
   (also visible in the terminal log / your wallet activity).

## Step 4 — Verify the source on BaseScan
1. Go to **https://basescan.org/address/<YOUR_CONTRACT_ADDRESS>**
2. **Contract** tab → **Verify and Publish**.
3. Settings:
   - **Compiler Type:** Solidity (Single file)
   - **Compiler Version:** `v0.8.24+commit…` (match Step 2)
   - **Open Source License:** MIT
4. Next page:
   - **Optimization:** Yes, **Runs:** 200
   - **EVM Version:** `default`
   - Paste the full `BabaProofRegistry.sol` source into the code box.
5. Submit. You should see **"Contract Verified"** with a green check.

## Step 5 — Hand back to me
Send me the **contract address**. Then I:
- authorize a dedicated **engine anchorer key** via `setAnchorer(...)` (so your identity
  wallet stays cold while automation runs from a low-value operational key),
- wire the **weekly anchor job** (`anchor/baba_proof_anchor.py`) on the mini so every week
  a fresh proof hash of your reconciled track record gets committed on-chain — that's the
  *recurring* on-chain activity that keeps building your Builder Score.

---

### Why each step matters for Builder Score
- **Deploy from `0x6c83`** → attributes a *verified contract* to your builder wallet (the
  signal you're missing today).
- **Verify on BaseScan** → unverified contracts barely count; verified ones do.
- **Weekly anchors** → sustained, real on-chain usage, not a one-off deploy.
