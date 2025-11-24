use actix_files::Files;
use actix_identity::IdentityMiddleware;
use actix_session::storage::RedisSessionStore;
use actix_session::{SessionMiddleware, config::PersistentSession};
use actix_web::middleware::from_fn;
use actix_web::{cookie, middleware};
use base64::Engine;
use cookie::{Key, SameSite};
use log::info;

use actix_web::{App, HttpServer, cookie::time::Duration, middleware::Logger, web};
use serde::Deserialize;
use std::{env, fs, io};

use crate::modules::authentication::{login, logout, me, require_login};
use crate::modules::mos::savemos;
use crate::modules::ref_synth::savecompare;
pub mod modules;

fn env(name: &str) -> String {
    std::env::var(name).expect(name)
}

#[derive(Deserialize)]
pub struct Login {
    email: String,
    password: String,
}

#[actix_rt::main]
async fn main() -> io::Result<()> {
    env_logger::init();

    if let Ok(build_date) = fs::read_to_string("/build_date.txt") {
        println!("Image built at: {}", build_date.trim());
    }

    let ip_binding = env::var("IP_PORT_BINDING").unwrap_or_else(|_| "0.0.0.0:6969".to_string());
    let redis_endpoint = env::var("REDIS_ENDPOINT").expect("REDIS_ENDPOINT must be set");
    let is_https = env::var("HTTPS").unwrap_or_else(|_| "false".to_string()) == "true";
    let session_key = {
        let b64 = env("SESSION_KEY");
        let bytes = base64::engine::general_purpose::STANDARD
            .decode(&b64)
            .expect("valid base64 SESSION_KEY");
        Key::from(&bytes)
    };
    let redis_store = RedisSessionStore::new(redis_endpoint).await.unwrap();
    info!("Starting server on {}", ip_binding);

    HttpServer::new(move || {
        App::new()
            .wrap(Logger::default())
            .wrap(middleware::Logger::default())
            .wrap(IdentityMiddleware::default())
            .wrap(
                SessionMiddleware::builder(redis_store.clone(), session_key.clone())
                    .cookie_name("sid".into())
                    .cookie_http_only(true)
                    .cookie_secure(is_https) // set true in prod (HTTPS)
                    .cookie_same_site(SameSite::Lax) // None if SPA on different origin; use Lax if same-site
                    .session_lifecycle(PersistentSession::default().session_ttl(Duration::days(1)))
                    .build(),
            )
            .route("/login", web::post().to(login))
            .route("/me", web::get().to(me))
            .route("/logout", web::post().to(logout))
            .route("/savemos", web::post().to(savemos))
            .route("/savecompare", web::post().to(savecompare))
            .service(
                web::scope("/dashboard")
                    .wrap(from_fn(require_login))
                    .service(Files::new("", "./static/dashboard/").index_file("index.html")),
            )
            .service(Files::new("/", "./static/login/").index_file("login.html"))
    })
    .bind(ip_binding)?
    .run()
    .await
}
