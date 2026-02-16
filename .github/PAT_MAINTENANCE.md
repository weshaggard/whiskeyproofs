# PAT Maintenance Guide

This guide explains how to maintain the Personal Access Token (PAT) used for automated workflow PRs.

## Overview

The repository uses a PAT to enable automated PRs (from the TTB label finder and GitHub Copilot) to trigger validation workflows. This token needs regular maintenance to ensure continuous operation.

## Maintenance Schedule

### Recommended Timeline

**Every 90 days:**
- Rotate the PAT (create new, update secret, delete old)

**Every 30 days:**
- Check token expiration date
- Verify workflows are functioning

**When workflows fail:**
- Check if PAT has expired
- Verify token still has correct scopes

## Monitoring PAT Health

### How to Check Token Status

1. **Go to GitHub Settings:**
   - Navigate to: https://github.com/settings/tokens
   - Or: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **Locate Your Token:**
   - Look for: "Automated PR Workflow Token" (or whatever name you used)
   - Check the "Expires" column

3. **Verify Scopes:**
   - Click on the token name
   - Confirm it has: `repo` and `workflow` scopes

### Signs of Token Issues

🚨 **Automated PRs are created but workflows don't run**
- Token may have expired
- Token may be missing `workflow` scope

🚨 **TTB label workflow fails with authentication error**
- Token has been deleted or revoked
- Repository secret may be misconfigured

🚨 **Workflows trigger but fail immediately**
- Token may have insufficient permissions
- Check for scope changes

## Token Rotation Procedure

Follow these steps to rotate your PAT safely (or use the [PAT Rotation Checklist](./PAT_ROTATION_CHECKLIST.md) for a printable version):

### Step 1: Create New Token

1. Go to: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Configure:
   - **Name:** `Automated PR Workflow Token` (add date: e.g., "Feb 2026")
   - **Expiration:** 90 days (recommended) or custom
   - **Scopes:**
     - ✅ `repo` (Full control of private repositories)
     - ✅ `workflow` (Update GitHub Action workflows)
4. Click "Generate token"
5. **Copy the token immediately** 🔑

### Step 2: Update Repository Secret

1. Go to repository: https://github.com/weshaggard/whiskeyproofs
2. Navigate to: Settings → Secrets and variables → Actions
3. Find the `PAT` secret
4. Click "Update" (or delete and recreate)
5. Paste the new token value
6. Click "Update secret"

### Step 3: Test the New Token

1. Manually trigger the "Find New TTB Labels" workflow:
   - Go to Actions → Find New TTB Labels → Run workflow
2. If it creates a PR, verify that:
   - The PR is created successfully
   - Validation workflows trigger automatically
   - Checks appear on the PR

### Step 4: Delete Old Token (Optional but Recommended)

1. Return to: GitHub → Settings → Developer settings → Personal access tokens
2. Find the old token (look for older date in name)
3. Click "Delete"
4. Confirm deletion

**Why delete?** Reduces security risk if old token is compromised.

## Expiration Management

### Setting Appropriate Expiration

**90 Days (Recommended):**
- Good balance between security and convenience
- Quarterly rotation aligns with business cycles
- Enough time to notice and react

**Custom Date:**
- Align with your maintenance schedule
- Consider team availability (avoid holidays)
- Set calendar reminders 1-2 weeks before expiration

**No Expiration (Not Recommended):**
- Security risk if token is leaked
- No forced rotation means token may never be updated
- GitHub may eventually require expiration

### Calendar Reminders

Set up reminders to rotate before expiration:

1. **When creating token:** Note expiration date
2. **Set reminder:** 2 weeks before expiration
3. **Use calendar:** Google Calendar, Outlook, etc.
4. **Reminder text:** "Rotate GitHub PAT for whiskeyproofs repo"

Example schedule if token expires April 1, 2026:
- **March 15, 2026:** Reminder to rotate
- **March 31, 2026:** Final warning
- **April 1, 2026:** Token expires (workflows will fail)

## Emergency Token Renewal

If the token has already expired and workflows are failing:

### Quick Recovery Steps

1. **Generate new token immediately** (follow Step 1 above)
2. **Update repository secret** (follow Step 2 above)
3. **Test immediately:**
   - Trigger a workflow manually
   - Or wait for next scheduled run
4. **Monitor for 24 hours** to ensure everything works

### Communication

If you're on a team:
- Notify team members about the expiration
- Share the maintenance schedule
- Document who is responsible for rotation

## Automation Options

### Option 1: GitHub App Token (Advanced)

Instead of a PAT, use a GitHub App for better security and automatic rotation:

**Benefits:**
- Tokens rotate automatically (1 hour lifetime)
- More granular permissions
- Better audit logging
- Can be scoped to single repository

**Setup:**
1. Create a GitHub App: https://github.com/settings/apps/new
2. Install it on your repository
3. Use [`tibdex/github-app-token`](https://github.com/tibdex/github-app-token) action
4. Update workflow to use app token

**Example:**
```yaml
- name: Generate token
  id: generate_token
  uses: tibdex/github-app-token@v2
  with:
    app_id: ${{ secrets.APP_ID }}
    private_key: ${{ secrets.APP_PRIVATE_KEY }}

- name: Create Pull Request
  uses: peter-evans/create-pull-request@v7
  with:
    token: ${{ steps.generate_token.outputs.token }}
```

### Option 2: Expiration Monitoring Workflow

Create a workflow to check PAT expiration (requires GitHub CLI setup):

```yaml
name: Check PAT Expiration

on:
  schedule:
    - cron: '0 0 * * 1'  # Weekly on Monday
  workflow_dispatch:

jobs:
  check-pat:
    runs-on: ubuntu-latest
    steps:
      - name: Check if PAT is expiring soon
        run: |
          echo "⚠️ Manual check required:"
          echo "1. Go to https://github.com/settings/tokens"
          echo "2. Check 'Automated PR Workflow Token' expiration"
          echo "3. If expiring in < 14 days, rotate it"
          echo "4. See .github/PAT_MAINTENANCE.md for rotation steps"
```

## Security Best Practices

### Do's ✅

- ✅ Set expiration dates (90 days recommended)
- ✅ Use minimal scopes (`repo` + `workflow` only)
- ✅ Store token as GitHub secret (never in code)
- ✅ Rotate tokens regularly
- ✅ Delete old tokens after rotation
- ✅ Use descriptive token names with dates
- ✅ Document token ownership/responsibility
- ✅ Test after rotation

### Don'ts ❌

- ❌ Never commit tokens to git
- ❌ Don't share tokens in chat/email
- ❌ Don't use tokens with excess permissions
- ❌ Don't create tokens with no expiration
- ❌ Don't forget to delete old tokens
- ❌ Don't share the same token across multiple repos
- ❌ Don't skip testing after rotation

## Troubleshooting

### Token Expired

**Symptoms:**
- Workflows fail with authentication errors
- PRs created but workflows don't trigger
- Error: "Resource not accessible by integration"

**Solution:**
Follow "Emergency Token Renewal" steps above.

### Token Missing Scopes

**Symptoms:**
- PRs created but can't update workflows
- Error about insufficient permissions

**Solution:**
1. Create new token with correct scopes (`repo` + `workflow`)
2. Update repository secret
3. Test

### Secret Not Found

**Symptoms:**
- Error: "Secret PAT not found"
- Workflow falls back to GITHUB_TOKEN

**Solution:**
1. Verify secret name is exactly `PAT` (case-sensitive)
2. Check repository Settings → Secrets → Actions
3. Ensure secret is in the correct repository

### Multiple Tokens Confusion

**Problem:**
- Have multiple tokens, unsure which is current

**Solution:**
1. Check token names for dates
2. Delete all old tokens
3. Keep only one token with recent date
4. Update repository secret with current token

## Checklist: Token Rotation

Use this checklist when rotating:

- [ ] Create new token with 90-day expiration
- [ ] Copy token to secure location (password manager)
- [ ] Update `PAT` repository secret
- [ ] Manually trigger test workflow
- [ ] Verify PR creation works
- [ ] Verify validation workflows trigger
- [ ] Check PR status checks appear
- [ ] Delete old token from GitHub
- [ ] Update documentation with new expiration date
- [ ] Set calendar reminder for next rotation
- [ ] Notify team (if applicable)

## Quick Reference

| Task | Frequency | Link |
|------|-----------|------|
| Check expiration | Monthly | [GitHub Tokens](https://github.com/settings/tokens) |
| Rotate token | Every 90 days | See "Token Rotation Procedure" above |
| Test workflows | After rotation | [Actions Tab](../../actions) |
| Update documentation | After rotation | Update this file with new date |

## Support

If you encounter issues:

1. Check this maintenance guide
2. Review [AUTOMATED_PR_SETUP.md](./AUTOMATED_PR_SETUP.md) for initial setup
3. Check [WORKFLOW_TRIGGERS.md](./WORKFLOW_TRIGGERS.md) for workflow details
4. Create an issue in the repository with details

## Version History

- **2026-02-16:** Initial maintenance guide created
- Document next rotation date here when performed
