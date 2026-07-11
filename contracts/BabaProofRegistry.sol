// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title BabaProofRegistry
/// @author BABA Capital (alaye.base.eth)
/// @notice Tamper-evident, on-chain anchor for BABA Capital's verifiable track record.
///         Each anchor commits a content hash (e.g. keccak256 of a day's reconciled
///         NAV or a week's trade-result feed) together with a human-readable label and
///         the block timestamp. This is the on-chain half of the open-source
///         `onchain-proof` tool: off-chain, anyone can recompute the hash from BABA's
///         public feed and check it matches what was committed here at that block time —
///         proof the record was not edited after the fact.
/// @dev Intentionally dependency-free so the source verifies cleanly on BaseScan.
contract BabaProofRegistry {
    struct Proof {
        bytes32 hash;       // content commitment (e.g. keccak256 of the feed snapshot)
        uint64  timestamp;  // block time of the anchor
        address anchorer;   // who submitted it
        string  label;      // e.g. "nav-2026-07-11" or "oracle-week-28"
    }

    address public owner;
    mapping(address => bool) public isAnchorer; // addresses allowed to anchor
    Proof[] private _proofs;

    event Anchored(
        uint256 indexed index,
        bytes32 indexed hash,
        address indexed anchorer,
        uint64 timestamp,
        string label
    );
    event AnchorerSet(address indexed account, bool allowed);
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    modifier onlyOwner() {
        require(msg.sender == owner, "not owner");
        _;
    }

    constructor() {
        owner = msg.sender;
        isAnchorer[msg.sender] = true; // deployer can anchor by default
        emit OwnershipTransferred(address(0), msg.sender);
        emit AnchorerSet(msg.sender, true);
    }

    /// @notice Commit a proof hash. Callable by the owner or any authorized anchorer.
    /// @param hash  content commitment; must be non-zero.
    /// @param label human-readable tag for the proof.
    /// @return index the position of the new proof in the registry.
    function anchor(bytes32 hash, string calldata label) external returns (uint256 index) {
        require(msg.sender == owner || isAnchorer[msg.sender], "not authorized");
        require(hash != bytes32(0), "empty hash");
        index = _proofs.length;
        _proofs.push(
            Proof({hash: hash, timestamp: uint64(block.timestamp), anchorer: msg.sender, label: label})
        );
        emit Anchored(index, hash, msg.sender, uint64(block.timestamp), label);
    }

    /// @notice Authorize or revoke an anchoring address (e.g. the engine's operational key).
    function setAnchorer(address account, bool allowed) external onlyOwner {
        isAnchorer[account] = allowed;
        emit AnchorerSet(account, allowed);
    }

    /// @notice Hand the registry to a new owner (e.g. a multisig later).
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "zero owner");
        emit OwnershipTransferred(owner, newOwner);
        owner = newOwner;
    }

    // ---------------- views ----------------

    function proofCount() external view returns (uint256) {
        return _proofs.length;
    }

    function getProof(uint256 index)
        external
        view
        returns (bytes32 hash, uint64 timestamp, address anchorer, string memory label)
    {
        require(index < _proofs.length, "out of range");
        Proof storage p = _proofs[index];
        return (p.hash, p.timestamp, p.anchorer, p.label);
    }

    function latest()
        external
        view
        returns (bytes32 hash, uint64 timestamp, address anchorer, string memory label)
    {
        require(_proofs.length > 0, "no proofs");
        Proof storage p = _proofs[_proofs.length - 1];
        return (p.hash, p.timestamp, p.anchorer, p.label);
    }
}
