# GitHub Actions Workflow Triggers

This document explains how workflows are triggered in this repository.

## Validation Workflow Triggers

The `build.yml` workflow (Validate, Build, and Deploy) is triggered by multiple events:

### 1. Pull Request Trigger
```yaml
pull_request:
  branches: ["main"]
```
Runs validation when a PR is opened or updated targeting the `main` branch.

**This includes automated PRs** created by the TTB label finder workflow and GitHub Copilot (when properly configured).

### 2. Push Trigger
```yaml
push:
  branches: ["main"]
```
Runs validation and deployment when code is pushed to `main`.

### 3. Manual Trigger
```yaml
workflow_dispatch:
```
Allows manual triggering from the Actions tab.

## Discovery Source Health

The `check-discovery-sources.yml` workflow runs daily at **08:17 UTC** (before
release discovery at 09:00 UTC) and can also be started with `workflow_dispatch`.
It runs independently, so a broken source does not block release discovery.

The dependency-free checker reads the fallback source links directly from
`.github/prompts/find-new-releases.prompt.md`, avoiding a separate URL list that
could drift. It uses HTTPS GET requests with certificate verification, a
20-second request timeout, and at most three retries for network errors, HTTP
429, and HTTP 5xx. HTTP 4xx errors such as 403/404/410 fail immediately.

Every source must return HTML with whiskey-related text and links. Breaking
Bourbon must also contain press-release article links, so a generic landing page
cannot silently replace its release listing. These are availability/content
smoke checks, not a guarantee that announcements are current or complete.
Bot-protection pages may require manual verification.

Failures produce a failed Actions run, a job summary, and an issue titled
**Discovery source health check failing**. Subsequent failures update the
existing open issue rather than creating daily duplicates. The issue links to
the latest failing run and lists source errors. GitHub's usual issue and Actions
notification settings control email/web notifications; no external alerting
credentials are needed.

To investigate, open the linked run, verify the source in a browser, update the
discovery prompt if the URL moved, and manually rerun **Discovery Source Health**.
Close the alert issue after a successful rerun. The monitor does not rewrite
source URLs or whiskey data automatically.

Local checks (from the repository root):

```bash
python3 -m unittest discover -s .github/scripts -p 'test_check_discovery_sources.py'
python3 .github/scripts/check_discovery_sources.py --report /tmp/source-health.md
```

## Automated PR Setup

To enable automatic workflow triggering for PRs created by automated workflows (TTB label finder) and GitHub Copilot, **see the detailed setup guide:**

📖 **[GitHub App Setup Guide](./GITHUB_APP_SETUP.md)**

This guide covers:
- Creating a GitHub App for automated tokens
- Configuring app permissions
- Adding secrets to the repository
- Zero-maintenance token rotation

**Summary:** Automated workflows use a GitHub App to generate short-lived tokens for creating PRs, which allows those PRs to trigger the `pull_request` workflow naturally.


## Workflow Permissions

The validation workflow uses minimal permissions:

```yaml
permissions:
  contents: read
```

The deployment job has additional permissions for GitHub Pages:

```yaml
permissions:
  contents: read
  pages: write
  id-token: write
```

## Testing Workflows

### Test Automated PR Workflow
1. Ensure GitHub App is configured (see [GitHub App Setup Guide](./GITHUB_APP_SETUP.md))
2. Manually trigger "Find New TTB Labels" workflow from Actions tab
3. It will create a PR with new labels
4. The validation workflow should automatically run via `pull_request` trigger
5. Check the PR to see validation results as status checks

### Test Copilot PR Workflow
1. Create a PR using Copilot (ask it to make a change)
2. Workflows should run automatically
3. If they don't, check repository settings (Settings → Actions → General)
