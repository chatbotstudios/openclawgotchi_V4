import json
from core.registry import load_all_extensions, get_tools_and_schemas
from config import PROJECT_DIR

load_all_extensions(str(PROJECT_DIR / "src" / "extensions"))
_, schemas = get_tools_and_schemas()
print(json.dumps(schemas, indent=2))
