# Automated PR Workflow Setup

This document explains how to make the validation pipeline automatically trigger on PRs created by automated workflows (like the TTB label finder) and by GitHub Copilot.

## Quick Links

- **🌟 Recommended:** [GitHub App Setup](./GITHUB_APP_SETUP.md) - **Zero maintenance!**
- **Alternative:** [PAT Setup](#setup-instructions-pat-method) - Requires manual rotation every 90 days
- **Token expired?** See [Emergency Token Renewal](./PAT_MAINTENANCE.md#emergency-token-renewal)
- **Troubleshooting?** See [Troubleshooting](#troubleshooting) below

---

## The Problem

By default, PRs created by `GITHUB_TOKEN` don't trigger `pull_request` workflows. This is a security feature in GitHub Actions to prevent recursive workflow runs.

## The Solution

You have two options:

### Option 1: GitHub App (Recommended) ✨

**✅ Zero manual maintenance**
- Tokens rotate automatically (1-hour lifetime)
- No expiration dates to track
- Set up once, works forever
- More secure with granular permissions

**👉 [Follow the GitHub App Setup Guide](./GITHUB_APP_SETUP.md)**

### Option 2: Personal Access Token (PAT)

**⚠️ Requires manual rotation every 90 days**
- Simpler initial setup
- Needs regular maintenance
- Manual token rotation required

**Continue reading below for PAT setup instructions.**

---

## Setup Instructions (PAT Method)

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

The workflows are already configured to use tokens in this priority order:

**`.github/workflows/find-new-ttb-labels.yml`:**
```yaml
- name: Create Pull Request
  uses: peter-evans/create-pull-request@v7
  with:
    # Priority: GitHub App > PAT > GITHUB_TOKEN
    token: ${{ steps.generate_token.outputs.token || secrets.PAT || secrets.GITHUB_TOKEN }}
```

**Token Selection:**
1. **GitHub App token** (if APP_ID and APP_PRIVATE_KEY secrets exist)
2. **PAT** (if PAT secret exists) 
3. **GITHUB_TOKEN** (fallback - won't trigger workflows)

If you set up the GitHub App, you can remove the PAT secret.

## How It Works

### With GitHub App (Recommended):
1. TTB workflow generates a fresh app token (valid 1 hour)
2. PR is created using the app token
3. PR automatically triggers validation workflow via normal `pull_request` trigger
4. Results show up naturally as PR checks
5. Token expires automatically (no cleanup needed)

### With PAT (Alternative):
1. TTB workflow creates PR using manually-created PAT
2. PR automatically triggers validation workflow via normal `pull_request` trigger
3. Results show up naturally as PR checks
4. **Requires manual token rotation every 90 days**

### Before (Old Complex Approach):
1. TTB workflow creates PR using `GITHUB_TOKEN`
2. PR doesn't trigger validation workflow (security restriction)
3. Separate `workflow_run` trigger required
4. Manual commit status updates needed to show results on PR
5. Extra 70+ lines of complex status management code

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

**Recommendation: Use GitHub App for Best Security**

GitHub Apps provide better security than PATs:
- ✅ Short-lived tokens (1 hour vs 90 days)
- ✅ Granular, repository-scoped permissions
- ✅ Better audit logging
- ✅ Automatic rotation (no manual process)

**👉 [Set up GitHub App](./GITHUB_APP_SETUP.md)**

**If Using PAT:**
- Store PAT as a repository secret (never commit to code)
- Use minimal necessary scopes (`repo` + `workflow`)
- Set an expiration date (e.g., 90 days) and rotate regularly
- Consider migrating to GitHub App for zero maintenance

**⭐ For detailed PAT maintenance procedures, see:** [PAT Maintenance Guide](./PAT_MAINTENANCE.md)

This includes:
- Regular rotation schedule and procedures
- Expiration monitoring
- Emergency renewal steps
- Security best practices

**Migration Path: PAT → GitHub App**

Already using a PAT? You can easily migrate:

1. Set up GitHub App (one-time, 15 minutes)
2. Test that it works
3. Remove the PAT secret (no longer needed)

See [GitHub App Setup Guide](./GITHUB_APP_SETUP.md) for migration instructions.

## References

- [peter-evans/create-pull-request documentation](https://github.com/peter-evans/create-pull-request)
- [GitHub Actions security hardening](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [Triggering workflows from workflows](https://docs.github.com/en/actions/using-workflows/triggering-a-workflow#triggering-a-workflow-from-a-workflow)
