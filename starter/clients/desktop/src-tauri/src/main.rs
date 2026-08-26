#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri_plugin_updater::UpdaterExt;

#[tauri::command]
async fn install_verified_update(app: tauri::AppHandle) -> Result<String, String> {
    let pubkey = option_env!("MIRA_TAURI_UPDATER_PUBLIC_KEY").unwrap_or("").trim();
    let endpoint = option_env!("MIRA_TAURI_UPDATER_ENDPOINT").unwrap_or("").trim();
    if pubkey.is_empty() || endpoint.is_empty() {
        return Err("This build is not attached to a signed MIRA update channel.".to_string());
    }
    if !endpoint.starts_with("https://") {
        return Err("MIRA production updater endpoints must use HTTPS.".to_string());
    }
    let endpoint_url: url::Url = endpoint
        .parse()
        .map_err(|error| format!("invalid updater endpoint: {error}"))?;
    let updater = app
        .updater_builder()
        .pubkey(pubkey)
        .endpoints(vec![endpoint_url])
        .map_err(|error| error.to_string())?
        .build()
        .map_err(|error| error.to_string())?;
    let Some(update) = updater.check().await.map_err(|error| error.to_string())? else {
        return Ok("current".to_string());
    };
    let version = update.version.clone();
    update
        .download_and_install(|_, _| {}, || {})
        .await
        .map_err(|error| error.to_string())?;
    app.restart();
}

#[tauri::command]
fn updater_channel_status() -> serde_json::Value {
    let endpoint = option_env!("MIRA_TAURI_UPDATER_ENDPOINT").unwrap_or("").trim();
    let pubkey = option_env!("MIRA_TAURI_UPDATER_PUBLIC_KEY").unwrap_or("").trim();
    serde_json::json!({
        "configured": !endpoint.is_empty() && !pubkey.is_empty(),
        "https": endpoint.starts_with("https://"),
        "endpoint": if endpoint.is_empty() { serde_json::Value::Null } else { serde_json::Value::String(endpoint.to_string()) },
        "signature_verification_required": true
    })
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_updater::Builder::new().build())
        .invoke_handler(tauri::generate_handler![install_verified_update, updater_channel_status])
        .run(tauri::generate_context!())
        .expect("error while running MIRA desktop application");
}
