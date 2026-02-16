# Quick Start: Automated PR Setup

Choose your approach based on your needs:

## Option 1: GitHub App (Recommended) 🌟

**Best for:** Long-term use, teams, anyone who wants zero maintenance

**Pros:**
- ✅ **Zero maintenance** - Set up once, works forever
- ✅ Automatic token rotation (1-hour tokens)
- ✅ More secure (short-lived, granular permissions)
- ✅ Better audit logging

**Cons:**
- ⚠️ Slightly more complex initial setup (15 minutes)
- ⚠️ Requires admin access to create GitHub App

**Setup Time:** 15 minutes (one-time)  
**Maintenance:** None

**👉 [GitHub App Setup Guide](./GITHUB_APP_SETUP.md)**

---

## Option 2: Personal Access Token (PAT)

**Best for:** Quick setup, personal repos, temporary testing

**Pros:**
- ✅ Simple initial setup (5 minutes)
- ✅ No app creation needed

**Cons:**
- ❌ **Requires manual rotation every 90 days**
- ❌ Less secure (long-lived tokens)
- ❌ Broader permissions (user-scoped)
- ❌ Manual maintenance burden

**Setup Time:** 5 minutes (initial), 10 minutes every 90 days (rotation)  
**Maintenance:** Quarterly rotation required

**👉 [PAT Setup Guide](./AUTOMATED_PR_SETUP.md#setup-instructions-pat-method)**

---

## Quick Comparison

| Feature | GitHub App | PAT |
|---------|-----------|-----|
| **Initial Setup** | 15 min | 5 min |
| **Maintenance** | ✨ None | ⚠️ Every 90 days |
| **Token Lifetime** | 1 hour (auto-renews) | 90 days (manual) |
| **Security** | Higher | Lower |
| **Permissions** | Repository-scoped | User-scoped |
| **Audit Logging** | Detailed | Basic |
| **Recommended For** | Production use | Testing/personal |

---

## Decision Guide

**Choose GitHub App if:**
- ✅ You want zero maintenance
- ✅ You value security
- ✅ You're setting up for long-term use
- ✅ You work on a team
- ✅ You can spend 15 minutes on initial setup

**Choose PAT if:**
- ✅ You need something working in 5 minutes
- ✅ You're just testing
- ✅ You don't mind quarterly maintenance
- ✅ You can't create GitHub Apps (permission limits)

---

## Already Using PAT? Migrate to GitHub App

It's easy to migrate and worth it for zero maintenance:

1. **Set up GitHub App** (15 minutes) - [Guide](./GITHUB_APP_SETUP.md)
2. **Test it works** (5 minutes)
3. **Remove PAT** (1 minute)
4. **Done!** Never rotate tokens again

**Total migration time:** ~20 minutes for a lifetime of zero maintenance

---

## Need Help?

- **GitHub App Setup:** [GITHUB_APP_SETUP.md](./GITHUB_APP_SETUP.md)
- **PAT Setup:** [AUTOMATED_PR_SETUP.md](./AUTOMATED_PR_SETUP.md)
- **PAT Maintenance:** [PAT_MAINTENANCE.md](./PAT_MAINTENANCE.md)
- **Troubleshooting:** Check the relevant guide above
