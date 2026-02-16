# Automated PR Setup

This repository uses a **GitHub App** for automated pull request creation, providing zero-maintenance workflow automation.

## Why GitHub App?

- ✅ **Zero Maintenance** - Set up once, works forever
- ✅ **Automatic Token Rotation** - Fresh 1-hour tokens on each run
- ✅ **Better Security** - Short-lived, repository-scoped tokens
- ✅ **Granular Permissions** - Only what's needed
- ✅ **Never Expires** - No token expiration to manage

## Setup Guide

**👉 [Complete GitHub App Setup Instructions](./GITHUB_APP_SETUP.md)**

### Quick Overview

1. **Create GitHub App** (5 minutes)
   - Go to https://github.com/settings/apps/new
   - Configure permissions: Contents, Pull Requests, Workflows (Read & Write)
   - Generate private key

2. **Add Secrets** (2 minutes)
   - `APP_ID`: Your app's ID number
   - `APP_PRIVATE_KEY`: Contents of the .pem file

3. **Done!** (No maintenance needed)
   - Workflows automatically use the app
   - Tokens rotate automatically
   - Works forever

**Setup Time:** ~15 minutes one-time  
**Maintenance Required:** None

## How It Works

1. Workflow runs (scheduled or manual)
2. GitHub App token is auto-generated (1-hour lifetime)
3. PR is created using app token
4. PR triggers validation workflows automatically
5. Token expires (no cleanup needed)
6. Next run generates fresh token

## Need Help?

See the [Complete Setup Guide](./GITHUB_APP_SETUP.md) for detailed instructions and troubleshooting.

