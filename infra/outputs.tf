output "backend_url" {
  description = "The URL of the Cloud Run backend service"
  value       = google_cloud_run_v2_service.backend.uri
}

output "cloud_sql_connection_name" {
  description = "The connection name for Cloud SQL"
  value       = google_sql_database_instance.main.connection_name
}

output "cloud_sql_ip" {
  description = "The public IP address of the Cloud SQL instance"
  value       = google_sql_database_instance.main.public_ip_address
}

output "redis_host" {
  description = "The host IP of the Memorystore Redis instance"
  value       = google_redis_instance.cache.host
}

output "redis_port" {
  description = "The port of the Memorystore Redis instance"
  value       = google_redis_instance.cache.port
}
