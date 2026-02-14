# GitHub Actions Workflow Triggers

This document explains how workflows are triggered in this repository and solutions for automated PR workflows.

## Validation Workflow Triggers

The `build.yml` workflow (Validate, Build, and Deploy) is triggered by multiple events:

### Conditional Validation

The CSV validation and URL validation steps are **conditional** - they only run if the `_data/whiskeyindex.csv` file was modified compared to the `main` branch. This prevents:
- False positives from pre-existing URL issues in automated label-only PRs
- Unnecessary validation overhead when only documentation or label files change
- Blocking of automated TTB label PRs due to unrelated data quality issues

If the CSV was not modified, the workflow will skip these validation steps and proceed directly to building the Jekyll site.

### 1. Pull Request Trigger
```yaml
pull_request:
  branches: ["main"]
```
Runs validation when a PR is opened or updated targeting the `main` branch.

### 2. Push Trigger
```yaml
push:
  branches: ["main"]
```
Runs validation and deployment when code is pushed to `main`.

### 3. Workflow Run Trigger
```yaml
workflow_run:
  workflows: ["Find New TTB Labels"]
  types:
    - completed
```
Runs validation after the "Find New TTB Labels" workflow completes.

**Why is this needed?**

GitHub Actions has a security feature where workflows triggered by `GITHUB_TOKEN` (like automated PRs) don't automatically trigger other workflows. This prevents recursive workflow runs.

The `workflow_run` trigger works around this limitation by explicitly running the validation workflow after the TTB label finder workflow completes, ensuring automated PRs are validated.

**Branch Checkout:**

The "Find New TTB Labels" workflow always creates/updates a PR with the branch name `automated/new-ttb-labels`. When triggered by `workflow_run`, the validation workflow explicitly checks out this branch:

```yaml
ref: ${{ (github.event_name == 'workflow_run' && github.event.workflow_run.name == 'Find New TTB Labels') && 'automated/new-ttb-labels' || github.ref }}
```

This is necessary because `workflow_run` events execute on the default branch context (main), not the PR branch context. The conditional:
1. Checks if the event is `workflow_run` AND the triggering workflow is "Find New TTB Labels"
2. If both conditions are true, uses the known branch name `automated/new-ttb-labels`
3. Otherwise, uses the default ref (for pull_request events or other triggers)

### 4. Manual Trigger
```yaml
workflow_dispatch:
```
Allows manual triggering from the Actions tab.

## Copilot-Created PR Approvals

### The Problem

PRs created by GitHub Copilot require manual approval before workflows run. This is a repository security setting.

### The Solution

To allow Copilot workflows to run automatically without approval:

1. Go to repository **Settings** → **Actions** → **General**
2. Scroll to **Fork pull request workflows from outside collaborators**
3. Select one of these options:
   - **"Require approval for first-time contributors who are new to GitHub"** (recommended)
   - **"Require approval for first-time contributors"**
   - **"Require approval for all outside collaborators"** (current setting - most restrictive)

**Recommended Setting**: "Require approval for first-time contributors who are new to GitHub"

This allows established bots like GitHub Copilot to run workflows automatically while still protecting against malicious PRs from new contributors.

### Alternative Solution

If you prefer to keep strict controls, you can:

1. Add the Copilot bot as a repository collaborator with write access
2. This will allow its workflows to run automatically

**Note**: This is generally not necessary as Copilot is a trusted GitHub service.

## Workflow Permissions

The validation workflow uses minimal permissions:

```yaml
permissions:
  contents: read
  pull-requests: read  # For workflow_run to fetch PR information
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
1. Manually trigger "Find New TTB Labels" workflow from Actions tab
2. It will create a PR with new labels
3. The validation workflow should automatically run via `workflow_run` trigger
4. Check the Actions tab to verify both workflows completed

### Test Copilot PR Workflow
1. Create a PR using Copilot (ask it to make a change)
2. After updating repository settings, workflows should run automatically
3. If manual approval is still required, verify the setting was saved correctly

## Troubleshooting

### Validation doesn't run for automated PRs
- Verify `workflow_run` trigger is in `build.yml`
- Check that the workflow name matches exactly: "Find New TTB Labels"
- Look in Actions tab to see if workflow_run was triggered

### Copilot PRs still require approval
- Verify repository settings were saved
- Check if Copilot is listed as an outside collaborator
- Try the alternative solution (add as collaborator)

### Workflow runs on wrong branch
- Check the `ref` parameter in the checkout step
- For workflow_run: uses `github.event.workflow_run.head_branch`
- For pull_request: uses default PR head (`github.ref`)
