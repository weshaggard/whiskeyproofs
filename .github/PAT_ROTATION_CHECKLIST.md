# PAT Rotation Checklist

Use this checklist when rotating the Personal Access Token.

## Pre-Rotation

- [ ] Note current token expiration date
- [ ] Schedule 30-60 minutes for rotation and testing
- [ ] Inform team members (if applicable)

## Rotation Steps

### 1. Create New Token
- [ ] Go to: https://github.com/settings/tokens
- [ ] Click "Generate new token (classic)"
- [ ] Name: `Automated PR Workflow Token (MMM YYYY)` e.g., "Feb 2026"
- [ ] Expiration: 90 days
- [ ] Scopes: ✅ `repo` ✅ `workflow`
- [ ] Click "Generate token"
- [ ] **Copy token immediately** (save to password manager)

### 2. Update Repository Secret
- [ ] Go to: https://github.com/weshaggard/whiskeyproofs/settings/secrets/actions
- [ ] Find `PAT` secret
- [ ] Click "Update"
- [ ] Paste new token
- [ ] Click "Update secret"

### 3. Test
- [ ] Go to: https://github.com/weshaggard/whiskeyproofs/actions/workflows/find-new-ttb-labels.yml
- [ ] Click "Run workflow"
- [ ] Wait for workflow to complete
- [ ] Verify PR was created
- [ ] Verify validation workflows triggered automatically
- [ ] Check that PR has status checks

### 4. Clean Up
- [ ] Go back to: https://github.com/settings/tokens
- [ ] Find old token (look for older date)
- [ ] Click "Delete"
- [ ] Confirm deletion

### 5. Document
- [ ] Update `.github/PAT_MAINTENANCE.md` version history with rotation date
- [ ] Set calendar reminder for next rotation (90 days from now)
- [ ] Note next expiration date: _______________

## Post-Rotation

- [ ] Monitor workflows for 24 hours
- [ ] Verify scheduled TTB workflow runs successfully
- [ ] Notify team rotation is complete (if applicable)

---

**Next scheduled rotation:** _______________

**Last rotated by:** _______________

**Last rotated on:** _______________
