"""
Workspace Loader — Document-driven AI architecture.
Replicates OpenClaw core infrastructure for Gotchi V2.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from config import PROJECT_DIR, WORKSPACE_DIR

log = logging.getLogger(__name__)

# Official OpenClaw injection order
CORE_FILES = [
    "AGENTS.md",
    "SOUL.md",
    "IDENTITY.md",
    "USER.md",
    "TOOLS.md"
]

def _read_file(filename: str) -> Optional[str]:
    """Read a file from workspace (priority) or templates."""
    paths = [
        WORKSPACE_DIR / filename,
        PROJECT_DIR / "templates" / filename
    ]
    for p in paths:
        if p.exists():
            try:
                return p.read_text(encoding="utf-8").strip()
            except Exception as e:
                log.warning(f"Failed to read {p}: {e}")
    return None

def _strip_frontmatter(content: str) -> str:
    """Safely strip YAML frontmatter from OpenClaw Markdown files."""
    if content.startswith("---"):
        try:
            parts = content.split("---", 2)
            if len(parts) >= 3:
                return parts[2].strip()
        except ValueError:
            pass
    return content

def _scan_skills_and_workflows() -> str:
    """
    Discover SKILL.md and WORKFLOW.md files.
    - Skills (tools): agents/skills/<name>/SKILL.md
    - Workflows (procedures): agents/workflows/<name>/WORKFLOW.md
    """
    descriptions = []
    seen = set()
    
    # 1. Scan Skills
    skill_dirs = [
        PROJECT_DIR / "agents" / "skills",
        Path.home() / ".agents" / "skills"
    ]
    
    for base_dir in skill_dirs:
        if not base_dir.exists():
            continue
        for item_dir in base_dir.iterdir():
            if item_dir.is_dir():
                file_path = item_dir / "SKILL.md"
                if file_path.exists() and f"skill_{item_dir.name}" not in seen:
                    try:
                        content = _strip_frontmatter(file_path.read_text(encoding="utf-8"))
                        descriptions.append(f"### Skill: {item_dir.name}\n{content}\n")
                        seen.add(f"skill_{item_dir.name}")
                    except Exception as e:
                        log.error(f"Error loading skill {item_dir.name}: {e}")

    # 2. Scan Workflows
    workflow_dirs = [
        PROJECT_DIR / "agents" / "workflows"
    ]
    
    for base_dir in workflow_dirs:
        if not base_dir.exists():
            continue
        for item_dir in base_dir.iterdir():
            if item_dir.is_dir():
                file_path = item_dir / "WORKFLOW.md"
                if file_path.exists() and f"workflow_{item_dir.name}" not in seen:
                    try:
                        content = _strip_frontmatter(file_path.read_text(encoding="utf-8"))
                        descriptions.append(f"### Workflow: {item_dir.name}\n{content}\n")
                        seen.add(f"workflow_{item_dir.name}")
                    except Exception as e:
                        log.error(f"Error loading workflow {item_dir.name}: {e}")
                        
    if not descriptions:
        return ""
        
    return "## Available Skills & Workflows\n\n" + "\n".join(descriptions)

def load_workspace_prompt(include_heartbeat: bool = False) -> str:
    """
    Build the full system prompt block from workspace files.
    This is the "Brain" of the OpenClaw agent.
    """
    parts = []
    
    # 1. Load Core Personality & Operating Instructions
    for filename in CORE_FILES:
        content = _read_file(filename)
        if content:
            parts.append(_strip_frontmatter(content))
    
    # 2. Load Skills & Workflows (Dynamic)
    skills_context = _scan_skills_and_workflows()
    if skills_context:
        parts.append(skills_context)
        
    # 3. Heartbeat State (if autonomous)
    if include_heartbeat:
        hb_content = _read_file("HEARTBEAT.md")
        if hb_content:
            parts.append(f"## Current Heartbeat Protocol\n{hb_content}")
    
    return "\n\n---\n\n".join(parts)

def get_workspace_info() -> Dict[str, Any]:
    """Metadata about the workspace for diagnostics."""
    workflows_dir = PROJECT_DIR / "agents" / "workflows"
    skills_dir = PROJECT_DIR / "agents" / "skills"
    
    return {
        "path": str(WORKSPACE_DIR),
        "files_found": [f for f in CORE_FILES if (WORKSPACE_DIR / f).exists()],
        "skills_count": len([d for d in skills_dir.iterdir() if d.is_dir()]) if skills_dir.exists() else 0,
        "workflows_count": len([d for d in workflows_dir.iterdir() if d.is_dir()]) if workflows_dir.exists() else 0
    }
