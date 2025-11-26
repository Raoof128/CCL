//! Demonstration of sealed storage.
use sha2::{Digest, Sha256};

/// Seal data to a pseudo-key derived from identity and measurement.
pub fn seal(identity: &str, mrenclave: &str, data: &[u8]) -> String {
    let mut key_hasher = Sha256::new();
    key_hasher.update(identity.as_bytes());
    key_hasher.update(mrenclave.as_bytes());
    let key = key_hasher.finalize();

    let mut cipher = Vec::with_capacity(data.len());
    for (i, byte) in data.iter().enumerate() {
        cipher.push(byte ^ key[i % key.len()]);
    }
    hex::encode(cipher)
}

/// Unseal data previously sealed with [`seal`].
pub fn unseal(identity: &str, mrenclave: &str, cipher_hex: &str) -> Vec<u8> {
    let cipher = hex::decode(cipher_hex).expect("ciphertext should be hex");
    let mut key_hasher = Sha256::new();
    key_hasher.update(identity.as_bytes());
    key_hasher.update(mrenclave.as_bytes());
    let key = key_hasher.finalize();

    cipher
        .iter()
        .enumerate()
        .map(|(i, byte)| byte ^ key[i % key.len()])
        .collect()
}
