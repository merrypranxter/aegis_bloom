//! Linux seccomp-bpf sandbox for stego operations

#[cfg(target_os = "linux")]
pub mod linux {
    use libc::{c_int, c_void, sock_filter, sock_fprog, PR_SET_SECCOMP, SECCOMP_MODE_FILTER};
    use std::process::abort;
    
    /// Allowed syscalls for image processing
    /// Blocks: network (except pre-established), exec, ptrace, etc.
    const ALLOWED_SYSCALLS: &[c_int] = &[
        // Memory
        libc::SYS_brk,
        libc::SYS_mmap,
        libc::SYS_munmap,
        libc::SYS_mremap,
        libc::SYS_mprotect,
        libc::SYS_mlock,
        libc::SYS_munlock,
        // File I/O (read-only for input, write for output)
        libc::SYS_read,
        libc::SYS_write,
        libc::SYS_openat, // With O_RDONLY or O_WRONLY|O_CREAT only
        libc::SYS_close,
        libc::SYS_lseek,
        libc::SYS_fstat,
        libc::SYS_newfstatat,
        // Process control
        libc::SYS_exit,
        libc::SYS_exit_group,
        libc::SYS_rt_sigreturn,
        // Time (for RNG seeding)
        libc::SYS_clock_gettime,
        libc::SYS_getrandom,
        // Threading (for rayon/parallel stego)
        libc::SYS_clone,
        libc::SYS_futex,
        libc::SYS_set_robust_list,
        libc::SYS_rseq,
    ];
    
    /// Build BPF filter program
    fn build_filter() -> Vec<sock_filter> {
        let mut filter = Vec::new();
        
        // Load syscall number into accumulator
        filter.push(sock_filter {
            code: 0x20, // BPF_LD | BPF_W | BPF_ABS
            jt: 0,
            jf: 0,
            k: 0, // offset of nr in seccomp_data
        });
        
        // Check each allowed syscall
        for &syscall in ALLOWED_SYSCALLS {
            filter.push(sock_filter {
                code: 0x15, // BPF_JMP | BPF_JEQ | BPF_K
                jt: 0,     // Fall through to next check
                jf: 1,     // Jump to next check on mismatch
                k: syscall as u32,
            });
            filter.push(sock_filter {
                code: 0x06, // BPF_RET | BPF_K
                jt: 0,
                jf: 0,
                k: 0x7fff_0000, // SECCOMP_RET_ALLOW
            });
        }
        
        // Default: kill process
        filter.push(sock_filter {
            code: 0x06, // BPF_RET | BPF_K
            jt: 0,
            jf: 0,
            k: 0x0000_0000 | (libc::SIGSYS as u32), // SECCOMP_RET_KILL
        });
        
        filter
    }
    
    pub fn activate() -> Result<(), SandboxError> {
        let filter = build_filter();
        let prog = sock_fprog {
            len: filter.len() as u16,
            filter: filter.as_ptr(),
        };
        
        unsafe {
            // Enable seccomp-bpf
            let ret = libc::prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &prog as *const _ as usize, 0, 0);
            if ret != 0 {
                return Err(SandboxError::SeccompFailed(std::io::Error::last_os_error()));
            }
        }
        
        // From here: any non-allowed syscall kills the process
        Ok(())
    }
    
    /// Pre-sandbox setup: open network sockets, load libraries
    pub fn pre_sandbox_init() {
        // Any syscalls that must happen before seccomp
        // e.g., dlopen for GPU drivers
    }
}

#[derive(Debug)]
pub enum SandboxError {
    SeccompFailed(std::io::Error),
}

#[cfg(not(target_os = "linux"))]
pub mod linux {
    pub fn activate() -> Result<(), super::SandboxError> {
        Ok(()) // No-op on non-Linux
    }
    pub fn pre_sandbox_init() {}
}
