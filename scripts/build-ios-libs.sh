#!/bin/bash
set -e

TARGETS=(
    "aarch64-apple-ios"
    "aarch64-apple-ios-sim"
    "x86_64-apple-ios"
)

OUTPUT_DIR="ios/Frameworks"
mkdir -p $OUTPUT_DIR

# Build each target
for target in "${TARGETS[@]}"; do
    echo "Building $target..."
    cargo build --release --target $target --features metal
done

# Create universal binary for simulators
lipo -create \
    target/aarch64-apple-ios-sim/release/libaegisbloom.a \
    target/x86_64-apple-ios/release/libaegisbloom.a \
    -output $OUTPUT_DIR/libaegisbloom-sim.a

# Copy device binary
cp target/aarch64-apple-ios/release/libaegisbloom.a $OUTPUT_DIR/

# Generate modulemap
cat > $OUTPUT_DIR/module.modulemap <<EOF
module AegisBloomCore {
    umbrella header "AegisBloomCore.h"
    export *
    link "aegisbloom"
}
EOF

# Create xcframework
xcodebuild -create-xcframework \
    -library $OUTPUT_DIR/libaegisbloom.a -headers $OUTPUT_DIR/include \
    -library $OUTPUT_DIR/libaegisbloom-sim.a -headers $OUTPUT_DIR/include \
    -output $OUTPUT_DIR/AegisBloomCore.xcframework

# Strip symbols for release
strip -x $OUTPUT_DIR/AegisBloomCore.xcframework/*/libaegisbloom.a

echo "iOS build complete!"
