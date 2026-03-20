# AegisBloom: Steganographic Messenger with AI-Aware Obfuscation

**Version:** 1.2.3  
**Date:** 2024-03-19  
**Classification:** Public  
**Authors:** AegisBloom Cryptographic Team

## Abstract

AegisBloom is a steganographic communication system combining AES-256-GCM encryption with AI-driven adaptive steganography. This document presents the security architecture, threat model, and formal security claims.

## 1. Cryptographic Design

### 1.1 Encryption Layer

- **Algorithm:** AES-256-GCM (Galois/Counter Mode)
- **Key Derivation:** Argon2id (m=64MB, t=3, p=4)
- **Nonce:** 96-bit random per message
- **Additional Data:** None (steganographic layer provides integrity)

**Security Claim:** IND-CCA2 secure under standard AES-GCM assumptions.

### 1.2 Steganographic Layer

- **Methods:** Adaptive LSB, DCT coefficient modification, pixel value modulation
- **Capacity:** Image-dependent, typically 0.1-1% of cover size
- **Detectability:** ε-indistinguishable from cover distribution

### 1.3 AI-Aware Obfuscation

- **Cognitive Decryption Instructions (CDIs):** Fragment location encoded via image content features
- **Fragmentation:** Variable-size with Reed-Solomon ECC
- **Key Derivation:** Contextual seeds from image statistics

**Security Claim:** Extraction requires both:
1. Shared symmetric key K
2. Pre-trained AI interpretation module M with parameters θ

## 2. Threat Model

### 2.1 Adversary Capabilities

| Class | Capabilities | Goals |
|-------|--------------|-------|
| Passive | Observe all network traffic, storage | Detect steganography use |
| Active | Modify/recompress images in transit | Destroy hidden messages |
| Forensic | Physical device access, memory dumps | Recover deleted messages |
| State | Side-channel monitoring, EM analysis | Extract keys or plaintext |

### 2.2 Security Goals

**Confidentiality:**
∀ adversary A with time t < 2^128: Pr[A(stego-image) = plaintext] < ε

**Undetectability:**
∀ statistical test T: |Pr[T(cover) = 1] - Pr[T(stego) = 1]| < ε

**Robustness:**
Message recoverable after JPEG recompression (quality ≥ 75), cropping ≤ 25%, Gaussian blur (σ ≤ 2).

### 2.3 Non-Goals

- **Traffic analysis resistance:** Message timing/presence observable
- **Plausible deniability:** Single-layer only (no hidden volumes in v1.x)
- **Quantum resistance:** Pre-quantum security only

## 3. Formal Security Analysis

### 3.1 Encryption Security

**Theorem 1 (IND-CCA2):**
Assuming AES-256 is a pseudorandom permutation and GCM is secure, AegisBloom encryption is IND-CCA2 secure.

### 3.2 Steganographic Security

**Theorem 2 (Adaptive LSB Security):**
For cover images with sufficient high-entropy regions (edge density ρ > 0.3), adaptive LSB embedding achieves ε-indistinguishability with ε = O(1/√n) for n embedding bits.

### 3.3 AI-Aware Layer Security

**Theorem 3 (CDI Extraction Hardness):**
Without AI module M, extracting fragments requires solving an NP-hard problem (reduction from set cover).

## 4. Implementation Security

### 4.1 Memory Safety

- Language: Rust (ownership-based safety)
- Unsafe code: 0.3% of codebase, all in `unsafe/` with Miri + Kani verification
- Hardened allocator: Guard pages, canaries, mandatory zeroization

### 4.2 Side-Channel Resistance

- Constant-time crypto: `subtle` crate, verified with dudect
- Power analysis: Dummy operations, noise injection
- Cache timing: Cache-line aligned tables, prefetch barriers

### 4.3 Supply Chain

- Vendored dependencies: All crypto and image processing
- Reproducible builds: Docker-based, hash-verified
- Signed releases: Sigstore keyless, SLSA Level 3

## 5. Verification Status

| Property | Tool | Status |
|----------|------|--------|
| Memory safety | Kani + Miri | ✅ Verified |
| Constant-time crypto | dudect | ✅ Verified |
| Roundtrip correctness | Proptest | ✅ 100K cases |
| No secret leakage | MIRAI | ✅ Verified |
| Reproducible builds | Deterministic Docker | ✅ Verified |

## 6. Known Limitations

1. **Cover image quality:** Low-entropy images (uniform backgrounds) insufficient for secure embedding. Detected at runtime with `analyze_cover()`.
2. **Active warden:** Determined adversary can destroy messages via aggressive recompression (quality < 50). Mitigated by redundancy.
3. **AI model extraction:** Adversary with physical device access can extract model weights. Mitigated by model binding to device keys.

## 7. References

- [Hopper et al., 2002] "Provably Secure Steganography"
- [Ferguson, 2005] "Authentication Weaknesses in GCM"
- [Bernsmed et al., 2022] "SLSA Framework for Supply Chain Security"

## Appendix A: Test Vectors

```hex
# AES-GCM test vector from NIST SP 800-38D
Key: 0000000000000000000000000000000000000000000000000000000000000000
IV:  000000000000000000000000
PT:  (empty)
AAD: (empty)
CT+Tag: 58e2fccefa7e3061367f1d57a4e7455a
```

## Appendix B: Formal Verification Artifacts

- Kani proofs: kani/proofs/ (symbolic execution)
- MIRAI taint analysis: mirai/config.json
- SLSA provenance: .github/workflows/slsa.yml
