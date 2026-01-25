mod google_drive;

use google_drive::{
    google_drive_auth, google_drive_callback, google_drive_list_files,
    google_drive_download, google_drive_upload, google_drive_disconnect
};

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_updater::Builder::new().build())
        .plugin(tauri_plugin_process::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_store::Builder::default().build())
        .plugin(tauri_plugin_mcp::Builder.build())
        .invoke_handler(tauri::generate_handler![
            google_drive_auth,
            google_drive_callback,
            google_drive_list_files,
            google_drive_download,
            google_drive_upload,
            google_drive_disconnect
        ])
        .setup(|app| {
            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
