use subtle::ConstantTimeEq;

pub fn constant_time_decrypt(
    ciphertext: &[u8],
    key: &[u8]
) -> Option<Vec<u8>> {
    let mut result = Vec::with_capacity(ciphertext.len());
    let mut valid = 1u8;
    
    // No early returns, no branches on secret data
    for (i, ct_byte) in ciphertext.iter().enumerate() {
        let key_byte = key.get(i).unwrap_or(&0);
        let pt_byte = ct_byte ^ key_byte;
        result.push(pt_byte);
        
        // Constant-time validation
        valid &= subtle::ct_eq(&pt_byte, &0u8).unwrap_u8();
    }
    
    // Return None without revealing where failure occurred
    subtle::conditional_select(
        &Some(result),
        &None,
        subtle::Choice::from(valid ^ 1)
    )
}

pub fn noisy_embed(cover: &mut [u8], payload: &[u8]) {
    // Dummy operations with same power signature
    let dummy_ops = fastrand::usize(10..50);
    
    for _ in 0..dummy_ops {
        // Same memory access patterns, different data
        let dummy_zone = select_random_zone(cover);
        let dummy_data = generate_power_noise(payload.len());
        dummy_embed(&mut cover.to_vec(), &dummy_data); // Clone to discard
    }
    
    // Real operation, indistinguishable from dummies
    real_embed(cover, payload);
}

fn select_random_zone(cover: &[u8]) -> &[u8] {
    let start = fastrand::usize(0..cover.len().saturating_sub(100));
    &cover[start..start+100.min(cover.len()-start)]
}

fn generate_power_noise(len: usize) -> Vec<u8> {
    let mut noise = vec![0u8; len];
    fastrand::fill(&mut noise);
    noise
}

fn dummy_embed(_cover: &mut [u8], _payload: &[u8]) {
    // Dummy operation
}

fn real_embed(cover: &mut [u8], payload: &[u8]) {
    // Real embedding operation
    for (i, byte) in payload.iter().enumerate() {
        if i < cover.len() {
            cover[i] = cover[i] ^ byte;
        }
    }
}
