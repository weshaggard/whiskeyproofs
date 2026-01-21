# Workflow Security Model

## Overview
This repository uses a defense-in-depth security model to prevent unauthorized deployments to GitHub Pages.

## Security Layers

### 1. CODEOWNERS Protection
**File:** `.github/CODEOWNERS`

Requires @weshaggard approval for changes to:
- All workflow files (`.github/workflows/`)
- Validation scripts (`.github/scripts/validate_*.py`)

**Why this matters:** Prevents PRs from removing the `environment:` declaration or modifying deployment conditions without review.

### 2. Environment Protection Rules ⚠️ **Must Configure**
**Location:** GitHub Settings → Environments → `github-pages`

**Required settings:**
```
✓ Required reviewers: @weshaggard
✓ Deployment branches: Only main branch
```

**Why this matters:** Even if workflow changes are approved, deployments still require manual approval.

### 3. Runtime Checks
**File:** `.github/workflows/build.yml` (line 71)

```yaml
if: (github.event_name == 'push' || github.event_name == 'workflow_dispatch') && github.event.pull_request == null
```

**Why this matters:** Checks at runtime that we're not in a PR context. Even if someone edits the condition in a PR, the check evaluates based on the actual event, not the modified code.

### 4. Minimal Permissions
**File:** `.github/workflows/build.yml`

- Workflow-level: only `contents: read`
- Build job: only `contents: read`  
- Deploy job: scoped to `contents: read`, `pages: write`, `id-token: write`

**Why this matters:** Limits blast radius if a job is compromised.

### 5. Branch Protection Rules ⚠️ **Must Configure**
**Location:** GitHub Settings → Branches → `main`

**Recommended settings:**
```
✓ Require pull request reviews before merging
✓ Require review from Code Owners
✓ Require status checks to pass: validate-and-build
✓ Require branches to be up to date before merging
✓ Do not allow bypassing the above settings
```

**Why this matters:** Enforces that CODEOWNERS approvals are actually required (not just suggested).

## Attack Scenarios & Defenses

### Scenario 1: PR tries to remove `environment:` declaration
- ❌ **Blocked by:** CODEOWNERS requires @weshaggard approval for workflow changes
- ❌ **Blocked by:** Branch protection requires Code Owner review
- ✓ **Even if approved:** Runtime check still prevents PR deployment

### Scenario 2: PR modifies the deployment condition
- ❌ **Blocked by:** CODEOWNERS requires approval
- ❌ **Blocked by:** Branch protection requires Code Owner review  
- ✓ **Even if approved:** `github.event.pull_request == null` evaluates at runtime based on actual event

### Scenario 3: Malicious push to main branch
- ❌ **Blocked by:** Branch protection prevents direct pushes
- ✓ **If somehow pushed:** Environment protection requires manual approval before deployment
- ✓ **If somehow pushed:** Only @weshaggard can approve `github-pages` environment deployments

## Setup Instructions

### Step 1: Enable Branch Protection
1. Go to Settings → Branches
2. Add rule for `main` branch
3. Enable all recommended settings above
4. **Critical:** Enable "Require review from Code Owners"

### Step 2: Configure Environment Protection
1. Go to Settings → Environments
2. Click on `github-pages` (or create if doesn't exist)
3. Add required reviewers: `@weshaggard`
4. Set deployment branches: `Selected branches` → Add `main`

### Step 3: Verify CODEOWNERS
1. CODEOWNERS file exists at `.github/CODEOWNERS`
2. File includes workflow directory protection
3. Test by creating a PR that modifies a workflow file - should require @weshaggard review

## Verification Checklist

- [ ] CODEOWNERS file exists and includes workflow protection
- [ ] Branch protection enabled on `main` with Code Owner requirement
- [ ] Environment protection configured for `github-pages`
- [ ] Required reviewers added to environment
- [ ] Deployment branches restricted to `main`
- [ ] Test PR to workflow file shows Code Owner review requirement

## Why Multiple Layers?

**Single point of failure is bad security.** Each layer provides:
- **CODEOWNERS + Branch Protection:** Prevents malicious workflow changes from being merged
- **Environment Protection:** Prevents deployment even if bad changes are merged  
- **Runtime Checks:** Belt-and-suspenders protection at execution time
- **Minimal Permissions:** Limits damage if a job is compromised

**All layers together** make it extremely difficult for unauthorized deployments to occur.
