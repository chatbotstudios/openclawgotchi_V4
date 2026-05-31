import subprocess
from sdk.tool_builder import register_tool
from config import PROJECT_DIR

@register_tool
def git_command(command: str) -> str:
    """Run a git command in the project repo. Use for status, log, diff, add, commit, branch, stash."""
    try:
        if command.startswith("git "):
            command = command[4:]
        from config import AGENT_GITHUB_PAT
        
        git_cmd_prefix = "git"
        if AGENT_GITHUB_PAT:
            # Tell git to transparently use the PAT for any https://github.com/ URLs
            git_cmd_prefix = f'git -c url."https://{AGENT_GITHUB_PAT}@github.com/".insteadOf="https://github.com/"'
        
        result = subprocess.run(
            f"{git_cmd_prefix} {command}", shell=True, capture_output=True, text=True,
            timeout=30, cwd=str(PROJECT_DIR)
        )
        output = ""
        if result.stdout.strip():
            output += result.stdout.strip() + "\n"
        if result.stderr.strip():
            output += f"[stderr] {result.stderr.strip()}\n"
        if not output:
            output = "(no output)"
        return output[:4000]
    except Exception as e:
        return f"Error: {e}"

@register_tool
def manage_service(service: str = "gotchi-bot", action: str = "status") -> str:
    """Manage systemd services. Actions: status, restart, stop, start, logs."""
    try:
        valid_actions = ["status", "restart", "stop", "start", "logs"]
        if action not in valid_actions:
            return f"Invalid action. Use: {', '.join(valid_actions)}"
            
        if action == "logs":
            cmd = f"sudo journalctl -u {service} -n 50 --no-pager"
        else:
            cmd = f"sudo systemctl {action} {service}"
            
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=10
        )
        
        output = (result.stdout + result.stderr).strip()
        return output or f"Service {service}: {action} done"
    except Exception as e:
        return f"Error: {e}"
