output "cloud_run_service_url" {
  description = "The public HTTPS URL of the deployed Cloud Run service"
  value       = google_cloud_run_v2_service.clinic_api.uri
}

output "artifact_registry_repository" {
  description = "Artifact Registry Docker repository endpoint"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.clinic_repo.name}"
}

output "deployer_service_account_email" {
  description = "Service account email to configure in GitHub Secrets"
  value       = google_service_account.github_deployer.email
}
