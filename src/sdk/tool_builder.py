import inspect
from typing import Callable, Dict, Any, get_type_hints

_TOOL_REGISTRY: Dict[str, Callable] = {}
_SCHEMA_REGISTRY: list[Dict[str, Any]] = []

def register_tool(func: Callable) -> Callable:
    """
    Decorator to register a function as an LLM tool.
    Automatically generates the OpenAI JSON schema from type hints and docstrings.
    """
    name = func.__name__
    doc = inspect.getdoc(func) or ""
    
    # First line of docstring is the tool description
    desc = doc.split("\n")[0] if doc else "No description provided."
    
    sig = inspect.signature(func)
    hints = get_type_hints(func)
    
    properties = {}
    required = []
    
    for param_name, param in sig.parameters.items():
        if param_name == "return":
            continue
            
        param_type = hints.get(param_name, str)
        type_str = "string"
        if param_type == int:
            type_str = "integer"
        elif param_type == bool:
            type_str = "boolean"
        elif param_type == float:
            type_str = "number"
        elif param_type == list or param_type == list[str]:
            type_str = "array"
            
        properties[param_name] = {
            "type": type_str
        }
        
        if type_str == "array":
            properties[param_name]["items"] = {"type": "string"}
        
        # If there is no default value, it's a required parameter
        if param.default == inspect.Parameter.empty:
            required.append(param_name)
            
    function_def = {
        "name": name,
        "description": desc,
    }
    
    if properties:
        param_def = {
            "type": "object",
            "properties": properties
        }
        if required:
            param_def["required"] = required
            
        function_def["parameters"] = param_def
        
    schema = {
        "type": "function",
        "function": function_def
    }
    
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        """Validation wrapper for LLM tool calls."""
        # If positional args are used, just pass them through (CLI usage)
        if args:
            return func(*args, **kwargs)
            
        # Sanitization & Type Validation (for LLM / kwargs usage)
        try:
            for param_name, param_type in hints.items():
                if param_name == 'return' or param_name not in kwargs:
                    continue
                
                val = kwargs[param_name]
                
                # Handle Basic Types
                if param_type == int and not isinstance(val, int):
                    try:
                        kwargs[param_name] = int(val)
                    except (ValueError, TypeError):
                        return f"Error: Parameter '{param_name}' must be an integer, got {type(val).__name__}."
                elif param_type == float and not isinstance(val, (float, int)):
                    try:
                        kwargs[param_name] = float(val)
                    except (ValueError, TypeError):
                        return f"Error: Parameter '{param_name}' must be a number, got {type(val).__name__}."
                elif param_type == bool and not isinstance(val, bool):
                    if str(val).lower() in ('true', '1', 'yes'):
                        kwargs[param_name] = True
                    elif str(val).lower() in ('false', '0', 'no'):
                        kwargs[param_name] = False
                    else:
                        return f"Error: Parameter '{param_name}' must be a boolean."
                elif param_type == str and not isinstance(val, str):
                    kwargs[param_name] = str(val)
                    
            # Call original function with sanitized args
            return func(**kwargs)
            
        except Exception as e:
            return f"Error executing {name}: {str(e)}"

    _TOOL_REGISTRY[name] = wrapper
    
    # Prevent duplicate schemas on reload
    for i, existing in enumerate(_SCHEMA_REGISTRY):
        if existing["function"]["name"] == name:
            _SCHEMA_REGISTRY[i] = schema
            return wrapper
            
    _SCHEMA_REGISTRY.append(schema)
    
    return wrapper

def get_registered_tools() -> Dict[str, Callable]:
    """Return the map of function name to actual Python function."""
    return _TOOL_REGISTRY

def get_registered_schemas() -> list[Dict[str, Any]]:
    """Return the list of OpenAI JSON schemas for LiteLLM."""
    return _SCHEMA_REGISTRY
