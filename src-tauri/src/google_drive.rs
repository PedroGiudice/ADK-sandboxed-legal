use serde::{Deserialize, Serialize};
use std::collections::HashMap;

const GOOGLE_AUTH_URL: &str = "https://accounts.google.com/o/oauth2/v2/auth";
const GOOGLE_TOKEN_URL: &str = "https://oauth2.googleapis.com/token";
const GOOGLE_DRIVE_API: &str = "https://www.googleapis.com/drive/v3";

// Scopes for Google Drive access
const DRIVE_SCOPES: &str = "https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/drive.readonly";

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct DriveFile {
    pub id: String,
    pub name: String,
    #[serde(rename = "mimeType")]
    pub mime_type: String,
    #[serde(rename = "modifiedTime")]
    pub modified_time: Option<String>,
    pub size: Option<String>,
    pub parents: Option<Vec<String>>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DriveFilesResponse {
    pub files: Vec<DriveFile>,
    #[serde(rename = "nextPageToken")]
    pub next_page_token: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
struct TokenResponse {
    access_token: String,
    refresh_token: Option<String>,
    expires_in: u64,
    token_type: String,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct GoogleDriveCredentials {
    pub client_id: String,
    pub client_secret: String,
    pub access_token: Option<String>,
    pub refresh_token: Option<String>,
    pub expires_at: Option<u64>,
}

/// Generates the OAuth URL for Google Drive authorization
#[tauri::command]
pub async fn google_drive_auth(
    client_id: String,
    redirect_uri: String,
) -> Result<String, String> {
    let params = [
        ("client_id", client_id.as_str()),
        ("redirect_uri", redirect_uri.as_str()),
        ("response_type", "code"),
        ("scope", DRIVE_SCOPES),
        ("access_type", "offline"),
        ("prompt", "consent"),
    ];

    let query = params
        .iter()
        .map(|(k, v)| format!("{}={}", k, urlencoding::encode(v)))
        .collect::<Vec<_>>()
        .join("&");

    Ok(format!("{}?{}", GOOGLE_AUTH_URL, query))
}

/// Exchanges the authorization code for tokens
#[tauri::command]
pub async fn google_drive_callback(
    code: String,
    client_id: String,
    client_secret: String,
    redirect_uri: String,
) -> Result<GoogleDriveCredentials, String> {
    let client = reqwest::Client::new();

    let mut params = HashMap::new();
    params.insert("code", code.as_str());
    params.insert("client_id", client_id.as_str());
    params.insert("client_secret", client_secret.as_str());
    params.insert("redirect_uri", redirect_uri.as_str());
    params.insert("grant_type", "authorization_code");

    let response = client
        .post(GOOGLE_TOKEN_URL)
        .form(&params)
        .send()
        .await
        .map_err(|e| format!("Failed to exchange code: {}", e))?;

    if !response.status().is_success() {
        let error_text = response.text().await.unwrap_or_default();
        return Err(format!("Token exchange failed: {}", error_text));
    }

    let token_response: TokenResponse = response
        .json()
        .await
        .map_err(|e| format!("Failed to parse token response: {}", e))?;

    let expires_at = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_secs()
        + token_response.expires_in;

    Ok(GoogleDriveCredentials {
        client_id,
        client_secret,
        access_token: Some(token_response.access_token),
        refresh_token: token_response.refresh_token,
        expires_at: Some(expires_at),
    })
}

/// Lists files from Google Drive
#[tauri::command]
pub async fn google_drive_list_files(
    access_token: String,
    folder_id: Option<String>,
    page_token: Option<String>,
) -> Result<DriveFilesResponse, String> {
    let client = reqwest::Client::new();

    let mut query_parts = vec![
        "trashed=false".to_string(),
    ];

    if let Some(fid) = folder_id {
        query_parts.push(format!("'{}' in parents", fid));
    }

    let query = query_parts.join(" and ");

    let mut url = format!(
        "{}/files?q={}&fields=files(id,name,mimeType,modifiedTime,size,parents),nextPageToken&pageSize=100",
        GOOGLE_DRIVE_API,
        urlencoding::encode(&query)
    );

    if let Some(pt) = page_token {
        url.push_str(&format!("&pageToken={}", pt));
    }

    let response = client
        .get(&url)
        .header("Authorization", format!("Bearer {}", access_token))
        .send()
        .await
        .map_err(|e| format!("Failed to list files: {}", e))?;

    if !response.status().is_success() {
        let error_text = response.text().await.unwrap_or_default();
        return Err(format!("Failed to list files: {}", error_text));
    }

    response
        .json::<DriveFilesResponse>()
        .await
        .map_err(|e| format!("Failed to parse files response: {}", e))
}

/// Downloads a file from Google Drive
#[tauri::command]
pub async fn google_drive_download(
    access_token: String,
    file_id: String,
    file_name: String,
    download_path: String,
) -> Result<String, String> {
    let client = reqwest::Client::new();

    // First, get file metadata to check if it's a Google Docs file
    let metadata_url = format!("{}/files/{}?fields=mimeType", GOOGLE_DRIVE_API, file_id);

    let metadata_response = client
        .get(&metadata_url)
        .header("Authorization", format!("Bearer {}", access_token))
        .send()
        .await
        .map_err(|e| format!("Failed to get file metadata: {}", e))?;

    if !metadata_response.status().is_success() {
        let error_text = metadata_response.text().await.unwrap_or_default();
        return Err(format!("Failed to get metadata: {}", error_text));
    }

    let metadata: serde_json::Value = metadata_response
        .json()
        .await
        .map_err(|e| format!("Failed to parse metadata: {}", e))?;

    let mime_type = metadata["mimeType"].as_str().unwrap_or("");

    // Determine download URL based on mime type
    let (download_url, final_extension) = if mime_type.starts_with("application/vnd.google-apps") {
        // Google Docs format - need to export
        let (export_mime, ext) = match mime_type {
            "application/vnd.google-apps.document" => ("application/pdf", ".pdf"),
            "application/vnd.google-apps.spreadsheet" => ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".xlsx"),
            "application/vnd.google-apps.presentation" => ("application/pdf", ".pdf"),
            _ => ("application/pdf", ".pdf"),
        };
        (
            format!("{}/files/{}/export?mimeType={}", GOOGLE_DRIVE_API, file_id, urlencoding::encode(export_mime)),
            ext
        )
    } else {
        // Regular file - direct download
        (
            format!("{}/files/{}?alt=media", GOOGLE_DRIVE_API, file_id),
            ""
        )
    };

    let response = client
        .get(&download_url)
        .header("Authorization", format!("Bearer {}", access_token))
        .send()
        .await
        .map_err(|e| format!("Failed to download file: {}", e))?;

    if !response.status().is_success() {
        let error_text = response.text().await.unwrap_or_default();
        return Err(format!("Failed to download: {}", error_text));
    }

    let bytes = response
        .bytes()
        .await
        .map_err(|e| format!("Failed to read file bytes: {}", e))?;

    // Construct final path
    let final_name = if final_extension.is_empty() {
        file_name
    } else {
        format!("{}{}", file_name.trim_end_matches(final_extension), final_extension)
    };

    let final_path = std::path::Path::new(&download_path).join(&final_name);

    std::fs::write(&final_path, bytes)
        .map_err(|e| format!("Failed to write file: {}", e))?;

    Ok(final_path.to_string_lossy().to_string())
}

/// Uploads a file to Google Drive
#[tauri::command]
pub async fn google_drive_upload(
    access_token: String,
    local_path: String,
    folder_id: Option<String>,
    file_name: Option<String>,
) -> Result<DriveFile, String> {
    let client = reqwest::Client::new();

    let path = std::path::Path::new(&local_path);
    let name = file_name.unwrap_or_else(|| {
        path.file_name()
            .map(|n| n.to_string_lossy().to_string())
            .unwrap_or_else(|| "untitled".to_string())
    });

    let content = std::fs::read(&local_path)
        .map_err(|e| format!("Failed to read local file: {}", e))?;

    // Detect mime type from extension
    let mime_type = match path.extension().and_then(|e| e.to_str()) {
        Some("pdf") => "application/pdf",
        Some("doc") | Some("docx") => "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        Some("txt") => "text/plain",
        Some("json") => "application/json",
        Some("md") => "text/markdown",
        _ => "application/octet-stream",
    };

    // Create metadata
    let mut metadata = serde_json::json!({
        "name": name
    });

    if let Some(fid) = folder_id {
        metadata["parents"] = serde_json::json!([fid]);
    }

    // Use multipart upload
    let boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW";
    let mut body = Vec::new();

    // Metadata part
    body.extend_from_slice(format!("--{}\r\n", boundary).as_bytes());
    body.extend_from_slice(b"Content-Type: application/json; charset=UTF-8\r\n\r\n");
    body.extend_from_slice(metadata.to_string().as_bytes());
    body.extend_from_slice(b"\r\n");

    // File content part
    body.extend_from_slice(format!("--{}\r\n", boundary).as_bytes());
    body.extend_from_slice(format!("Content-Type: {}\r\n\r\n", mime_type).as_bytes());
    body.extend_from_slice(&content);
    body.extend_from_slice(b"\r\n");

    // End boundary
    body.extend_from_slice(format!("--{}--\r\n", boundary).as_bytes());

    let response = client
        .post("https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,name,mimeType,modifiedTime,size,parents")
        .header("Authorization", format!("Bearer {}", access_token))
        .header("Content-Type", format!("multipart/related; boundary={}", boundary))
        .body(body)
        .send()
        .await
        .map_err(|e| format!("Failed to upload file: {}", e))?;

    if !response.status().is_success() {
        let error_text = response.text().await.unwrap_or_default();
        return Err(format!("Failed to upload: {}", error_text));
    }

    response
        .json::<DriveFile>()
        .await
        .map_err(|e| format!("Failed to parse upload response: {}", e))
}

/// Disconnects Google Drive (clears stored credentials)
#[tauri::command]
pub async fn google_drive_disconnect() -> Result<(), String> {
    // The actual credential clearing happens on the frontend side via tauri-plugin-store
    // This command can be used to revoke the token if needed
    Ok(())
}

// URL encoding helper
mod urlencoding {
    pub fn encode(input: &str) -> String {
        let mut encoded = String::new();
        for byte in input.bytes() {
            match byte {
                b'A'..=b'Z' | b'a'..=b'z' | b'0'..=b'9' | b'-' | b'_' | b'.' | b'~' => {
                    encoded.push(byte as char);
                }
                _ => {
                    encoded.push_str(&format!("%{:02X}", byte));
                }
            }
        }
        encoded
    }
}
