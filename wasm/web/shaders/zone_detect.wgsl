@group(0) @binding(0) var inputTex: texture_2d<f32>;
@group(0) @binding(1) var<storage, read_write> edgeScores: array<f32>;

@compute @workgroup_size(16, 16)
fn main(@builtin(global_invocation_id) gid: vec3<u32>) {
    let dims = textureDimensions(inputTex);
    if (gid.x >= dims.x || gid.y >= dims.y) { return; }
    
    var gx: f32 = 0.0;
    var gy: f32 = 0.0;
    
    let sobel_x = mat3x3(
        -1.0, 0.0, 1.0,
        -2.0, 0.0, 2.0,
        -1.0, 0.0, 1.0
    );
    let sobel_y = mat3x3(
        -1.0, -2.0, -1.0,
         0.0,  0.0,  0.0,
         1.0,  2.0,  1.0
    );
    
    for (var y: i32 = -1; y <= 1; y++) {
        for (var x: i32 = -1; x <= 1; x++) {
            let sample = textureLoad(inputTex, vec2<i32>(gid.xy) + vec2<i32>(x,y), 0).r;
            gx += sample * sobel_x[y+1][x+1];
            gy += sample * sobel_y[y+1][x+1];
        }
    }
    
    let idx = gid.y * dims.x + gid.x;
    edgeScores[idx] = sqrt(gx*gx + gy*gy);
}
