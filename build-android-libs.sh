#!/bin/bash
set -e

export ANDROID_NDK_HOME=$ANDROID_HOME/ndk/$ANDROID_NDK_VERSION
TOOLCHAIN=$ANDROID_NDK_HOME/toolchains/llvm/prebuilt/linux-x86_64

TARGETS=(
    "aarch64-linux-android:arm64-v8a:21"
    "armv7-linux-androideabi:armeabi-v7a:21"
    "x86_64-linux-android:x86_64:21"
    "i686-linux-android:x86:21"
)

OUTPUT_DIR="android/app/src/main/jniLibs"
mkdir -p $OUTPUT_DIR

for target_tuple in "${TARGETS[@]}"; do
    IFS=: read -r target arch min_sdk <<< "$target_tuple"
    
    export CC="$TOOLCHAIN/bin/${target}${min_sdk}-clang"
    export CXX="$TOOLCHAIN/bin/${target}${min_sdk}-clang++"
    export AR="$TOOLCHAIN/bin/llvm-ar"
    
    echo "Building $target..."
    cargo build --release --target $target --features "vulkan"
    
    mkdir -p $OUTPUT_DIR/$arch
    cp target/$target/release/libaegisbloom.so $OUTPUT_DIR/$arch/
    
    # Strip debug symbols
    $TOOLCHAIN/bin/llvm-strip $OUTPUT_DIR/$arch/libaegisbloom.so
done

echo "Android build complete!"
