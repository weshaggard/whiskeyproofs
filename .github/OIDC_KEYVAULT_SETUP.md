# OIDC + Key Vault Setup for Enhanced Security

**🔒 Most Secure: Private key never leaves your cloud provider!**

This guide explains how to use OIDC with cloud key vaults to avoid storing the GitHub App private key in GitHub Secrets.

## The Enhanced Security Approach

### What You're Concerned About:
- Storing private key in GitHub Secrets
- Private key being downloaded to runner
- Risk of key leakage

### The OIDC + Key Vault Solution:
✅ Private key stored in **Azure Key Vault** or **AWS Secrets Manager**  
✅ Workflow authenticates via **OIDC** (no cloud credentials in GitHub!)  
✅ For Azure: Key Vault **signs JWT remotely** - key never downloaded  
✅ For AWS: Key retrieved at runtime from AWS (still more secure than GitHub)  
✅ Audit trail in cloud provider logs  

## Option A: Azure Key Vault with Remote Signing (Recommended)

### How It Works

```
┌─────────────────┐
│ GitHub Actions  │
│   Workflow      │
└────────┬────────┘
         │ 1. Authenticate via OIDC
         │    (no static credentials!)
         ▼
┌─────────────────┐
│  Azure OIDC     │
│   Provider      │
└────────┬────────┘
         │ 2. Get temporary Azure token
         ▼
┌─────────────────┐       ┌──────────────────┐
│ Workflow builds │       │  Azure Key Vault │
│  unsigned JWT   │──────▶│  Signs JWT with  │
│  (header.payload)│  3.   │  private key     │
└─────────────────┘ Sign  │  (key stays in   │
         ▲                 │   Azure!)        │
         │ 4. Signature    └──────────────────┘
         │    returned
         │
         ▼
┌─────────────────┐
│ Complete JWT    │
│ (header.payload │
│  .signature)    │
└────────┬────────┘
         │ 5. Call GitHub API
         ▼
┌─────────────────┐
│  GitHub API     │
│ Returns access  │
│ token for PR    │
└─────────────────┘
```

**Key Security Benefit:** The private key **never leaves Azure Key Vault**. The signing happens in the vault using the `sign` API.

### What You Need

**Azure Resources:**
- Azure subscription (free tier works)
- Azure Key Vault (Premium tier for HSM-backed keys recommended)
- Azure AD App Registration (for OIDC federation)

**Cost:** ~$1-2/month for Key Vault + minimal signing operation costs

### High-Level Setup Steps

1. **Import GitHub App private key into Azure Key Vault** as a key (not secret)
2. **Configure OIDC federation** between GitHub Actions and Azure
3. **Grant signing permission** (NOT get/download permission) to the service principal
4. **Workflow authenticates** to Azure via OIDC
5. **Workflow builds unsigned JWT** (header + payload)
6. **Workflow calls Key Vault sign API** with the JWT digest
7. **Key Vault returns signature** (without exposing private key)
8. **Workflow completes the JWT** and exchanges it for GitHub token

### Required GitHub Secrets (in 'automation' environment)

- `AZURE_CLIENT_ID` - App registration client ID
- `AZURE_TENANT_ID` - Azure AD tenant ID
- `AZURE_SUBSCRIPTION_ID` - Azure subscription ID
- `AZURE_KEYVAULT_NAME` - Name of your Key Vault
- `AZURE_KEYVAULT_KEY_NAME` - Name of the key in vault
- `GITHUB_APP_ID` - Your GitHub App ID

**No APP_PRIVATE_KEY secret needed!**

### Resources for Implementation

- **Microsoft Learn:** [Use Azure Key Vault in GitHub Actions](https://learn.microsoft.com/en-us/azure/developer/github/github-actions-key-vault)
- **Detailed tutorial:** [Signing JWTs with Azure Key Vault](https://manbearpiet.com/posts/signing-jwt/)
- **Python example:** [GitHub Gist - JWT with Key Vault](https://gist.github.com/davidzenisu/a33c2344aa2bb48074f1ec61773b8ec0)
- **GitHub Docs:** [OIDC in Azure](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-azure)

---

## Option B: AWS Secrets Manager with OIDC

### How It Works

```
┌─────────────────┐
│ GitHub Actions  │
│   Workflow      │
└────────┬────────┘
         │ 1. Authenticate via OIDC
         │    (no AWS credentials!)
         ▼
┌─────────────────┐
│  AWS STS OIDC   │
│   Provider      │
└────────┬────────┘
         │ 2. Get temporary AWS credentials
         ▼
┌─────────────────┐
│ Workflow calls  │
│ Secrets Manager │
└────────┬────────┘
         │ 3. Retrieve private key
         │    (encrypted in transit)
         ▼
┌─────────────────┐
│ Generate JWT    │
│ locally on      │
│ runner          │
└────────┬────────┘
         │ 4. Exchange JWT for token
         ▼
┌─────────────────┐
│  GitHub API     │
│ Returns token   │
└─────────────────┘
```

**Security Note:** The private key IS downloaded to the runner (like GitHub Secrets), but:
- Stored in AWS (better audit logging)
- Retrieved via OIDC (no static AWS credentials)
- Can use AWS KMS encryption
- Better for compliance/auditing requirements

### What You Need

**AWS Resources:**
- AWS account
- AWS Secrets Manager secret
- IAM OIDC provider for GitHub
- IAM role with appropriate trust policy

**Cost:** ~$0.40/month + $0.05 per 10,000 retrievals

### High-Level Setup Steps

1. **Store GitHub App private key** in AWS Secrets Manager
2. **Configure OIDC provider** for GitHub in IAM
3. **Create IAM role** with federated trust for your repository
4. **Grant GetSecretValue permission** to the role
5. **Workflow authenticates** to AWS via OIDC
6. **Workflow retrieves private key** from Secrets Manager
7. **Workflow generates token** using standard GitHub App action

### Required GitHub Secrets (in 'automation' environment)

- `AWS_ROLE_ARN` - ARN of the IAM role for OIDC
- `GITHUB_APP_ID` - Your GitHub App ID

**No APP_PRIVATE_KEY secret needed!**

### Resources for Implementation

- **AWS Docs:** [Use Secrets Manager in GitHub](https://docs.aws.amazon.com/secretsmanager/latest/userguide/retrieving-secrets_github.html)
- **GitHub Action:** [aws-secretsmanager-get-secrets](https://github.com/aws-actions/aws-secretsmanager-get-secrets)
- **AWS Blog:** [OIDC with GitHub Actions](https://aws.amazon.com/blogs/security/use-iam-roles-to-connect-github-actions-to-actions-in-aws/)
- **GitHub Docs:** [OIDC in AWS](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)

---

## Comparison: All Three Approaches

| Feature | GitHub Secrets | AWS Secrets Manager + OIDC | Azure Key Vault Sign + OIDC |
|---------|----------------|---------------------------|----------------------------|
| **Private key stored in** | GitHub Secrets | AWS Secrets Manager | Azure Key Vault (HSM) |
| **Key downloaded to runner?** | ✅ Yes | ✅ Yes | ❌ **No** (signs remotely) |
| **Authentication method** | Built-in | OIDC (no credentials!) | OIDC (no credentials!) |
| **Static credentials in GitHub** | 1 secret | 0 secrets | 0 secrets |
| **Audit logging** | GitHub logs | AWS CloudTrail | Azure Monitor |
| **Key rotation complexity** | Update 1 secret | Update in AWS | Update in Azure |
| **Setup complexity** | Simple | Medium | Complex |
| **Monthly cost** | $0 | ~$0.40 | ~$1-2 |
| **Security level** | Good | Better | **Best** |
| **Compliance friendly** | Yes | More so | Most |

## My Recommendation

### For Maximum Security: **Azure Key Vault with Remote Signing**
**Best if:**
- Security is paramount
- You have or plan to use Azure
- You want true "key never leaves the vault" security
- You need strong audit/compliance requirements

**Setup time:** 1-2 hours (one-time)

### For Good Security + Simplicity: **GitHub Secrets** (Current)
**Best if:**
- You want it working quickly
- You don't have cloud infrastructure
- You trust GitHub's security model
- You need zero ongoing costs

**Setup time:** 15 minutes (already done!)

### For AWS Users: **AWS Secrets Manager + OIDC**
**Best if:**
- Already using AWS infrastructure
- Want better audit logging
- AWS compliance requirements
- Middle ground security/complexity

**Setup time:** 30-45 minutes

## Implementation Support

I can help you implement the OIDC + Key Vault approach if you'd like:

**For Azure:**
1. Create the helper scripts for JWT signing
2. Update the workflow configuration
3. Provide testing instructions

**For AWS:**
1. Update the workflow to use AWS Secrets Manager
2. Configure OIDC authentication
3. Provide testing instructions

**Or stick with GitHub Secrets:**
- Already working
- Good security with environment secrets
- Zero additional infrastructure
- Most cost-effective

Which approach would you like to pursue?
