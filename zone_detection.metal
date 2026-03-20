#include <metal_stdlib>
using namespace metal;

kernel void edge_detect(
    texture2d<float, access::read> in [[texture(0)]],
    device float* edge_scores [[buffer(0)]],
    uint2 gid [[thread_position_in_grid]]
) {
    float3x3 sobel_x = float3x3(-1, 0, 1, -2, 0, 2, -1, 0, 1);
    float3x3 sobel_y = float3x3(-1, -2, -1, 0, 0, 0, 1, 2, 1);
    
    float gx = 0, gy = 0;
    for (int i = -1; i <= 1; i++) {
        for (int j = -1; j <= 1; j++) {
            float lum = in.read(gid + uint2(i,j)).r;
            gx += lum * sobel_x[i+1][j+1];
            gy += lum * sobel_y[i+1][j+1];
        }
    }
    
    float magnitude = sqrt(gx*gx + gy*gy);
    edge_scores[gid.y * in.get_width() + gid.x] = magnitude;
}

kernel void dct_embed(
    texture2d<float, access::read_write> image [[texture(0)]],
    device const uint8_t* bits [[buffer(0)]],
    device const uint2* block_coords [[buffer(1)]],
    constant uint& num_blocks [[buffer(2)]],
    uint gid [[thread_position_in_grid]]
) {
    if (gid >= num_blocks) return;
    
    uint2 coord = block_coords[gid] * 8;
    threadgroup float block[8][8];
    
    // Load 8x8 to threadgroup
    for (int y = 0; y < 8; y++) {
        for (int x = 0; x < 8; x++) {
            block[y][x] = image.read(coord + uint2(x,y)).r - 128.0;
        }
    }
    
    threadgroup_barrier(mem_flags::mem_threadgroup);
    
    // DCT via matrix multiply (A * block * A^T)
    float temp[8][8], dct[8][8];
    // ... optimized DCT-II
    
    // Embed bit in coefficient (2,3) - mid-frequency
    uint bit_idx = gid;
    float target = dct[2][3];
    int desired_parity = bits[bit_idx / 8] >> (7 - (bit_idx % 8)) & 1;
    
    if ((int(round(target)) & 1) != desired_parity) {
        dct[2][3] += (target >= 0) ? 1.0 : -1.0;
    }
    
    // IDCT
    // ... write back
    image.write(float4(result + 128.0), coord + uint2(x,y));
}
