use wasm_bindgen::prelude::*;
use std::simd::{u8x16, Simd};
use rand::SeedableRng;
use rand_chacha::ChaCha8Rng;

#[wasm_bindgen]
pub fn embed_lsb_simd(
    image: &mut [u8],
    bits: &[u8],
    seed: u32,
    lsb_order: u8
) {
    let mask = 0xFF ^ (1 << (lsb_order - 1));
    let simd_mask = u8x16::splat(mask);
    let one = u8x16::splat(1 << (lsb_order - 1));
    
    // ChaCha8 for deterministic pseudorandom indices
    let mut rng = ChaCha8Rng::seed_from_u64(seed as u64);
    
    let chunks = image.chunks_exact_mut(16);
    let bit_chunks = bits.chunks_exact(16);
    
    for (img_chunk, bit_chunk) in chunks.zip(bit_chunks) {
        let bits_vec = u8x16::from_slice(bit_chunk);
        let img_vec = u8x16::from_slice(img_chunk);
        
        // Clear LSB, set new bit
        let cleared = img_vec & simd_mask;
        let new_bits = bits_vec & one;
        (cleared | new_bits).copy_to_slice(img_chunk);
    }
}

#[wasm_bindgen]
pub fn extract_lsb_simd(
    image: &[u8],
    bit_count: usize,
    seed: u32,
    lsb_order: u8
) -> Vec<u8> {
    let mask = 1 << (lsb_order - 1);
    let mut rng = ChaCha8Rng::seed_from_u64(seed as u64);
    
    // Generate indices
    use rand::seq::index::sample;
    let indices = sample(&mut rng, image.len(), bit_count);
    
    let mut result = vec![0u8; (bit_count + 7) / 8];
    for (i, idx) in indices.iter().enumerate() {
        let bit = (image[idx] >> (lsb_order - 1)) & 1;
        result[i / 8] |= bit << (7 - (i % 8));
    }
    
    result
}
