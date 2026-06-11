#!/bin/bash
# ==============================================================================
# 🧠 Autonomous Brain Backup (Headless Protocol)
# ==============================================================================
# This script forcefully tracks ignored DB/Memory files, pushes a snapshot 
# to the remote 'gotchi' branch, and softly unwinds the local commit so the 
# Pi can safely remain on the 'master' branch at all times.
# ==============================================================================

set -e

echo "[+] Initiating Autonomous Brain Backup..."

# 1. Ensure we are on master and the tree is clean (except for ignored files)
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "master" ]; then
    echo "[-] Error: You must be on the 'master' branch to run the headless backup."
    exit 1
fi

# 2. Force-add the normally ignored brain files
echo "[+] Forcing addition of ignored database and memory logs..."
git add -f gotchi.db templates/memory/ templates/knowledge/ handshakes/ pcaps/ data/cron_jobs.json 2>/dev/null || true

# Check if there's actually anything to commit
if git diff --staged --quiet; then
    echo "[!] No new memories to backup."
    exit 0
fi

# 3. Create the ephemeral commit
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
echo "[+] Creating snapshot commit..."
git commit -m "🧠 Autonomous Brain Backup: $TIMESTAMP"

# 4. Push directly to the remote 'gotchi' branch
echo "[+] Pushing snapshot to remote 'gotchi' branch..."
git push origin HEAD:gotchi

# 5. Unwind the commit locally
echo "[+] Unwinding local snapshot to restore clean master..."
git reset HEAD~1

echo "[+] Backup Complete! Your brain is safe in the cloud. ☁️"
