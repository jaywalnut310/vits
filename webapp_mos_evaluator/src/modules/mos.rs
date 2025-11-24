use actix_identity::Identity;
use actix_web::{
    Error, HttpResponse,
    http::StatusCode,
    web::{self},
};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

use crate::modules::{ResponseMsg, authentication::require_auth, save_json_pretty};

#[derive(Debug, Serialize, Deserialize)]
pub struct MosPayload {
    #[serde(rename = "sessionId")]
    pub session_id: String,

    #[serde(rename = "createdAt")]
    pub created_at: String, // or DateTime<Utc> with a custom serde format

    /// e.g. ["overall", "naturalness", "intelligibility", ...]
    pub attributes: Vec<String>,

    pub responses: Vec<MosResponse>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct MosResponse {
    #[serde(rename = "sessionId")]
    pub session_id: String,

    #[serde(rename = "sampleId")]
    pub sample_id: String,

    /// Map attribute_id -> score (1–5)
    pub scores: HashMap<String, i32>,

    #[serde(rename = "playCount")]
    pub play_count: u32,

    /// Shuffled index again (same as sample.order at rating time)
    pub order: u32,

    /// ISO8601 timestamp string
    #[serde(rename = "ts")]
    pub timestamp: String,
}

pub async fn savemos(id: Identity, payload: web::Json<MosPayload>) -> Result<HttpResponse, Error> {
    let _user_id = require_auth(&id)?; // 401 if not logged in

    match save_json_pretty(
        &payload,
        format!("results/mos/{}.json", payload.session_id).as_str(),
    ) {
        Ok(_) => Ok(HttpResponse::Ok()
            .content_type("application/json")
            .status(StatusCode::ACCEPTED)
            .json(ResponseMsg {
                status: "ok".to_string(),
                error: None,
            })),
        Err(e) => Ok(HttpResponse::InternalServerError()
            .content_type("application/json")
            .json(ResponseMsg {
                status: "error".to_string(),
                error: Some(format!("Failed to save JSON: {}", e)),
            })),
    }
}
