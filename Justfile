# Justfile - task runner for local builds

set shell := ["bash", "-c"]

# Default: show available tasks
default:
    @just --list

# Install dependencies
setup:
    rustup target add aarch64-apple-ios x86_64-apple-ios aarch64-linux-android wasm32-unknown-unknown
    cargo install cargo-audit cargo-sbom wasm-pack
    gem install fastlane
    npm install -g wasm-opt

# Build all targets
build-all: build-ios build-android build-wasm

# iOS
build-ios:
    ./scripts/build-ios-libs.sh
    cd ios && xcodebuild -scheme AegisBloom -configuration Debug build

# Android
build-android:
    ./scripts/build-android-libs.sh
    cd android && ./gradlew assembleDebug

# WASM
build-wasm:
    cd wasm && wasm-pack build --target web --dev
    cd web && npm run build

# Test
test:
    cargo test --all-features
    cd wasm && wasm-pack test --headless --firefox

# Security audit
audit:
    cargo audit
    cargo deny check

# Clean
clean:
    cargo clean
    rm -rf ios/Frameworks android/app/src/main/jniLibs wasm/pkg web/dist

# Release (local dry-run)
release-dry-run:
    just build-all
    just audit
    echo "Dry run complete. Use CI for actual release."

# Generate documentation
docs: docs-rust docs-swift docs-kotlin docs-wasm docs-security

docs-rust:
    cargo doc --no-deps --document-private-items --features "all"
    cp -r target/doc docs/api/rust

docs-swift:
    cd ios && xcodebuild docbuild \
        -scheme AegisBloom \
        -destination 'platform=iOS Simulator,name=iPhone 15'
    $(xcrun --find docc) process-archive \
        transform-for-static-hosting \
        ios/build/Build/Products/Debug/AegisBloom.doccarchive \
        --output-path docs/api/swift

docs-kotlin:
    cd android && ./gradlew dokkaHtml
    cp -r sdk/build/dokka/html docs/api/kotlin

docs-wasm:
    cd wasm && npx typedoc \
        --out ../docs/api/wasm-ts \
        --entryPoints pkg/aegisbloom.d.ts

docs-security:
    pandoc docs/security/whitepaper.md \
        --template=eisvogel \
        --pdf-engine=xelatex \
        -o docs/security/whitepaper.pdf

# Serve docs locally
docs-serve:
    cd docs && python -m http.server 8000
