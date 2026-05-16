use axum::{routing::get, Json, Router};
use serde_json::{json, Value};
use std::{env, net::SocketAddr, time::Instant};

// Стартовий час процесу - використовуємо для розрахунку uptime у /health.
static STARTED_AT: std::sync::OnceLock<Instant> = std::sync::OnceLock::new();

#[tokio::main]
async fn main() {
    STARTED_AT.set(Instant::now()).ok();

    let port: u16 = env::var("PORT")
        .ok()
        .and_then(|s| s.parse().ok())
        .unwrap_or(3000);

    let app = Router::new()
        .route("/", get(root))
        .route("/health", get(health));

    let addr = SocketAddr::from(([0, 0, 0, 0], port));
    let listener = tokio::net::TcpListener::bind(addr)
        .await
        .expect("bind failed");

    println!("Server listening on port {port}");
    axum::serve(listener, app).await.expect("server failed");
}

async fn root() -> Json<Value> {
    Json(json!({
        "message": "Hello from agentic-engineering-course rust-axum starter"
    }))
}

async fn health() -> Json<Value> {
    let uptime = STARTED_AT
        .get()
        .map(|t| t.elapsed().as_secs_f64())
        .unwrap_or(0.0);
    Json(json!({
        "status": "ok",
        "uptime": uptime
    }))
}
