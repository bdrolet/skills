---
name: deploying-email-analysis-job
description: Use when the user wants to deploy, release, or push updates for the analyze-emails Cloud Run job, rebuild the Docker image for email analysis on GCP, or update the email-analysis job after changing python/services or Dockerfile.analyze-emails
---

# Deploying the email-analysis Cloud Run job

Application code and container live under the **`scripts`** repo: **`python/`**. Infrastructure is Terraform in **`python/terraform/`** (Artifact Registry, secrets, job definition). **Image updates** are done with Docker + `gcloud run jobs update`; use Terraform when changing env, resources, or IAM.

## Preconditions

- **gcloud** authenticated; **`gcloud config get-value project`** is the target GCP project (e.g. `bens-project-462804`).
- **Docker** running; **`gcloud auth configure-docker us-central1-docker.pkg.dev`** (adjust region if the registry region differs).
- **`linux/amd64` image** required for Cloud Run (build with `--platform linux/amd64` on Apple Silicon).

Default registry image (matches Terraform):

`us-central1-docker.pkg.dev/PROJECT_ID/email-analysis/analyze-emails:latest`

Job name: **`email-analysis`**, region: **`us-central1`** (override if `python/terraform/project.auto.tfvars` or variables differ).

## Deploy application changes (typical)

Run from the **machine that can push to Artifact Registry** (user laptop or CI).

```bash
cd /path/to/scripts/python

docker build --platform linux/amd64 -f Dockerfile.analyze-emails \
  -t us-central1-docker.pkg.dev/$(gcloud config get-value project)/email-analysis/analyze-emails:latest .

docker push us-central1-docker.pkg.dev/$(gcloud config get-value project)/email-analysis/analyze-emails:latest
```

Copy the **`digest:`** line from the push output (`sha256:...`).

```bash
gcloud run jobs update email-analysis \
  --image=us-central1-docker.pkg.dev/$(gcloud config get-value project)/email-analysis/analyze-emails@sha256:PASTE_DIGEST \
  --region=us-central1 \
  --project="$(gcloud config get-value project)"
```

Pinning **`@sha256:`** avoids Cloud Run reusing a cached **`latest`** layer. If you only set **`...:latest`** in Terraform, a later **`terraform apply`** can align state; until then, **`gcloud run jobs update`** is authoritative for the running digest.

## Optional: run the job once

```bash
gcloud run jobs execute email-analysis --region=us-central1 --wait
```

Long runs (hundreds of emails) can exceed default tool timeouts; run **`execute`** in the background and poll **`gcloud run jobs executions list`** or Cloud Logging.

## When to use Terraform instead

- New secrets, env vars, CPU/memory, schedule, or **first-time** provisioning: **`cd python/terraform`** then **`terraform plan -var-file=terraform.tfvars`** / **`apply`**. Do **not** commit **`terraform.tfvars`** (sensitive).
- **`project.auto.tfvars`** may set **`project_id`** only; secrets stay in **`terraform.tfvars`**.

## Repo touchpoints

| Piece | Path |
|-------|------|
| Container definition | `python/Dockerfile.analyze-emails` |
| Entrypoint | `python/scripts/analyze_emails.py` |
| **`PYTHONPATH`** | Set in Dockerfile (`/app`) |
| Move-to-folder behavior | `EMAIL_ANALYSIS_MOVE_TO_ACTION_FOLDERS` (default on); Graph needs **Mail.ReadWrite** on the MSAL token |
| IaC | `python/terraform/*.tf` |

## MSAL / Graph scope changes

If delegated permissions change (e.g. added **Mail.ReadWrite**), refresh the **`msal-token-cache`** secret: run **`python/scripts/seed_token_cache.py`** locally with an **`.env`** that includes the new **`SCOPES`**, then update the secret version (or **`terraform apply`** with updated **`msal_token_cache`** in tfvars).
