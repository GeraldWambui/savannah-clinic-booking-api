variable "project_id" {
  type        = string
  description = "The Google Cloud Project ID"
}

variable "region" {
  type        = string
  description = "The GCP region to deploy resources (e.g. europe-west1 or us-central1)"
  default     = "europe-west1"
}

variable "service_name" {
  type        = string
  description = "The name of the Cloud Run service"
  default     = "clinic-booking-api"
}

variable "artifact_repo_name" {
  type        = string
  description = "The Artifact Registry Docker repository name"
  default     = "clinic-booking-repo"
}

variable "image_tag" {
  type        = string
  description = "The Docker container image tag to deploy"
  default     = "latest"
}
