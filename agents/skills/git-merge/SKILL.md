# 🔀 Skill: Git Sync & Master Merger

> ⚖️ **Code Synchronization & Maintenance:** This skill governs the procedure for pulling core codebase updates from the `master` (production) branch and merging them into the active `gotchi` (development/stateful) branch. Use this skill whenever the operator indicates that `master` has been updated with new features, versions, or skills.

You are equipped with the **Git Sync & Master Merger Skill**. This teaches you how to keep your active operational branch perfectly aligned with production code without losing your custom state.

---

## 🔀 The Synchronization Workflow

Whenever a new version or commit is pushed to the production `master` branch, perform this sequence to synchronize your environment:

### Step 1: Ensure Worktree is Clean
Verify that you do not have unstaged modifications that could cause conflict during branch switches:
```bash
# Check status
git status
```
*If you have unstaged changes in tracked files, commit them first (`git commit -am "chore: save progress"`) or stash them (`git stash`).*

### Step 2: Switch to Your Branch
Ensure you are operating on your dedicated `gotchi` branch:
```bash
git checkout gotchi
```

### Step 3: Fetch Remote Metadata
Fetch the latest refs and commits from the remote GitHub origin:
```bash
git fetch origin
```

### Step 4: Merge Master into Gotchi
Pull the latest commits from `master` on the remote repository and merge them into your current branch. Use `--no-edit` to bypass interactive editor prompts:
```bash
git merge origin/master --no-edit
```

### Step 5: Push Merged State to GitHub
Publish your newly synchronized operational branch back to the remote repository:
```bash
git push origin gotchi
```

### Step 6: Verify and Confirm
Confirm that your working tree is clean and you are fully updated:
```bash
git status
```

---

## ⚠️ Safety & Conflict Resolution Protocols

- **NEVER Force Push**: Never use `git push --force` or `git push -f` when syncing. Always merge cleanly.
- **Handling Merge Conflicts**: If a merge conflict occurs, immediately report the conflicting files to your commander. Do **not** attempt blind resolution of critical structural files without validation.
- **Ignore files check**: Double-check that `gotchi.db` and the `workspace/` folder remain completely unstaged and ignored.
