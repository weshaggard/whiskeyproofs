# Security Analysis: GitHub App Private Key Storage

This document addresses security concerns about storing the GitHub App private key in repository secrets.

## Your Concern

> "Is there any other option than storing the entire private key in a secret and downloading it to the agent to get the token? I worry that the private key might get leaked."

## Short Answer

**Unfortunately, no.** All methods for triggering workflows on automated PRs require storing some form of credential (private key or token) in GitHub secrets. This is a fundamental GitHub Actions security design.

## Why Credential Storage is Required

GitHub Actions has an intentional security restriction:

> "When you use the repository's `GITHUB_TOKEN` to perform tasks, events triggered by the `GITHUB_TOKEN` will not create a new workflow run. This prevents you from accidentally creating recursive workflow runs."
> 
> — [GitHub Documentation: Triggering a workflow from a workflow](https://docs.github.com/en/actions/using-workflows/triggering-a-workflow#triggering-a-workflow-from-a-workflow)

**This means:**
- GITHUB_TOKEN cannot be used to trigger `pull_request` workflows
- You **must** use a different credential type
- ALL alternative credential types require storing secrets

## Available Options (All Require Secrets)

| Method | Secret to Store | Risk Level | Scope |
|--------|----------------|------------|-------|
| **GitHub App** | Private Key (.pem file) | Medium | Repository-scoped |
| **PAT** | Access Token | High | User-scoped |
| **SSH Deploy Key** | Private SSH Key | Medium | Repository-scoped |

**There is no "secretless" option** for triggering GitHub Actions workflows from within GitHub Actions.

## Why GitHub App is Actually the MOST Secure Option

Despite requiring private key storage, GitHub App is the **most secure** approach because:

### 1. Short-Lived Tokens (1 Hour)
- Generated tokens expire after 1 hour
- If a token leaks, it's only valid briefly
- Compare to PAT: 90-day lifetime

### 2. Repository-Scoped Permissions
- App is installed only on specific repositories
- Cannot access other repos
- Compare to PAT: Access to all repos the user can access

### 3. Granular Permissions
- Only has exact permissions needed:
  - Contents: Read & write
  - Pull requests: Read & write
  - Workflows: Read & write
- Compare to PAT: Broad `repo` and `workflow` scopes

### 4. The Private Key Never Leaves GitHub's Infrastructure

This is crucial to understand:

✅ **The private key is stored encrypted in GitHub Secrets**
- Encrypted at rest using AES-256-GCM
- Only decrypted at runtime in the secure runner environment
- Never exposed in logs or outputs

✅ **The private key is only used momentarily**
- Loaded into memory on the runner
- Used to generate a 1-hour token
- Runner environment is destroyed after workflow completes

✅ **The token (not the key) is what's actually used**
- The private key generates a token
- The token is what interacts with GitHub API
- The token expires quickly

## Security Best Practices to Minimize Risk

### 1. Use Environment Secrets (You're Already Doing This!)

✅ You've stored secrets in the 'automation' environment - this is excellent!

**Benefits:**
- Better access control
- Can add protection rules
- Organized separately from general secrets
- Can restrict which workflows access them

### 2. Limit App Installation Scope

✅ **Install app on minimal repositories**
- Only install on `weshaggard/whiskeyproofs`
- Don't install organization-wide

### 3. Use Minimal Permissions

✅ **Only grant what's needed:**
- Contents: Read & write (for creating commits)
- Pull requests: Read & write (for creating PRs)
- Workflows: Read & write (for updating workflow files, if needed)

**Don't grant:**
- Issues, Projects, or other unnecessary permissions

### 4. Monitor App Activity

📊 **Regularly check your GitHub App's activity:**
- https://github.com/settings/apps
- Click on your app
- View "Advanced" tab for activity logs
- Look for unusual patterns

### 5. Rotate Private Key if Compromise Suspected

If you ever suspect the key may have been exposed:
1. Generate new private key in app settings
2. Update APP_PRIVATE_KEY secret immediately
3. Revoke old private key

## Why This is Still Secure

### GitHub Secrets Security Model

GitHub Secrets are designed for this exact purpose:

1. **Encrypted at Rest**
   - AES-256-GCM encryption
   - Keys managed by GitHub's infrastructure
   - Cannot be read once added

2. **Encrypted in Transit**
   - Secrets transmitted over TLS
   - Never exposed in plain text over network

3. **Limited Exposure**
   - Only decrypted in runner memory during execution
   - Automatically redacted from logs
   - Runner environment destroyed after use

4. **Access Controls**
   - Only accessible to workflows in the repository
   - Environment protection rules can be added
   - Audit logs track secret access

### Comparison to Other Secret Storage

**GitHub Secrets vs Other Options:**

| Storage Method | GitHub Secrets | Self-Hosted Solution |
|----------------|----------------|---------------------|
| **Encryption** | AES-256-GCM | Depends on implementation |
| **Key Management** | GitHub-managed | You manage |
| **Access Logs** | Built-in | Must implement |
| **Exposure Risk** | Low (GitHub's security) | Varies |
| **Maintenance** | None | Regular updates needed |

Storing the private key in GitHub Secrets is **safer** than many alternatives (like environment variables on a self-hosted server).

## What About OIDC Federation?

**OIDC (OpenID Connect)** is a modern secretless auth approach, but:

❌ **Not applicable here** - OIDC is for authenticating GitHub Actions to **external cloud providers** (AWS, Azure, GCP), not for GitHub-to-GitHub authentication.

OIDC scenarios:
- ✅ GitHub Actions → AWS (get AWS credentials without storing keys)
- ✅ GitHub Actions → Azure (get Azure credentials without storing keys)
- ❌ GitHub Actions → GitHub API (not supported)

## The Reality: Trade-offs Are Necessary

There is **no perfect solution** without storing credentials. You must choose based on your risk tolerance:

### Option 1: GitHub App (Recommended)
**Security Level:** High  
**Maintenance:** None  
**Credential Stored:** Private key  
**Risk Mitigation:** Short-lived tokens, repository-scoped, granular permissions

### Option 2: Just Use GITHUB_TOKEN (Most Secure, Limited Functionality)
**Security Level:** Highest  
**Maintenance:** None  
**Credential Stored:** None (built-in)  
**Trade-off:** Workflows won't trigger on automated PRs - you'd manually approve/reopen each PR

## My Recommendation

**Use the GitHub App approach** because:

1. ✅ The private key is as secure as it can be in GitHub Secrets
2. ✅ Environment secrets add an extra layer of protection
3. ✅ Short-lived tokens minimize blast radius if compromised
4. ✅ Repository-scoped installation limits access
5. ✅ This is the industry-standard approach for automated PRs
6. ✅ Used by thousands of repositories including major open source projects

**The risk is manageable** with proper controls:
- Environment secrets (you have this)
- Minimal permissions (configured correctly)
- Limited scope (single repository)
- Activity monitoring (built-in)

## If You're Still Concerned

### Option 1: OIDC + Key Vault (Advanced - Optional)

If you need maximum security and can invest in setup time:

**✅ Use OIDC + Azure Key Vault or AWS Secrets Manager**

This approach:
- Stores private key in cloud provider (Azure/AWS)
- Uses OIDC for authentication (no cloud credentials in GitHub)
- With Azure: Private key **never** downloaded (remote signing)
- Enhanced audit logging and compliance

**📖 See:** [OIDC + Key Vault Setup Guide](./OIDC_KEYVAULT_SETUP.md)

**When to use:**
- Maximum security requirements
- Regulatory/compliance needs
- Already using Azure or AWS
- Want to eliminate GitHub secret storage

**Setup time:** 1-2 hours (one-time)  
**Maintenance:** None  
**Cost:** ~$1-2/month (cloud provider fees)

### Option 2: Manual Approval Workflow (Most Secure, Least Practical)

If you absolutely cannot accept storing a private key, your only option is:

1. **Use GITHUB_TOKEN** (no private key storage)
2. **Accept that workflows won't trigger automatically**
3. **Manually reopen PRs** to trigger workflows

**Workflow:**
- Automated workflow creates PR with GITHUB_TOKEN
- You receive notification
- You manually close and reopen the PR
- This triggers validation workflows

**This is the only truly secretless option**, but it defeats the purpose of automation.

## Conclusion

**Storing the GitHub App private key in environment secrets is:**
- ✅ The most practical solution
- ✅ Industry-standard practice
- ✅ Reasonably secure with GitHub's encryption
- ✅ Better than PAT alternatives
- ✅ Significantly more secure than self-managed credential storage

**The risk of leakage is low** because:
- GitHub Secrets are encrypted and access-controlled
- The key is only used momentarily to generate tokens
- Tokens are short-lived (1 hour)
- App is scoped to one repository
- Activity is logged and auditable

**Your concerns are valid**, but this is the best available solution given GitHub's platform constraints.
