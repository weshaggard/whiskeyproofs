# GitHub App Setup for Automated PRs

**🎯 Zero Manual Maintenance Required!**

This guide shows you how to set up a GitHub App for automated PR workflows. GitHub Apps provide automatic token rotation with no manual maintenance needed.

## Why GitHub App?

- ✅ **Zero Maintenance** - Set up once, works forever
- ✅ **Automatic Token Rotation** - Fresh 1-hour tokens on each run
- ✅ **Better Security** - Short-lived, repository-scoped tokens
- ✅ **Granular Permissions** - Only what's needed
- ✅ **Detailed Audit Logging** - Track all actions
- ✅ **Never Expires** - No token expiration to manage

## Prerequisites

- Repository admin access
- Ability to create GitHub Apps in your account/organization

## Setup Instructions

### Step 1: Create the GitHub App

1. **Navigate to GitHub App settings:**
   - **Personal account:** https://github.com/settings/apps/new
   - **Organization:** https://github.com/organizations/YOUR_ORG/settings/apps/new

2. **Configure the App:**

   **GitHub App name:** `whiskeyproofs-automation` (or your preferred name)
   
   **Description:** `Automated PR creation for TTB labels and other workflows`
   
   **Homepage URL:** `https://github.com/weshaggard/whiskeyproofs`
   
   **Webhook:**
   - ☑️ **Uncheck** "Active" (we don't need webhooks)
   
   **Permissions:**
   
   Under "Repository permissions":
   - **Contents:** Read and write
   - **Pull requests:** Read and write
   - **Workflows:** Read and write
   
   **Where can this GitHub App be installed?**
   - ⚫ Only on this account
   
3. **Click "Create GitHub App"**

4. **Save the App ID:**
   - You'll see "App ID" on the app's settings page
   - Copy this number (e.g., `123456`)
   - You'll need it later

### Step 2: Generate Private Key

1. **On the app settings page, scroll to "Private keys"**

2. **Click "Generate a private key"**

3. **A `.pem` file will download**
   - Keep this file secure!
   - You'll need its contents for the repository secret

4. **Open the `.pem` file in a text editor:**
   ```bash
   # On Mac/Linux:
   cat ~/Downloads/whiskeyproofs-automation.*.private-key.pem
   
   # On Windows:
   notepad %USERPROFILE%\Downloads\whiskeyproofs-automation.*.private-key.pem
   ```

5. **Copy the entire contents** (including `-----BEGIN RSA PRIVATE KEY-----` and `-----END RSA PRIVATE KEY-----`)

### Step 3: Install the App on Your Repository

1. **From the app settings page, click "Install App" in the left sidebar**

2. **Select your account** (or organization)

3. **Choose repository access:**
   - ⚫ Only select repositories
   - ☑️ Select `weshaggard/whiskeyproofs`

4. **Click "Install"**

### Step 4: Add Secrets to Repository

1. **Go to your repository:**
   https://github.com/weshaggard/whiskeyproofs/settings/secrets/actions

2. **Add two secrets:**

   **Secret 1: `APP_ID`**
   - Click "New repository secret"
   - Name: `APP_ID`
   - Value: The App ID from Step 1.4 (e.g., `123456`)
   - Click "Add secret"

   **Secret 2: `APP_PRIVATE_KEY`**
   - Click "New repository secret"
   - Name: `APP_PRIVATE_KEY`
   - Value: The entire `.pem` file contents from Step 2.5
   - Click "Add secret"

### Step 5: Verify Workflow Configuration

The workflow file `.github/workflows/find-new-ttb-labels.yml` is already configured to use the GitHub App token:

```yaml
- name: Generate GitHub App Token
  id: generate_token
  uses: actions/create-github-app-token@v1
  with:
    app-id: ${{ secrets.APP_ID }}
    private-key: ${{ secrets.APP_PRIVATE_KEY }}
    repositories: ${{ github.repository }}

- name: Create Pull Request
  uses: peter-evans/create-pull-request@v7
  with:
    token: ${{ steps.generate_token.outputs.token }}
```

No changes needed - the workflow is ready to use once you add the secrets!

### Step 6: Test the Setup

1. **Go to Actions → Find New TTB Labels**
   https://github.com/weshaggard/whiskeyproofs/actions/workflows/find-new-ttb-labels.yml

2. **Click "Run workflow"**

3. **Verify:**
   - ✅ Workflow completes successfully
   - ✅ PR is created (if new labels found)
   - ✅ Validation workflows trigger automatically on the PR
   - ✅ Status checks appear on the PR

## How It Works

1. **Workflow starts** (scheduled or manual trigger)
2. **GitHub App token is generated** using `actions/create-github-app-token`
   - Token is valid for 1 hour
   - Token is scoped to this repository only
3. **PR is created** using the app token
4. **PR triggers validation workflows** (because it's not created with GITHUB_TOKEN)
5. **Token expires** after 1 hour (automatically, no cleanup needed)
6. **Next run** generates a fresh token

## Maintenance

**Required maintenance:** ✨ **NONE!** ✨

- ✅ Tokens rotate automatically
- ✅ No expiration dates to track
- ✅ No manual renewal needed
- ✅ No calendar reminders required

## Troubleshooting

### Error: "GitHub App token generation failed"

**Check:**
- APP_ID secret is correct (numbers only, no quotes)
- APP_PRIVATE_KEY secret contains the full `.pem` file contents
- GitHub App is installed on the repository
- GitHub App has the correct permissions

### Error: "Resource not accessible by integration"

**Fix:**
- Check that the GitHub App has the required permissions:
  - Contents: Read and write
  - Pull requests: Read and write
  - Workflows: Read and write

### Workflows still don't trigger on PRs

**Verify:**
- The PR was created with the app token (not GITHUB_TOKEN)
- Check workflow logs to see which token was used
- Ensure `.github/workflows/build.yml` has `on: pull_request`

### GitHub App shows "Suspended"

**Reason:**
- App may have been inactive for too long
- Contact GitHub support to reactivate

## Security Considerations

**Best Practices:**

✅ **Store private key as secret** - Never commit to git  
✅ **Use repository-scoped installation** - Don't grant access to all repos  
✅ **Minimal permissions** - Only grant what's needed  
✅ **Monitor app activity** - Check the app's activity log periodically  
✅ **Rotate private key if compromised** - Generate new key immediately  

**Private Key Security:**

- The private key is like a password for your app
- Store the `.pem` file securely (password manager, encrypted storage)
- Don't share it with anyone
- If compromised, immediately:
  1. Revoke the old key in app settings
  2. Generate a new private key
  3. Update the APP_PRIVATE_KEY secret

## Key Benefits

1. **No Maintenance:** Set up once, works forever
2. **Better Security:** Short-lived tokens (1 hour)
3. **Audit Trail:** Detailed logs of all actions
4. **Granular Permissions:** Scoped to specific repositories
5. **No Expiration:** App itself doesn't expire
6. **Professional:** Better for teams and organizations

## Support and Resources

- **GitHub Apps Documentation:** https://docs.github.com/en/apps
- **actions/create-github-app-token:** https://github.com/actions/create-github-app-token
- **Security best practices:** https://docs.github.com/en/apps/creating-github-apps/setting-up-a-github-app/best-practices-for-creating-a-github-app

## Quick Reference

| Item | Value | Location |
|------|-------|----------|
| App Settings | - | https://github.com/settings/apps |
| Repository Secrets | APP_ID, APP_PRIVATE_KEY | Repository Settings → Secrets |
| Workflow File | find-new-ttb-labels.yml | `.github/workflows/` |
| Test Workflow | Run workflow manually | Actions tab |

---

**🎉 Congratulations!** You now have a zero-maintenance automated PR system. No more token rotation reminders!
