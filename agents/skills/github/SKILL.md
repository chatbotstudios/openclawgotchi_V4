---
name: github
description: 'GitHub integration skill for repository management, remote operations, and CI/CD using AGENT_GITHUB_PAT. Use when user wants to push code, manage branches, work with remotes, create repos, or automate GitHub operations. Supports: (1) Git remote auth with PAT, (2) Branch management, (3) Push/pull operations, (4) Repo creation via API, (5) CI/CD workflow management'
license: MIT
allowed-tools: Bash, execute_bash, git_command
---

# GitHub Operations with PAT Authentication

## Overview

This skill enables autonomous GitHub operations using a Personal Access Token (PAT) stored in `AGENT_GITHUB_PAT` from `.env`. It provides secure remote authentication and repository management without manual SSH key setup.

## Authentication

### Reading the PAT

```bash
# The PAT is loaded from .env at runtime
# grep AGENT_GITHUB_PAT .env | cut -d'=' -f2
```

### Configure Remote with PAT

```bash
# Universal pattern — embeds PAT into the remote URL
git remote set-url origin https://${AGENT_GITHUB_PAT}@github.com/${GITHUB_USER}/${GITHUB_REPO}.git

# Check it stuck
git remote -v
```

**⚠️ CRITICAL:** Never echo/display the PAT value in chat, logs, or responses. Use `${AGENT_GITHUB_PAT}` in bash commands only.

## Core Workflows

### 1. Push Changes to Existing Branch

```bash
# Stage everything
git add -A

# Commit
git commit -m "type(scope): description"

# Push current branch to origin
git push origin $(git rev-parse --abbrev-ref HEAD)
```

### 2. Create & Push a New Branch

```bash
# Ensure we're on the source branch
git checkout main

# Create and switch to new branch
git checkout -b feat/my-new-feature

# Make changes, commit, push
git add -A
git commit -m "feat: add new thing"
git push origin feat/my-new-feature
```

### 3. Check Remote Status

```bash
# See if local is ahead/behind
git status
git log --oneline -5
git rev-parse --abbrev-ref HEAD
```

### 4. Create a GitHub Repo from CLI

```bash
# Using GitHub API (requires repo scope on PAT)
curl -s -H "Authorization: token ${AGENT_GITHUB_PAT}" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d '{"name":"repo-name","description":"description","private":false}'
```

### 5. List Remote Branches

```bash
# List all branches including remote
git branch -a

# Check what's on remote that we don't have locally
git remote show origin
```

## Branch Naming Conventions

Use conventional commit prefixes for branch names:

| Prefix | Purpose | Example |
|--------|---------|---------|
| `feat/` | New features | `feat/ble-hunter-skill` |
| `fix/` | Bug fixes | `fix/e-ink-ghosting` |
| `chore/` | Maintenance | `chore/cleanup-logs` |
| `docs/` | Documentation | `docs/github-skill` |
| `refactor/` | Code restructuring | `refactor/tool-loader` |
| `experiment/` | Research/testing | `experiment/pinecone-vector` |

## Safety Protocols

- **NEVER** display the PAT value in any output
- **NEVER** commit `.env` files or hardcoded tokens
- Use `git push --force` only when explicitly authorized
- Verify the correct remote URL before pushing
- Check that the branch name is correct before push
- Confirm with user before creating public repos

## Example: Quick Push Sequence

```bash
# 1. Verify current state
git status

# 2. Set remote with PAT auth
git remote set-url origin https://${AGENT_GITHUB_PAT}@github.com/${GITHUB_USER}/${GITHUB_REPO}.git

# 3. Stage and commit
git add -A
git commit -m "feat: add github skill for remote operations"

# 4. Push silently
git push origin gotchi
```

## Environmental Variables

| Variable | Source | Purpose |
|----------|--------|---------|
| `AGENT_GITHUB_PAT` | `.env` | GitHub Personal Access Token |
| `GITHUB_USER` | Context/User | GitHub username (ask if unknown) |
| `GITHUB_REPO` | Context/User | Repository name (ask if unknown) |

## Getting GITHUB_USER and GITHUB_REPO

```bash
# Get GitHub username from the API
curl -s -H "Authorization: token ${AGENT_GITHUB_PAT}" \
  https://api.github.com/user | python3 -c "import sys,json; print(json.load(sys.stdin).get('login','unknown'))"

# Get origin remote URL info
git remote get-url origin
```
