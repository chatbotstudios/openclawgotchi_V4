import json

from config import PROJECT_DIR
from core.registry import get_tools_and_schemas, load_all_extensions

load_all_extensions(str(PROJECT_DIR / "src" / "extensions"))
_, schemas = get_tools_and_schemas()
print(json.dumps(schemas, indent=2))
