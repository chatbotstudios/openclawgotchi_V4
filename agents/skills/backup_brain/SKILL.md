# Skill: Backup Brain
## Type: Administration
## Trigger: When the user asks you to back up your brain, save your memories to the cloud, OR asks you to merge/push/update the remote `gotchi` branch (e.g. "pull master and merge to your branch gotchi").

# Overview
You have a special headless backup script that allows you to safely commit and force-push your ignored databases and daily memory logs to your remote `gotchi` branch without corrupting the `master` codebase branch. Because it force-pushes, it naturally overrides any diverged Git history, making it completely resilient to code updates.

# Instructions
1. If the user requests a backup, use your `execute_bash` or `run_cli` tool to run the backup script.
2. The script is located at the root of the project: `./backup_brain.sh`
3. Execute the script and wait for the results.
4. Report back to the user that your memories have been safely synchronized to the cloud!
