use zeroize::{Zeroize, ZeroizeOnDrop};

#[derive(Zeroize, ZeroizeOnDrop)]
pub struct SecureBuffer {
    #[zeroize(skip)]
    ptr: *mut u8,
    len: usize,
}

impl SecureBuffer {
    pub fn new(len: usize) -> Self {
        let layout = std::alloc::Layout::from_size_align(len, 64).unwrap();
        let ptr = unsafe { std::alloc::alloc_zeroed(layout) };
        Self { ptr, len }
    }
    
    pub fn as_mut_slice(&mut self) -> &mut [u8] {
        unsafe { std::slice::from_raw_parts_mut(self.ptr, self.len) }
    }
    
    // Explicit mlock to prevent swap
    pub fn lock(&self) -> Result<(), Error> {
        #[cfg(unix)]
        unsafe {
            if libc::mlock(self.ptr as *const libc::c_void, self.len) != 0 {
                return Err(Error::MemoryLockFailed);
            }
        }
        Ok(())
    }
}

#[derive(Debug)]
pub enum Error {
    MemoryLockFailed,
}

// Automatic zeroization on drop, even on panic
impl Drop for SecureBuffer {
    fn drop(&mut self) {
        let layout = std::alloc::Layout::from_size_align(self.len, 64).unwrap();
        unsafe {
            std::alloc::dealloc(self.ptr, layout);
        }
    }
}
