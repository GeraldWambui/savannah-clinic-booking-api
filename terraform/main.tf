terraform {
  required_version = ">= 1.5.0"
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

# 1. Enable Required GCP APIs
resource "google_project_service" "enabled_apis" {
  for_each = toset([
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "iam.googleapis.com"
  ])

  service            = each.key
  disable_on_destroy = false
}

# 2. Artifact Registry for Container Storage
resource "google_artifact_registry_repository" "clinic_repo" {
  depends_on    = [google_project_service.enabled_apis]
  location      = var.region
  repository_id = var.artifact_repo_name
  description   = "Docker container repository for Clinic Booking API"
  format        = "DOCKER"
}

# 3. Cloud Run Service (Serverless Container Platform)
resource "google_cloud_run_v2_service" "clinic_api" {
  name       = var.service_name
  location   = var.region
  ingress    = "INGRESS_TRAFFIC_ALL"
  depends_on = [google_artifact_registry_repository.clinic_repo]

  template {
    scaling {
      min_instance_count = 0
      max_instance_count = 3
    }

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.clinic_repo.name}/${var.service_name}:${var.image_tag}"

      ports {
        container_port = 8000
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }

      env {
        name  = "ENVIRONMENT"
        value = "production"
      }

      env {
        name  = "PORT"
        value = "8000"
      }

      startup_probe {
        http_get {
          path = "/health"
          port = 8000
        }
        initial_delay_seconds = 5
        period_seconds        = 10
        failure_threshold     = 3
      }

      liveness_probe {
        http_get {
          path = "/health"
          port = 8000
        }
        period_seconds    = 15
        failure_threshold = 3
      }
    }
  }
}

# 4. Public Access (allow unauthenticated callers to view API and Swagger docs)
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  project  = google_cloud_run_v2_service.clinic_api.project
  location = google_cloud_run_v2_service.clinic_api.location
  name     = google_cloud_run_v2_service.clinic_api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# 5. Service Account for Automated GitHub Actions CI/CD Deployment
resource "google_service_account" "github_deployer" {
  account_id   = "github-actions-deployer"
  display_name = "GitHub Actions CI/CD Deployer"
  description  = "Service account used by GitHub Actions pipeline to push containers and deploy to Cloud Run"
}

# Grant necessary least-privilege roles to CI/CD Service Account
resource "google_project_iam_member" "deployer_roles" {
  for_each = toset([
    "roles/run.admin",
    "roles/artifactregistry.writer",
    "roles/iam.serviceAccountUser"
  ])

  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.github_deployer.email}"
}
