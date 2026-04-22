---
name: setting-up-email-analysis
description: Use when the user wants to set up, bootstrap, or configure the email analysis project for the first time on a new machine, initialize local Python dependencies and .env, seed MSAL token cache for Graph, or prepare Terraform/GCP secrets before running analyze_emails or the Cloud Run job
metadata:
  depends-on: "deploying-email-analysis-job, analyzing-emails"
---

# Setting up email analysis (initial)

Target repo path: **`scripts`** → **`python/`**. Never commit **`.env`**, **`.token_cache.json`**, **`terraform.tfvars`**, or OAuth client JSON files.

## 1. Clone and Python

- Python **3.11+** recommended (matches `Dockerfile.analyze-emails`).
- From repo root: `cd python && pip install -r requirements.txt` (or use a venv first).

## 2. Azure app registration (prerequisite)

In Entra ID, register a **public client** app (or your existing app) and note:

- **Application (client) ID** → `CLIENT_ID`
- **Directory (tenant) ID** → `TENANT_ID`
- For confidential flows you may have a secret → `CLIENT_SECRET` (local `.env` / Terraform variable; not committed)

**API permissions (delegated):** at minimum **`Mail.Read`** to fetch mail; add **`Mail.ReadWrite`** if you use **move-to-folder** after analysis. **`User.Read`** is typical. Grant admin consent if required.

**Redirect URI:** for local interactive flows, match what MSAL expects (e.g. `http://localhost:8080/callback` if configured in Azure).

## 3. Local `.env` in `python/`

Create **`python/.env`** (gitignored). Example shape:

```bash
CLIENT_ID=<azure-app-id>
CLIENT_SECRET=<azure-secret-if-used>
TENANT_ID=<tenant-id>
OPENAI_API_KEY=<key>
REDIRECT_URI=http://localhost:8080/callback
SCOPES=https://graph.microsoft.com/Mail.ReadWrite https://graph.microsoft.com/User.Read
```

Adjust **`SCOPES`** to match Azure grants and whether you need writes (folder moves). **`python-dotenv`** loads this for `analyze_emails.py` and **`scripts/seed_token_cache.py`**.

## 4. First local run (device code)

Always from **`python/`**, unbuffered:

```bash
cd python && python3 -u scripts/analyze_emails.py
```

Without **`GCP_PROJECT_ID`**, the script runs **interactive** mode: complete **device code** sign-in in the browser. It will create/update **`.token_cache.json`** in `python/` for subsequent silent refresh.

## 5. Optional: copy token cache from another machine

You may copy **`.token_cache.json`** from a trusted machine instead of signing in again. Same **Azure app** and **user account**; treat the file as a **credential**.

## 6. Seeding MSAL for Cloud Run / Terraform

For **headless** runs, the job reads MSAL JSON from **GCP Secret Manager** (`msal-token-cache`). Generate on a machine where you can sign in:

```bash
cd python
# .env must have CLIENT_ID, TENANT_ID, SCOPES
python3 scripts/seed_token_cache.py > /tmp/msal_cache.json
# Then add version to secret or paste into terraform.tfvars msal_token_cache (never commit tfvars)
```

Re-seed after **scope changes** (e.g. adding Mail.ReadWrite).

## 7. OpenAI

Set **`OPENAI_API_KEY`** in `.env` locally; for Cloud Run use Terraform **`openai_api_key`** → Secret Manager (see **`python/terraform/terraform.tfvars.example`**).

## 8. GCP / Terraform (optional second phase)

- **`gcloud auth login`** and **`gcloud auth application-default login`**
- **`gcloud config set project <id>`**
- Copy **`python/terraform/terraform.tfvars.example`** → **`terraform.tfvars`** (gitignored); fill Azure/OpenAI/**`msal_token_cache`**
- **`project.auto.tfvars`** may set **`project_id`** only (safe to commit if you accept a fixed default project)
- Run **`terraform init`** / **`plan`** / **`apply`** from **`python/terraform/`**

Docker + Artifact Registry + **`gcloud run jobs update`** are covered by the **`deploying-email-analysis-job`** skill.

## Quick verification

- **Local:** `python3 -u scripts/analyze_emails.py` completes without auth errors and prints analysis output.
- **GCP:** after deploy, one execution succeeds in Cloud Logging (check Graph/move errors if permissions are wrong).

## Related

- **Deploy image / update job:** skill **`deploying-email-analysis-job`**
- **Local triage behavior:** skill **`analyzing-emails`** (update paths/models if the repo drifted)
