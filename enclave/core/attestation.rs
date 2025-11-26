//! Simulated attestation support for the demo enclave.
use rand::RngCore;
use sha2::{Digest, Sha256};

/// A mock attestation quote consisting of measurement and nonce.
pub struct Quote {
    pub mrenclave: String,
    pub signer: String,
    pub nonce: String,
    pub signature: String,
}

impl Quote {
    pub fn new(mrenclave: &str, signer: &str) -> Self {
        let mut nonce_bytes = [0u8; 16];
        rand::thread_rng().fill_bytes(&mut nonce_bytes);
        let nonce = hex::encode(nonce_bytes);
        let mut hasher = Sha256::new();
        hasher.update(mrenclave.as_bytes());
        hasher.update(signer.as_bytes());
        hasher.update(&nonce_bytes);
        let signature = format!("{:x}", hasher.finalize());
        Self {
            mrenclave: mrenclave.to_string(),
            signer: signer.to_string(),
            nonce,
            signature,
        }
    }
}
