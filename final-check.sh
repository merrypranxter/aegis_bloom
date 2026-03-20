#!/bin/bash
# final-check.sh - Pre-release verification

set -euo pipefail

echo "=== AEGISBLOOM FINAL RELEASE CHECKLIST ==="

# 1. Security
echo "[ ] Security: Kani proofs passing"
cargo kani --all --quiet

echo "[ ] Security: MIRAI clean"
cargo mirai 2>&1 | grep -q "0 errors" || exit 1

echo "[ ] Security: cargo-deny policy"
cargo deny check

echo "[ ] Security: No critical CVEs"
cargo audit --deny warnings

# 2. Testing
echo "[ ] Tests: Unit + integration"
cargo test --all-features

echo "[ ] Tests: E2E roundtrip (100 cases)"
PROPTEST_CASES=100 cargo test --test e2e --release

echo "[ ] Tests: Adversarial suite"
cargo test --test adversarial --release

# 3. Build
echo "[ ] Build: Reproducible hash match"
./scripts/build-reproducible.sh
./scripts/verify-reproducible.sh

echo "[ ] Build: All targets"
just build-all

# 4. Documentation
echo "[ ] Docs: API reference generated"
just docs

echo "[ ] Docs: Security whitepaper current"
test docs/security/whitepaper.md -nt src/lib.rs

# 5. Operations
echo "[ ] Ops: Runbooks reviewed"
test runbooks/incident-response/SEV-1-critical.md -nt .git/HEAD

echo "[ ] Ops: DR tested within 90 days"
./scripts/check-dr-test.sh

# 6. Signatures
echo "[ ] Sign: Sigstore signatures"
cosign verify-blob --signature ...

echo "[ ] Sign: SLSA provenance"
slsa-verifier verify-artifact ...

echo ""
echo "=== ALL CHECKS PASSED ==="
echo "Ready for: just deploy-stable v$(cat VERSION)"
