terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# -----------------------------------------------------
# Enable Required APIs
# -----------------------------------------------------
resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "redis.googleapis.com",
    "firestore.googleapis.com",
    "aiplatform.googleapis.com",    # Vertex AI
    "secretmanager.googleapis.com"
  ])
  service            = each.key
  disable_on_destroy = false
}

# -----------------------------------------------------
# Cloud SQL (PostgreSQL 16)
# -----------------------------------------------------
resource "google_sql_database_instance" "main" {
  name             = "travel-engine-db"
  database_version = "POSTGRES_16"
  region           = var.region

  settings {
    tier = "db-f1-micro" # Use smallest tier for MVP
    
    # For MVP we allow public IP, in production we would use Private IP
    ip_configuration {
      ipv4_enabled = true
    }
  }

  depends_on = [google_project_service.apis]
}

resource "google_sql_user" "default" {
  name     = "travel_admin"
  instance = google_sql_database_instance.main.name
  password = var.db_password
}

# -----------------------------------------------------
# Memorystore for Redis (Maps Cache)
# -----------------------------------------------------
resource "google_redis_instance" "cache" {
  name           = "travel-engine-cache"
  tier           = "BASIC" # Basic tier for MVP cost savings
  memory_size_gb = 1

  region = var.region

  depends_on = [google_project_service.apis]
}

# -----------------------------------------------------
# Firestore (Real-time updates)
# -----------------------------------------------------
resource "google_firestore_database" "database" {
  project     = var.project_id
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"

  depends_on = [google_project_service.apis]
}

# -----------------------------------------------------
# Cloud Run Backend Service Placeholder
# -----------------------------------------------------
resource "google_cloud_run_v2_service" "backend" {
  name     = "travel-engine-backend"
  location = var.region

  template {
    containers {
      image = "us-docker.pkg.dev/cloudrun/container/hello" # Placeholder until first build
      env {
        name  = "GOOGLE_MAPS_API_KEY"
        value = var.maps_api_key
      }
      # Database connection string would be constructed and passed here
    }
  }

  depends_on = [google_project_service.apis]
}

# Allow public access to backend
resource "google_cloud_run_service_iam_member" "public_access" {
  location = google_cloud_run_v2_service.backend.location
  service  = google_cloud_run_v2_service.backend.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
