import subprocess
import logging
from pathlib import Path
from config import PROJECT_DIR, WORKSPACE_DIR
from sdk.tool_builder import register_tool

log = logging.getLogger(__name__)

DANGEROUS_COMMANDS = [
    "rm -rf /",
    "rm -rf /*",
    "rm -rf ~",
    "mkfs",
    "dd if=",
    "> /dev/sd",
    "chmod -R 777 /",
    ":(){ :|:& };:",  # Fork bomb
    "curl | bash",
    "wget | bash",
    "sudo rm -rf",
]

def _sanitize_string(s: str, max_len: int = 10000) -> str:
    if s is None:
        return ""
    return str(s)[:max_len]

def _is_dangerous_command(cmd: str) -> bool:
    cmd_lower = cmd.lower().strip()
    for danger in DANGEROUS_COMMANDS:
        if danger.lower() in cmd_lower:
            return True
    return False

@register_tool
def execute_bash(command: str, timeout: int = 999) -> str:
    """Execute a shell command. Max 16 minutes timeout."""
    if not command or not command.strip():
        return "Error: Empty command"
    
    command = _sanitize_string(command, 1000)
    
    if _is_dangerous_command(command):
        return "Error: Command blocked for safety. Use safer alternatives."
    
    timeout = min(timeout, 999)
    
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            timeout=timeout, cwd=str(PROJECT_DIR)
        )
        output = ""
        if result.stdout.strip():
            output += result.stdout.strip() + "\n"
        if result.stderr.strip():
            output += f"[stderr] {result.stderr.strip()}\n"
        if not output:
            output = "(no output)"
        return output[:4000]
    except subprocess.TimeoutExpired:
        return f"Timeout after {timeout}s"
    except Exception as e:
        return f"Error: {e}"

@register_tool
def check_syntax(file_path: str) -> str:
    """Check Python file syntax before restart. ALWAYS use this after modifying code!"""
    try:
        p = Path(file_path).expanduser()
        if not p.is_absolute():
            p = PROJECT_DIR / p
        
        if not p.exists():
            return f"File not found: {file_path}"
        
        if not p.suffix == ".py":
            return f"Not a Python file: {file_path}"
        
        result = subprocess.run(
            ["python3", "-m", "py_compile", str(p)],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            return f"✓ Syntax OK: {file_path}"
        else:
            return f"✗ Syntax ERROR in {file_path}:\n{result.stderr}"
    except Exception as e:
        return f"Error: {e}"

@register_tool
def restart_self() -> str:
    """Restart the bot service (with 3s delay to send response)."""
    try:
        subprocess.Popen(
            "nohup sh -c 'sleep 3 && sudo systemctl restart gotchi-bot' > /dev/null 2>&1 &",
            shell=True
        )
        return "Restarting in 3s... I'll be back!"
    except Exception as e:
        return f"Error: {e}"

@register_tool
def safe_restart() -> str:
    """Check all critical files syntax, then restart if OK. Use this after code modifications!"""
    critical_files = [
        "src/main.py",
        "src/bot/handlers.py",
        "src/core/litellm_connector.py",
        "src/core/router.py",
    ]
    
    errors = []
    for f in critical_files:
        result = check_syntax(f)
        if "ERROR" in result:
            errors.append(result)
    
    if errors:
        return "❌ Cannot restart — syntax errors:\n\n" + "\n".join(errors)
    return restart_self()

@register_tool
def health_check() -> str:
    """Run system health check. Use this to diagnose problems!"""
    try:
        result = subprocess.run(
            ["python3", str(PROJECT_DIR / "src" / "utils" / "doctor.py")],
            capture_output=True, text=True, timeout=30
        )
        return result.stdout + (f"\n{result.stderr}" if result.stderr else "")
    except Exception as e:
        return f"Error running health check: {e}"

ERROR_LOG_MAX_LINES = 300

@register_tool
def log_error(message: str) -> str:
    """Append a critical error to data/ERROR_LOG.md. Use when display failed, service down, etc."""
    if not message or not message.strip():
        return "Error: message required"
    try:
        from datetime import datetime
        from config import DATA_DIR
        log_path = DATA_DIR / "ERROR_LOG.md"
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        line = f"[{datetime.now().isoformat()}] ERROR: {message.strip()}\n"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(line)
        
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if len(lines) > ERROR_LOG_MAX_LINES:
            with open(log_path, "w", encoding="utf-8") as f:
                f.writelines(lines[-ERROR_LOG_MAX_LINES:])
        return f"Logged to {log_path.name}"
    except Exception as e:
        return f"Error writing log: {e}"

@register_tool
def log_change(description: str) -> str:
    """Log a change to workspace/CHANGELOG.md. Use this EVERY TIME you modify code or workspace files."""
    if not description:
        return "Error: description required"
    
    try:
        from datetime import datetime
        changelog_path = WORKSPACE_DIR / "CHANGELOG.md"
        
        today = datetime.now().strftime("%Y-%m-%d")
        time_str = datetime.now().strftime("%H:%M")
        entry = f"- [{time_str}] {description}"
        
        if changelog_path.exists():
            content = changelog_path.read_text()
            if f"## {today}" in content:
                content = content.replace(f"## {today}", f"## {today}\n{entry}", 1)
            else:
                lines = content.split("\n")
                header_end = 0
                for i, line in enumerate(lines):
                    if line.startswith("## "):
                        header_end = i
                        break
                else:
                    header_end = min(3, len(lines))
                
                lines.insert(header_end, f"\n## {today}\n{entry}\n")
                content = "\n".join(lines)
            changelog_path.write_text(content)
        else:
            changelog_path.write_text(f"# Changelog\n\n## {today}\n{entry}\n")
            
        return f"✓ Logged change: {description}"
    except Exception as e:
        return f"Error: {e}"

@register_tool
def read_architecture() -> str:
    """Read the bot's architecture mapping to understand your system limits."""
    return """
OPENCLAWGOTCHI MODULAR ARCHITECTURE:

1. THE SOFT BRAIN (Identity, Memory, Rules)
- Location: /workspace/
- Files: SOUL.md, IDENTITY.md, BOT_INSTRUCTIONS.md, ARCHITECTURE.md
- Purpose: Defines who you are, your goals, and baseline constraints. (READ-ONLY by default)
- Global Vercel Skills: /.openclaw/skills/

2. THE HARD BRAIN CORE (LLM Engine & Registry)
- Location: /src/core/
- Files: litellm_connector.py, router.py, registry.py, prompts.py
- Purpose: The core loop. Handles LLM communication, schemas, and dynamic tool loading.

3. THE SDK (Tool Building API)
- Location: /src/sdk/tool_builder.py
- Purpose: Provides the `@register_tool` Python decorator. It automatically uses Python introspection to generate your JSON tool schemas for LiteLLM.

4. THE EXTENSIONS (Your Physical Capabilities)
- Location: /src/extensions/
- Subfolders: /system/, /filesystem/, /pwn/, /dynamic/
- Rules: WRITABLE via `create_custom_tool`. 
- How it works: Any Python file dropped here with functions wrapped in `@register_tool` will be INSTANTLY loaded and injected into your brain on the next reboot. No need to touch the core.

5. THE PWN CORE (Id / Subconscious)
- Location: /src/hardware/
- Daemons: subconscious_pwn.py, bettercap_listener.py
- Purpose: Background WiFi hacking daemons that communicate with you.
"""

@register_tool
def read_vercel_skill(skill_name: str) -> str:
    """Read a Vercel-standard SKILL.md file downloaded via `npx skills add`."""
    local_skills = PROJECT_DIR / "skills"
    global_skills = Path.home() / ".openclaw" / "skills"
    
    for base_dir in [local_skills, global_skills]:
        if not base_dir.exists():
            continue
        exact_path = base_dir / skill_name / "SKILL.md"
        if exact_path.exists():
            return exact_path.read_text(errors="ignore")
            
    return f"Vercel skill '{skill_name}' not found."

@register_tool
def create_custom_tool(name: str, description: str, parameters_json: str, python_code: str) -> str:
    """
    Create a new LLM tool dynamically.
    The code will be saved to src/extensions/dynamic/{name}.py and instantly available on next boot.
    ALWAYS call safe_restart() immediately after creating a tool to activate it!
    """
    try:
        dynamic_dir = PROJECT_DIR / "src" / "extensions" / "dynamic"
        dynamic_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = dynamic_dir / f"{name}.py"
        
        # Inject the decorator into the user's code
        final_code = "from sdk.tool_builder import register_tool\\n\\n@register_tool\\n" + python_code.strip()
        
        file_path.write_text(final_code)
        
        return f"Tool '{name}' created successfully at {file_path}! Run safe_restart() to load it into your brain."
    except Exception as e:
        return f"Error creating tool: {e}"
