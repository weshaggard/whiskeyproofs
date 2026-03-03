# Automated PR Setup

**✅ Your setup is complete!** This repository uses a GitHub App for automated pull request creation with zero-maintenance workflow automation.

The GitHub App approach with environment secrets provides excellent security and is production-ready.

## Current Setup

- ✅ **Zero Maintenance** - Set up once, works forever
- ✅ **Automatic Token Rotation** - Fresh 1-hour tokens on each run
- ✅ **Better Security** - Short-lived, repository-scoped tokens
- ✅ **Environment Secrets** - Stored in 'automation' environment
- ✅ **Never Expires** - No token expiration to manage

## How It Works

1. Workflow runs (scheduled or manual)
2. GitHub App token is auto-generated (1-hour lifetime)
3. PR is created using app token
4. PR triggers validation workflows automatically
5. Token expires (no cleanup needed)
6. Next run generates fresh token

## Setup Guide

**👉 [Complete GitHub App Setup Instructions](./GITHUB_APP_SETUP.md)**

Your secrets are configured in: **Settings → Environments → automation**
- `APP_ID`
- `APP_PRIVATE_KEY`

**Setup Time:** ~15 minutes one-time  
**Maintenance Required:** None

## Weekly Release Research Workflow

The **Find New Bourbon and Rye Releases** workflow (`find-new-releases.yml`) uses the
[GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/automate-with-actions)
to run the research agent on a weekly schedule. It requires one additional secret in the
`automation` environment:

| Secret | Description |
|---|---|
| `COPILOT_GITHUB_TOKEN` | Fine-grained PAT with **Copilot Requests (Read)** user permission and **Contents (R/W), Pull Requests (R/W), Metadata (Read)** repository permissions |

This PAT authenticates the Copilot CLI with the AI service, allows `gh` to create PRs, and
lets the GitHub MCP server read/write repository files. Unlike `APP_ID`/`APP_PRIVATE_KEY`,
this token is tied to a **user account** (not a GitHub App), so it will need rotation when
it expires.

## Optional Future Enhancement

**Want maximum security?** You can optionally upgrade to OIDC + Key Vault later:

📖 [OIDC + Key Vault Setup Guide](./OIDC_KEYVAULT_SETUP.md) (Optional)

This stores the private key in Azure Key Vault or AWS Secrets Manager instead of GitHub, with remote signing that never downloads the key.

**When to consider:**
- Enhanced security/compliance requirements
- Already using Azure/AWS
- Want to eliminate all credential storage in GitHub

**Current setup is fine for now** - you can always upgrade later if needed.

## Need Help?

See the [Complete Setup Guide](./GITHUB_APP_SETUP.md) for detailed instructions and troubleshooting.

