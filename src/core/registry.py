import importlib.util
import os
import sys
from pathlib import Path
from sdk.tool_builder import get_registered_tools, get_registered_schemas

def load_all_extensions(extensions_dir: str):
    """
    Dynamically scan the extensions directory and import all .py files.
    This triggers the @register_tool decorators inside the files.
    """
    ext_path = Path(extensions_dir).resolve()
    
    if not ext_path.exists():
        return
        
    for root, dirs, files in os.walk(ext_path):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                full_path = Path(root) / file
                module_name = f"extensions.{full_path.stem}"
                
                # Dynamic import
                spec = importlib.util.spec_from_file_location(module_name, full_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    try:
                        spec.loader.exec_module(module)
                    except Exception as e:
                        print(f"Failed to load extension {file}: {e}")

def get_tools_and_schemas():
    """Return the populated tool map and schema array."""
    return get_registered_tools(), get_registered_schemas()
