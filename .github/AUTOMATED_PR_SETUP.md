# Automated PR Workflow Setup

This document explains how to make the validation pipeline automatically trigger on PRs created by automated workflows (like the TTB label finder) and by GitHub Copilot.

## Quick Links

- **Maintaining the PAT?** See [PAT Maintenance Guide](./PAT_MAINTENANCE.md)
- **Token expired?** See [Emergency Token Renewal](./PAT_MAINTENANCE.md#emergency-token-renewal)
- **Troubleshooting?** See [Troubleshooting](#troubleshooting) below

---

## The Problem

By default, PRs created by `GITHUB_TOKEN` don't trigger `pull_request` workflows. This is a security feature in GitHub Actions to prevent recursive workflow runs.

## The Solution

Use a **Personal Access Token (PAT)** instead of `GITHUB_TOKEN` when creating pull requests. This allows the created PRs to trigger workflows normally.

## Setup Instructions

### Step 1: Create a Personal Access Token

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a descriptive name: `Automated PR Workflow Token`
4. Select scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again!)

### Step 2: Add Token as Repository Secret

1. Go to your repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `PAT`
4. Value: Paste the token you copied
5. Click "Add secret"

**⚠️ Important:** Set a calendar reminder to rotate this token before it expires! See [PAT Maintenance Guide](./PAT_MAINTENANCE.md) for details.

### Step 3: Verify Workflow Configuration

The workflows are already configured to use the PAT token:

**`.github/workflows/find-new-ttb-labels.yml`:**
```yaml
- name: Create Pull Request
  uses: peter-evans/create-pull-request@v7
  with:
    token: ${{ secrets.PAT || secrets.GITHUB_TOKEN }}  # Uses PAT if available
```

The `||` operator means it will use `PAT` if it exists, otherwise fall back to `GITHUB_TOKEN`.

## How It Works

### Before (Complex):
1. TTB workflow creates PR using `GITHUB_TOKEN`
2. PR doesn't trigger validation workflow (security restriction)
3. Separate `workflow_run` trigger required
4. Manual commit status updates needed to show results on PR
5. Extra 70+ lines of complex status management code

### After (Simple):
1. TTB workflow creates PR using `PAT`
2. PR automatically triggers validation workflow via normal `pull_request` trigger
3. Results show up naturally as PR checks
4. No manual status management needed
5. Clean, simple code

## Benefits

✅ **Simple** - Uses standard `pull_request` trigger, no special handling needed  
✅ **Automatic** - PRs trigger validation workflows naturally  
✅ **Visible** - Results appear as PR checks automatically  
✅ **Reliable** - No complex status synchronization logic  
✅ **Maintainable** - 50% less code (84 lines vs 156 lines in build.yml)

## Troubleshooting

### PRs still don't trigger workflows

**Check that the PAT secret exists:**
```bash
# In repository Settings → Secrets → Actions
# Verify "PAT" is listed
```

**Check PAT scopes:**
- Token must have `repo` and `workflow` scopes
- Go to GitHub → Settings → Developer settings → Personal access tokens
- Find your token and verify scopes

**Check token expiration:**
- PATs can expire
- If expired, generate a new one and update the secret

### Workflows run but don't show as PR checks

This shouldn't happen with the PAT approach. If it does:
- Verify the workflow file has `on: pull_request`
- Check workflow run logs for errors
- Ensure branch protection rules don't prevent checks from running

## Security Considerations

**PAT Security:**
- Store PAT as a repository secret (never commit to code)
- Use minimal necessary scopes (`repo` + `workflow`)
- Set an expiration date (e.g., 90 days) and rotate regularly
- Consider using a GitHub App token for better security controls

**⭐ For detailed maintenance procedures, see:** [PAT Maintenance Guide](./PAT_MAINTENANCE.md)

This includes:
- Regular rotation schedule and procedures
- Expiration monitoring
- Emergency renewal steps
- Automation options
- Security best practices

**Alternative: GitHub App Token**

For enterprise/organization use, consider using a GitHub App instead of a PAT:
- More granular permissions
- Better audit logging
- Automatic token rotation
- See: https://github.com/tibdex/github-app-token

## References

- [peter-evans/create-pull-request documentation](https://github.com/peter-evans/create-pull-request)
- [GitHub Actions security hardening](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [Triggering workflows from workflows](https://docs.github.com/en/actions/using-workflows/triggering-a-workflow#triggering-a-workflow-from-a-workflow)
