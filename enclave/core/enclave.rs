//! SGX-style enclave simulation written in Rust for demonstration.
//! The code is intentionally simple and does not rely on SGX hardware.

use sha2::{Digest, Sha256};

/// Represents a loaded enclave.
pub struct Enclave {
    pub name: String,
    pub signer: String,
    pub mrenclave: String,
    pages: Vec<Vec<u8>>,
}

impl Enclave {
    /// Create and measure a new enclave from memory segments.
    pub fn new(name: &str, signer: &str, segments: &[Vec<u8>]) -> Self {
        let mut hasher = Sha256::new();
        for seg in segments {
            hasher.update(seg);
        }
        hasher.update(name.as_bytes());
        hasher.update(signer.as_bytes());
        let mrenclave = format!("{:x}", hasher.finalize());

        Self {
            name: name.to_string(),
            signer: signer.to_string(),
            mrenclave,
            pages: segments.to_vec(),
        }
    }

    /// Perform an ECALL into the enclave.
    pub fn ecall(&self, name: &str) -> String {
        format!("ECALL {} executed inside {}", name, self.name)
    }

    /// Simulate an OCALL to the untrusted host.
    pub fn ocall(&self, name: &str) -> String {
        format!("OCALL {} invoked by {}", name, self.name)
    }
}
