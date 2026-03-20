# AegisBloom

**Secure steganographic messenger with AI-aware obfuscation**

[![cargo-deny](https://img.shields.io/badge/cargo--deny-passing-green)]()
[![cargo-vet](https://img.shields.io/badge/cargo--vet-audited-blue)]()
[![Kani](https://img.shields.io/badge/Kani-verified-purple)]()
[![Sigstore](https://img.shields.io/badge/Sigstore-signed-orange)]()
[![SLSA](https://img.shields.io/badge/SLSA-3-gold)]()

## Overview

AegisBloom is a steganographic communication system that hides encrypted messages within images using AI-driven adaptive techniques. It combines:

- **AES-256-GCM encryption** for message confidentiality
- **Adaptive steganography** (LSB, DCT, pixel modulation) for covert embedding
- **AI-aware obfuscation** using Cognitive Decryption Instructions (CDIs)
- **Reed-Solomon ECC** for robustness against image transformations

## Architecture

```
[Sender] → AES-256(GCM) → Fragment → Adaptive Stego → [Image] → Server → [Receiver] → AI Extraction → Decrypt
```

## Quick Start

```python
from aegisbloom import AegisBloom

# Create instance with passphrase-derived key
bloom = AegisBloom.from_passphrase("correct horse battery staple")

# Embed message into cover image
stego = bloom.embed("Secret message", "cover.png")
stego.save("stego.png")

# Extract message
extracted = bloom.extract("stego.png")
print(extracted)  # "Secret message"
```

## Security

- **Memory safety:** Rust with formal verification (Kani)
- **Constant-time crypto:** Verified with dudect
- **Hardened allocator:** Guard pages, canaries, mandatory zeroization
- **Supply chain:** Vendored dependencies, reproducible builds, SLSA Level 3

See [docs/security/whitepaper.md](docs/security/whitepaper.md) for full security analysis.

## Building

```bash
# Install dependencies
just setup

# Build all targets
just build-all

# Run tests
just test

# Security audit
just audit
```

## Platforms

| Platform | Status | GPU Acceleration |
|----------|--------|------------------|
| iOS 15+ | ✅ Supported | Metal |
| Android 10+ | ✅ Supported | Vulkan |
| Web/WASM | ✅ Supported | WebGPU |
| Linux | ✅ Supported | CPU |
| macOS | ✅ Supported | Metal |

## Documentation

- [Security Whitepaper](docs/security/whitepaper.md)
- [API Reference](docs/api/)
- [Operational Runbooks](runbooks/)

## License

MIT OR Apache-2.0

---

**AEGISBLOOM v1.2.3** - *Ship it.* 🚀
