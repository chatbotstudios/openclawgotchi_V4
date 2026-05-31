import logging
from pathlib import Path
from config import PROJECT_DIR
from sdk.tool_builder import register_tool

log = logging.getLogger(__name__)

# Protected files (cannot be written/deleted)
PROTECTED_FILES = [
    ".env",
    "gotchi.db",
    "src/drivers/",  # Hardware drivers
    "src/ui/",       # E-Ink UI (critical display stack)
    "src/ui/gotchi_ui.py",
]

MAX_WRITE_SIZE = 100 * 1024

def _is_protected_path(path: Path) -> bool:
    path_str = str(path)
    for protected in PROTECTED_FILES:
        if protected in path_str:
            return True
    return False

@register_tool
def read_file(path: str) -> str:
    """Read the contents of a file. Essential for analyzing code and logs."""
    if not path or not path.strip():
        return "Error: Empty path"
    
    try:
        p = Path(path).expanduser()
        if not p.is_absolute():
            p = PROJECT_DIR / p
        p = p.resolve()
        
        if not p.exists():
            return f"File not found: {path}"
        if p.stat().st_size > 100 * 1024:
            return "File too large (>100KB). Read in chunks or use execute_bash with head/tail."
        
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return f"Error: {e}"

@register_tool
def write_file(path: str, content: str) -> str:
    """Write content to a file (automatically backs up the existing file)."""
    if not path or not path.strip():
        return "Error: Empty path"
    if content is None:
        return "Error: Content is None"
    
    if len(content) > MAX_WRITE_SIZE:
        return f"Error: Content too large ({len(content)} bytes). Max is {MAX_WRITE_SIZE}."
    
    try:
        p = Path(path).expanduser()
        if not p.is_absolute():
            p = PROJECT_DIR / p
        p = p.resolve()
        
        if _is_protected_path(p):
            return f"Error: Cannot write to protected file: {path}"
        
        p.parent.mkdir(parents=True, exist_ok=True)
        
        if p.exists():
            import shutil
            backup_path = p.with_suffix(p.suffix + ".bak")
            shutil.copy2(p, backup_path)
            log.info(f"Backup created: {backup_path}")
        
        p.write_text(content, encoding="utf-8")
        return f"✓ Wrote {len(content)} bytes to {path}"
    except Exception as e:
        return f"Error: {e}"

@register_tool
def list_directory(path: str = ".") -> str:
    """List directory contents (single level)."""
    try:
        p = Path(path).expanduser()
        if not p.is_absolute():
            p = PROJECT_DIR / p
        p = p.resolve()
        
        if not p.exists():
            return f"Not found: {path}"
        if not p.is_dir():
            return f"Not a directory: {path}"
        
        items = []
        for item in sorted(p.iterdir()):
            suffix = "/" if item.is_dir() else ""
            items.append(f"  {item.name}{suffix}")
        
        return f"{p}/\n" + "\n".join(items) if items else f"{p}/ (empty)"
    except Exception as e:
        return f"Error: {e}"

@register_tool
def list_tree(path: str = ".", max_depth: int = 3) -> str:
    """List directory contents recursively (tree structure). Essential for analyzing workspaces or seeing nested files."""
    try:
        p = Path(path).expanduser()
        if not p.is_absolute():
            p = PROJECT_DIR / p
        p = p.resolve()
        
        if not p.exists():
            return f"Not found: {path}"
        if not p.is_dir():
            return f"Not a directory: {path}"
            
        tree = []
        ignore = {".git", "__pycache__", ".venv", "venv", "node_modules", ".pytest_cache"}
        
        def walk_dir(current_path, prefix="", depth=0):
            if depth > max_depth:
                return
                
            try:
                items = sorted([item for item in current_path.iterdir() if item.name not in ignore])
            except PermissionError:
                return
                
            for i, item in enumerate(items):
                is_last = (i == len(items) - 1)
                connector = "└── " if is_last else "├── "
                
                if item.is_dir():
                    tree.append(f"{prefix}{connector}{item.name}/")
                    extension = "    " if is_last else "│   "
                    walk_dir(item, prefix + extension, depth + 1)
                else:
                    tree.append(f"{prefix}{connector}{item.name}")
                    
        tree.append(f"{p.name}/")
        walk_dir(p)
        
        return "\n".join(tree)
    except Exception as e:
        return f"Error generating tree: {e}"

@register_tool
def restore_from_backup(file_path: str) -> str:
    """Restore a file from its .bak backup. Use this if you broke something!"""
    if not file_path:
        return "Error: file_path required"
    
    try:
        p = Path(file_path).expanduser()
        if not p.is_absolute():
            p = PROJECT_DIR / p
        p = p.resolve()
        
        backup = p.with_suffix(p.suffix + ".bak")
        
        if not backup.exists():
            return f"No backup found: {backup}"
        
        import shutil
        shutil.copy2(backup, p)
        return f"✓ Restored {file_path} from backup"
    except Exception as e:
        return f"Error: {e}"
