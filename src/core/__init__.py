# LLM connectors module — lazy accessor to avoid eager full-dep-tree import
_router_instance = None

def get_router():
    global _router_instance
    if _router_instance is None:
        from core.router import get_router as _get_router
        _router_instance = _get_router()
    return _router_instance

def get_llm():
    return get_router()
