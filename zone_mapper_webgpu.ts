export interface Zone {
    type: 'EDGE' | 'TEXTURE' | 'OBJECT' | 'COLOR';
    bbox: [number, number, number, number]; // x, y, w, h
    params: Record<string, number>;
}

export class ZoneMapperWebGPU {
    device!: GPUDevice;
    pipeline!: GPUComputePipeline;
    
    async init() {
        const adapter = await navigator.gpu.requestAdapter();
        if (!adapter) {
            throw new Error('WebGPU not supported');
        }
        this.device = await adapter.requestDevice();
        
        const shaderModule = this.device.createShaderModule({
            code: await fetch('/shaders/zone_detect.wgsl').then(r => r.text())
        });
        
        this.pipeline = this.device.createComputePipeline({
            layout: 'auto',
            compute: { module: shaderModule, entryPoint: 'main' }
        });
    }
    
    async mapZones(imageData: ImageData): Promise<Zone[]> {
        const texture = this.device.createTexture({
            size: [imageData.width, imageData.height],
            format: 'rgba8unorm',
            usage: GPUTextureUsage.TEXTURE_BINDING | GPUTextureUsage.COPY_DST
        });
        
        // Upload image
        this.device.queue.writeTexture(
            { texture },
            imageData.data,
            { bytesPerRow: imageData.width * 4 },
            [imageData.width, imageData.height]
        );
        
        // Create output buffer
        const outputSize = imageData.width * imageData.height * 4;
        const outputBuffer = this.device.createBuffer({
            size: outputSize,
            usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_SRC
        });
        
        // Create bind group
        const bindGroup = this.device.createBindGroup({
            layout: this.pipeline.getBindGroupLayout(0),
            entries: [
                { binding: 0, resource: texture.createView() },
                { binding: 1, resource: { buffer: outputBuffer } }
            ]
        });
        
        // Run compute
        const commandEncoder = this.device.createCommandEncoder();
        const pass = commandEncoder.beginComputePass();
        pass.setPipeline(this.pipeline);
        pass.setBindGroup(0, bindGroup);
        pass.dispatchWorkgroups(
            Math.ceil(imageData.width / 16),
            Math.ceil(imageData.height / 16)
        );
        pass.end();
        
        // Read back
        const readBuffer = this.device.createBuffer({
            size: outputSize,
            usage: GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ
        });
        commandEncoder.copyBufferToBuffer(outputBuffer, 0, readBuffer, 0, outputSize);
        
        this.device.queue.submit([commandEncoder.finish()]);
        
        await readBuffer.mapAsync(GPUMapMode.READ);
        const scores = new Float32Array(readBuffer.getMappedRange().slice(0));
        
        // CPU: threshold + bbox extraction
        return this.extractZonesCPU(scores, imageData.width, imageData.height);
    }
    
    private extractZonesCPU(
        scores: Float32Array,
        width: number,
        height: number
    ): Zone[] {
        const zones: Zone[] = [];
        const threshold = 0.3;
        
        // Simple threshold-based zone detection
        for (let y = 0; y < height; y += 64) {
            for (let x = 0; x < width; x += 64) {
                let sum = 0;
                let count = 0;
                
                for (let dy = 0; dy < 64 && y + dy < height; dy++) {
                    for (let dx = 0; dx < 64 && x + dx < width; dx++) {
                        sum += scores[(y + dy) * width + (x + dx)];
                        count++;
                    }
                }
                
                const density = sum / count;
                if (density > threshold) {
                    zones.push({
                        type: 'EDGE',
                        bbox: [x, y, Math.min(64, width - x), Math.min(64, height - y)],
                        params: { density }
                    });
                }
            }
        }
        
        return zones.sort((a, b) => b.params.density - a.params.density);
    }
}
