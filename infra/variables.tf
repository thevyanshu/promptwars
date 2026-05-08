variable "project_id" {
  description = "The GCP Project ID"
  type        = string
  default     = "solid-altar-495705-q5"
}

variable "region" {
  description = "The GCP Region"
  type        = string
  default     = "us-central1"
}

variable "db_password" {
  description = "Password for Cloud SQL Postgres"
  type        = string
  sensitive   = true
}

variable "maps_api_key" {
  description = "Google Maps API Key"
  type        = string
  sensitive   = true
}
