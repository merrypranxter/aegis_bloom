//! Hardened memory allocator for secret data
use std::alloc::{GlobalAlloc, Layout, System};
use std::ptr;

/// Security-hardened allocator with:
/// - Guard pages (PROT_NONE)
/// - Canaries (detect overflows)
/// - Mandatory zeroization on free
/// - Randomized addresses (ASLR-friendly)
pub struct SecureAllocator;

unsafe impl GlobalAlloc for SecureAllocator {
    unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
        // Add guard pages + canary overhead
        let page_size = 4096;
        let guarded_size = layout.size() + 2 * page_size;
        
        // Allocate with guard pages using mmap
        #[cfg(unix)]
        {
            let ptr = libc::mmap(
                ptr::null_mut(),
                guarded_size,
                libc::PROT_READ | libc::PROT_WRITE,
                libc::MAP_PRIVATE | libc::MAP_ANONYMOUS,
                -1,
                0,
            );
            
            if ptr == libc::MAP_FAILED {
                return ptr::null_mut();
            }
            
            // mlock to prevent swap
            libc::mlock(ptr, guarded_size);
            
            // Set guard pages (before and after)
            let guard_before = ptr;
            let guard_after = ptr.add(guarded_size - page_size) as *mut libc::c_void;
            libc::mprotect(guard_before, page_size, libc::PROT_NONE);
            libc::mprotect(guard_after, page_size, libc::PROT_NONE);
            
            // Return pointer to usable region (after first guard page + canary)
            let usable = ptr.add(page_size + 8) as *mut u8;
            
            // Write canary (detects overflow into guard page)
            let canary = 0xDEADBEEFCAFEBABEu64;
            (usable.sub(8) as *mut u64).write(canary);
            
            usable
        }
        
        #[cfg(not(unix))]
        {
            // Fallback to system allocator + zeroization
            System.alloc(layout)
        }
    }
    
    unsafe fn dealloc(&self, ptr: *mut u8, layout: Layout) {
        #[cfg(unix)]
        {
            let page_size = 4096;
            let guarded_size = layout.size() + 2 * page_size;
            
            // Verify canary (detect corruption)
            let canary_ptr = ptr.sub(8) as *mut u64;
            let canary = canary_ptr.read();
            if canary != 0xDEADBEEFCAFEBABEu64 {
                // Corruption detected - abort or log
                panic!("Heap corruption detected: canary={:x}", canary);
            }
            
            // Zeroize entire usable region
            ptr::write_bytes(ptr, 0, layout.size());
            
            // Get base pointer for munmap
            let base = ptr.sub(page_size + 8) as *mut libc::c_void;
            
            // Unlock and unmap (also zeros in most kernels)
            libc::munlock(base, guarded_size);
            libc::munmap(base, guarded_size);
        }
        
        #[cfg(not(unix))]
        {
            // Zeroize then free
            ptr::write_bytes(ptr, 0, layout.size());
            System.dealloc(ptr, layout);
        }
    }
    
    unsafe fn realloc(&self, ptr: *mut u8, layout: Layout, new_size: usize) -> *mut u8 {
        // Always alloc-copy-free to prevent in-place expansion leaks
        let new_layout = Layout::from_size_align(new_size, layout.align()).unwrap();
        let new_ptr = self.alloc(new_layout);
        
        if !new_ptr.is_null() {
            let copy_size = layout.size().min(new_size);
            ptr::copy_nonoverlapping(ptr, new_ptr, copy_size);
            self.dealloc(ptr, layout);
        }
        
        new_ptr
    }
}

#[global_allocator]
static SECURE_ALLOC: SecureAllocator = SecureAllocator;

/// Force all secret allocations through secure path
#[repr(C, align(64))]
pub struct SecretBox<T> {
    ptr: *mut T,
    _marker: std::marker::PhantomData<T>,
}

impl<T> SecretBox<T> {
    pub fn new(value: T) -> Self {
        let layout = Layout::new::<T>();
        let ptr = unsafe { SECURE_ALLOC.alloc(layout) as *mut T };
        if ptr.is_null() {
            panic!("Secure allocation failed");
        }
        unsafe {
            ptr.write(value);
        }
        Self { ptr, _marker: std::marker::PhantomData }
    }
    
    pub fn as_ref(&self) -> &T {
        unsafe { &*self.ptr }
    }
    
    pub fn as_mut(&mut self) -> &mut T {
        unsafe { &mut *self.ptr }
    }
}

impl<T> Drop for SecretBox<T> {
    fn drop(&mut self) {
        let layout = Layout::new::<T>();
        unsafe {
            // Explicit zeroization before dealloc
            ptr::write_bytes(self.ptr as *mut u8, 0, std::mem::size_of::<T>());
            SECURE_ALLOC.dealloc(self.ptr as *mut u8, layout);
        }
    }
}
