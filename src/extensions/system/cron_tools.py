from sdk.tool_builder import register_tool
from cron.scheduler import add_cron_job, list_cron_jobs, remove_cron_job

@register_tool
def get_system_time() -> str:
    """Returns the current system date and time in ISO format and human-readable format. Use this to orient yourself before setting reminders or cron jobs."""
    from datetime import datetime
    now = datetime.now()
    return f"ISO: {now.isoformat()}\nHuman: {now.strftime('%A, %B %d, %Y %I:%M %p')}"

@register_tool
def list_my_cron_jobs() -> str:
    """List all currently active cron jobs and reminders. Returns their IDs, names, intervals, and next run times."""
    jobs = list_cron_jobs()
    if not jobs:
        return "You have no active cron jobs or scheduled reminders."
    
    result = []
    for j in jobs:
        schedule = f"Every {j.interval_minutes}m" if j.interval_minutes > 0 else f"One-shot at {j.next_run}"
        typ = "[MSG]"
        if getattr(j, "bash_command", None): typ = "[BASH]"
        elif getattr(j, "python_script", None): typ = "[PY]"
        result.append(f"- ID: {j.id} | {typ} Name: {j.name} | Schedule: {schedule} | Target: {j.message or j.bash_command or 'python'}")
    
    return "Your active schedule:\n" + "\n".join(result)


@register_tool
def create_background_bash_task(name: str, interval_minutes: int, bash_command: str) -> str:
    """Create a recurring headless background bash loop that executes natively without pinging the LLM. Use this for reliable hardware/system operations like pinging networks or running tools."""
    if interval_minutes < 1:
        return "Error: interval_minutes must be at least 1."
    
    from cron.scheduler import add_cron_job
    job = add_cron_job(name=name, bash_command=bash_command, interval_minutes=interval_minutes)
    return f"Successfully created native bash background loop '{name}' (ID: {job.id}). It will execute '{bash_command}' silently every {interval_minutes} minutes."


@register_tool
def create_background_python_task(name: str, interval_minutes: int, python_code: str) -> str:
    """Create a recurring headless background python execution loop that runs natively. Use this to execute internal functions like pwn_ble_scan directly without pinging the LLM."""
    if interval_minutes < 1:
        return "Error: interval_minutes must be at least 1."
    
    from cron.scheduler import add_cron_job
    job = add_cron_job(name=name, python_script=python_code, interval_minutes=interval_minutes)
    return f"Successfully created native python background loop '{name}' (ID: {job.id}). It will execute the code silently every {interval_minutes} minutes."


@register_tool
def create_recurring_task(name: str, interval_minutes: int, message: str) -> str:
    """Create a recurring cron job that will ping you with a message at a set interval. Use this to continuously monitor something."""
    if interval_minutes < 1:
        return "Error: interval_minutes must be at least 1."
    
    job = add_cron_job(name=name, message=message, interval_minutes=interval_minutes)
    return f"Successfully created recurring task '{name}' (ID: {job.id}). I will remind you: '{message}' every {interval_minutes} minutes."


@register_tool
def create_reminder(name: str, run_at: str, message: str) -> str:
    """Create a one-shot reminder that will ping you once. 'run_at' accepts values like '30s' (30 seconds), '15m' (15 minutes), or '2h' (2 hours)."""
    if not run_at.endswith(("s", "m", "h")):
        return "Error: run_at must end with 's', 'm', or 'h' (e.g., '10m' for 10 minutes)."
    
    job = add_cron_job(name=name, message=message, run_at=run_at, delete_after_run=True)
    return f"Successfully set reminder '{name}' (ID: {job.id}). I will remind you: '{message}' in {run_at}."


@register_tool
def delete_cron_job(job_id: str) -> str:
    """Delete an active cron job or reminder by its ID. Use list_my_cron_jobs to find the ID first."""
    success = remove_cron_job(job_id)
    if success:
        return f"Successfully deleted job {job_id}."
    else:
        return f"Error: Could not find job with ID {job_id}. Did you type it correctly?"
