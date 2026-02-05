# 1. Define the Provider
terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
  }
}

# 2. Define a "Resource"
# We are 'documenting' your bot's configuration as code.
resource "local_file" "bot_metadata" {
  filename = "${path.module}/infra_summary.txt"
  content  = <<-EOT
    Platform: AI Architect Bot
    Version: 1.0.0
    Environment: Local Development
    Features: Slack Integration, Gemini AI, Logging
    Owner: Tomoyuki
  EOT
}

variable "project_id" {
  description = "The GCP Project ID"
  type        = string
}

# 1. Define the Google Provider
provider "google" {
  project = var.project_id
  region  = "us-central1"
  credentials = file("gcp-key.json")
}

# 2. Create the Artifact Registry Repository
resource "google_artifact_registry_repository" "my_bot_repo" {
  location      = "us-central1"
  repository_id = "slack-gemini-repo"
  description   = "Docker repository for the AI Slack Bot"
  format        = "DOCKER"

  # Optional: Clean up old images to save space/cost
  cleanup_policy_dry_run = false
}

# 3. Output the Registry URL (we'll need this for Docker later)
output "repository_url" {
  value = "${google_artifact_registry_repository.my_bot_repo.location}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.my_bot_repo.repository_id}"
}