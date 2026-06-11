"""
LLM Router — auto-fallback between LLM providers.
"""

import logging
from typing import Optional
import asyncio

from core.base import LLMError
from core.litellm_connector import LiteLLMConnector

log = logging.getLogger(__name__)

class LLMRouter:
    """
    Routes requests to available LLM.
    - Lite mode (default): Standard LiteLLM (backend from DEFAULT_LITE_PRESET: glm or gemini)
    - Pro mode: Advanced Gemini model via LiteLLM
    """
    
    def __init__(self):
        # Lite Mode
        self.litellm = LiteLLMConnector()
        
        from config import DEFAULT_PRO_MODEL, DEFAULT_PRO_PRESET, LLM_PRESETS
        
        pro_api_base = None
        if DEFAULT_PRO_PRESET in LLM_PRESETS:
            pro_api_base = LLM_PRESETS[DEFAULT_PRO_PRESET].get("api_base")
            
        # Pro Mode
        self.pro_llm = LiteLLMConnector(
            model=DEFAULT_PRO_MODEL, 
            api_base=pro_api_base,
            preset=DEFAULT_PRO_PRESET
        )
        
        from config import _env_flag
        self.force_lite = _env_flag("LLM_FORCE_LITE", True)  # Load persisted mode choice
        self._lock = asyncio.Lock()
    
    async def call(
        self, 
        prompt: str, 
        history: list[dict],
        system_prompt: Optional[str] = None
    ) -> tuple[str, str]:
        """
        Call LLM based on current mode.
        
        Returns:
            tuple: (response_text, connector_name)
        """
        if self.force_lite:
            if not self.litellm.is_available():
                raise LLMError("LiteLLM not available")
            response = await self.litellm.call(prompt, history, system_prompt)
            return response, "litellm-lite"
        else:
            if not self.pro_llm.is_available():
                raise LLMError("LiteLLM not available for Pro mode")
            # Pro Mode call
            response = await self.pro_llm.call(prompt, history, system_prompt)
            return response, "litellm-pro"
    
    def toggle_lite_mode(self) -> bool:
        """Toggle between Lite and Pro mode. Returns new state (True=Lite)."""
        self.force_lite = not self.force_lite
        log.info(f"Mode switched to: {'Lite' if self.force_lite else 'Pro'}")
        return self.force_lite
    
    @property
    def lock(self):
        """Get the lock for exclusive access."""
        return self._lock

# Global instance
_router: Optional[LLMRouter] = None

def get_router() -> LLMRouter:
    """Get or create the global router instance."""
    global _router
    if _router is None:
        _router = LLMRouter()
    return _router

def get_llm() -> LLMRouter:
    """Alias for get_router()."""
    return get_router()
