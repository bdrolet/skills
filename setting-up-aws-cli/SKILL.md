---
name: setting-up-aws-cli
description: >
  Use when the user has AWS CLI authentication issues, cannot assume a role,
  gets AccessDenied on sts:AssumeRole, AWS_PROFILE doesn't work, or needs
  help configuring ~/.aws/config or ~/.aws/credentials.
---

# Setting Up AWS CLI

## Organization Structure

All access flows through the **IAM hub account** (`homeward-iam` / `612782862337`).

| Profile | Account | Role | Region |
|---|---|---|---|
| `iam` | `612782862337` (homeward-iam) | Direct IAM user | us-east-1 |
| `eng-dev` | `682983209039` | `HwhDeveloper` | us-east-1 |
| `eng-staging` | `962254627709` | `HwhDeveloper` | us-east-2 |
| `eng-prod` | `427286316823` | — | us-east-2 |

Console sign-in: `https://iam-hwh.signin.aws.amazon.com/console`

## Expected Config

**`~/.aws/config`**:
```ini
[profile iam]
region = us-east-1
output = json

[profile eng-dev]
role_arn = arn:aws:iam::682983209039:role/HwhDeveloper
source_profile = iam
region = us-east-1
output = json

[profile eng-staging]
role_arn = arn:aws:iam::962254627709:role/HwhDeveloper
source_profile = iam
region = us-east-2
output = json
```

**`~/.aws/credentials`**: Access keys created from the `homeward-iam` console under `[iam]`.

## Debugging Checklist

1. **Check for env var override** — the most common issue:
   ```bash
   env | grep -i AWS_
   ```
   `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` in the environment **override all profiles**. Check `.zshrc`, `.zprofile`, `.secrets`, and similar startup files. Remove or comment them out.

2. **Verify the `[iam]` key is in the right account**:
   ```bash
   AWS_ACCESS_KEY_ID=<key> AWS_SECRET_ACCESS_KEY=<secret> aws sts get-caller-identity
   ```
   Must return account `612782862337`. If it returns a different account, the keys were created in the wrong AWS console.

3. **Test role assumption with a clean env**:
   ```bash
   env -u AWS_ACCESS_KEY_ID -u AWS_SECRET_ACCESS_KEY -u AWS_SESSION_TOKEN \
     AWS_PROFILE=eng-staging aws sts get-caller-identity
   ```
   Should return `962254627709` with an `assumed-role/HwhDeveloper` ARN.

4. **If AccessDenied persists** with clean env and correct keys:
   - The `HwhDeveloper` trust policy in the target account may require MFA
   - Check if the user has an MFA device: `aws iam list-mfa-devices --profile iam`
   - If MFA is required, add `mfa_serial` to the profile in `~/.aws/config`

## Reference

[AWS Access Howto](https://homewardhealth.atlassian.net/wiki/spaces/SD/pages/421232653/AWS+Access+Howto) — Confluence page with full setup instructions.
