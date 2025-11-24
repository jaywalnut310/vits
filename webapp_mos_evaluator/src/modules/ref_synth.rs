use actix_identity::Identity;
use actix_web::{
    Error, HttpResponse,
    http::StatusCode,
    web::{self},
};
use serde::{Deserialize, Serialize};

use crate::modules::{ResponseMsg, authentication::require_auth, save_json_pretty};

#[derive(Debug, Serialize, Deserialize)]
pub struct RefSynthPayload {
    #[serde(rename = "sessionId")]
    pub session_id: String,

    #[serde(rename = "createdAt")]
    pub created_at: String,

    /// All pairs the frontend had configured (with blind mappings)
    pub pairs: Vec<RefPair>,

    /// User responses for this session
    pub responses: Vec<RefResponse>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct RefPair {
    pub id: String,
    pub text: String,
    pub mapping: RefMapping,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum SampleType {
    Ref,
    Synth,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct RefMapping {
    #[serde(rename = "sample1Type")]
    pub sample1_type: SampleType,

    #[serde(rename = "sample1Path")]
    pub sample1_path: String,

    #[serde(rename = "sample2Type")]
    pub sample2_type: SampleType,

    #[serde(rename = "sample2Path")]
    pub sample2_path: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct RefResponse {
    #[serde(rename = "sessionId")]
    pub session_id: String,

    #[serde(rename = "pairId")]
    pub pair_id: String,

    /// Mapping for this pair at the time of rating
    pub mapping: RefMapping,

    /// Which one they think is synthetic: 1, 2, or 0 (not sure)
    pub guess: i32,

    /// Similarity rating: 1–5
    pub similarity: i32,

    /// Which sounds more natural: 1,2,0 (optional, may be null)
    pub naturalness: Option<i32>,

    #[serde(rename = "playCount1")]
    pub play_count1: u32,

    #[serde(rename = "playCount2")]
    pub play_count2: u32,

    #[serde(rename = "ts")]
    pub timestamp: String,
}

pub async fn savecompare(
    id: Identity,
    payload: web::Json<RefSynthPayload>,
) -> Result<HttpResponse, Error> {
    let _user_id = require_auth(&id)?; // 401 if not logged in

    match save_json_pretty(
        &payload,
        format!("results/ab/{}.json", payload.session_id).as_str(),
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
