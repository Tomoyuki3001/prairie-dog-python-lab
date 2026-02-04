# AI-Powered Platform Agent (Gemini & Slack)

A production-ready automation platform that integrates **Google Gemini AI** into **Slack**, built with a heavy emphasis on **Platform Engineering** principles, **Infrastructure as Code (IaC)**, and **Security**.

## Tech Stack & Engineering Standards

- **Language:** Python 3.11+ (Modular and Type-hinted)
- **IaC:** Terraform (for repository structure and environment standardization)
- **CI/CD:** GitHub Actions (Automated linting and dependency validation)
- **Security:** Secret Management via `python-dotenv` and `.gitignore` shields
- **Frameworks:** Slack Bolt SDK, Google GenAI SDK

## Operational Excellence & Security

This project follows professional **SRE and Platform Engineering** best practices:

- **Secret Management:** Sensitive API tokens are handled via environment variables. Zero-leakage is enforced through strict `.gitignore` rules.
- **Dependency Management:** Versions are locked in `requirements.txt` to ensure reproducible builds across all environments.
- **Branching Strategy:** Followed a Feature-Branch workflow (`main` branch protection) to ensure code quality.

## CI/CD Pipeline

The included GitHub Actions workflow automatically:

1. Validates Python syntax and dependencies.
2. Ensures the repository adheres to the standardized structure defined by the Terraform configuration.
3. Prevents "broken" code from being merged into the production branch.

## Getting Started

1. **Clone the repo:** `git clone <your-repo-url>`
2. **Setup Environment:** Create a `.env` file with `SLACK_BOT_TOKEN`, `SLACK_SIGNING_SECRET`, and `GEMINI_API_KEY`.
3. **Install Dependencies:** `pip install -r requirements.txt`
4. **Run App:** `python slack_app.py`
