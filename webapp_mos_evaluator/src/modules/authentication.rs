use crate::Login;
use actix_identity::Identity;
use actix_web::middleware::Next;
use actix_web::{Error, FromRequest};
use actix_web::{HttpMessage, HttpRequest, Responder, web};
use actix_web::{
    HttpResponse,
    body::BoxBody,
    dev::{ServiceRequest, ServiceResponse},
    error::ErrorUnauthorized,
};
use argon2::{Argon2, PasswordHash, PasswordVerifier};
use log::error;

pub fn verify_admin(email: &str, password: &str) -> bool {
    let allowed_email = std::env::var("ADMIN_EMAIL").unwrap_or_else(|_| "admin".into());
    if email != allowed_email {
        return false;
    }
    let phc = match std::env::var("ADMIN_PWHASH") {
        Ok(v) => v,
        Err(_) => return false,
    };
    let parsed = match PasswordHash::new(&phc) {
        Ok(p) => p,
        Err(_) => return false,
    };
    Argon2::default()
        .verify_password(password.as_bytes(), &parsed)
        .is_ok()
}

// API HANDLER: LOGIN
pub async fn login(req: HttpRequest, form: web::Json<Login>) -> impl Responder {
    if verify_admin(&form.email, &form.password) {
        // was: id.remember("admin".to_string());
        let _ = Identity::login(&req.extensions(), "admin".to_string());

        HttpResponse::Ok().finish()
    } else {
        // redirect to login page instead
        HttpResponse::Unauthorized().finish()
    }
}

// API HANDLER: ME
// If you want 401 automatically when unauthenticated, use Identity extractor.
// If you want to allow unauth and handle manually, use Option<Identity>.
pub async fn me(user: Option<Identity>) -> impl Responder {
    if let Some(user) = user {
        let uid = user.id().unwrap_or_default();
        HttpResponse::Ok().json(serde_json::json!({ "user": uid }))
    } else {
        HttpResponse::Unauthorized().finish()
    }
}

// API HANDLER: LOGOUT
pub async fn logout(user: Identity) -> impl Responder {
    // was: user.forget();
    user.logout();
    // invalidate the session cookie as well

    HttpResponse::Ok().finish()
}

pub fn require_auth(id: &Identity) -> Result<String, Error> {
    id.id().map_err(|_| ErrorUnauthorized("login required"))
}

// API HANDLER: REQUIRE LOGIN MIDDLEWARE FOR STATIC FILES
pub async fn require_login(
    req: ServiceRequest,
    next: Next<BoxBody>,
) -> Result<ServiceResponse<BoxBody>, Error> {
    let (httpreq, mut pl) = req.into_parts();
    let identity = Identity::from_request(&httpreq, &mut pl).await;

    match identity {
        Err(error) => {
            error!("Error extracting identity: {:?}", error);
            let res = HttpResponse::TemporaryRedirect()
                .insert_header(("Location", "/login.html"))
                .finish()
                .map_into_boxed_body();
            Ok(ServiceResponse::new(httpreq, res))
        }
        Ok(id) => {
            if id.id().is_err() {
                let res = HttpResponse::TemporaryRedirect()
                    .insert_header(("Location", "/login.html"))
                    .finish()
                    .map_into_boxed_body();
                Ok(ServiceResponse::new(httpreq, res))
            } else {
                // reconstruct the ServiceRequest from parts and call the next service
                let srv_req = ServiceRequest::from_parts(httpreq, pl);
                next.call(srv_req).await
            }
        }
    }
}
