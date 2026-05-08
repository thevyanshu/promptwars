# Secret Manager for sensitive values
resource "google_secret_manager_secret" "db_password" {
  secret_id = "travel-engine-db-password"
  
  replication {
    auto {}
  }

  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret_version" "db_password_value" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = var.db_password
}

resource "google_secret_manager_secret" "maps_api_key" {
  secret_id = "travel-engine-maps-key"
  
  replication {
    auto {}
  }

  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret_version" "maps_api_key_value" {
  secret      = google_secret_manager_secret.maps_api_key.id
  secret_data = var.maps_api_key
}
