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

## Automated PR Setup

To enable automatic workflow triggering for PRs created by automated workflows (TTB label finder) and GitHub Copilot, **see the detailed setup guide:**

📖 **[AUTOMATED_PR_SETUP.md](./AUTOMATED_PR_SETUP.md)**

This guide covers:
- Creating a Personal Access Token (PAT)
- Adding it as a repository secret
- How it enables automatic PR workflow triggering
- Troubleshooting common issues

**Summary:** Automated workflows use a PAT instead of `GITHUB_TOKEN` to create PRs, which allows those PRs to trigger the `pull_request` workflow naturally.


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
1. Ensure PAT secret is configured (see [AUTOMATED_PR_SETUP.md](./AUTOMATED_PR_SETUP.md))
2. Manually trigger "Find New TTB Labels" workflow from Actions tab
3. It will create a PR with new labels
4. The validation workflow should automatically run via `pull_request` trigger
5. Check the PR to see validation results as status checks

### Test Copilot PR Workflow
1. Create a PR using Copilot (ask it to make a change)
2. Workflows should run automatically
3. If they don't, check repository settings (Settings → Actions → General)
