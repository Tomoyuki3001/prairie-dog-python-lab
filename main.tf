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