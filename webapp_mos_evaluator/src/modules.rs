use std::{fs::File, io::Write};

use serde::{Deserialize, Serialize};

pub mod authentication;
pub mod mos;
pub mod ref_synth;

// structs for the service
#[derive(Serialize, Deserialize)]
struct ResponseMsg {
    status: String,
    error: Option<String>,
}

pub fn save_json_pretty<T: Serialize>(value: &T, path: &str) -> std::io::Result<()> {
    let json = serde_json::to_string_pretty(value)?; // pretty
    let mut file = File::create(path)?;
    file.write_all(json.as_bytes())?;
    Ok(())
}

pub fn save_json<T: Serialize>(value: &T, path: &str) -> std::io::Result<()> {
    let json = serde_json::to_string(value)?; // compact
    let mut file = File::create(path)?;
    file.write_all(json.as_bytes())?;
    Ok(())
}
