import sys
import os
import asyncio

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

from core.litellm_connector import LiteLLMConnector
import pytest

@pytest.mark.skip(reason="Manual integration test. Requires physical Buddy on local network.")
async def test_pulse():
    print("--- Starting OpenClawGotchi Buddy Test ---")
    
    # Initialize connector with a dummy model
    # (We don't actually need to hit the API if we just want to see the 'Busy' pulse)
    connector = LiteLLMConnector(model="gemini/gemini-1.5-flash")
    
    print("Triggering LLM call (this should pulse the Buddy at 10.0.0.23)...")
    try:
        # We pass a very short timeout and no real keys to force it to fail 
        # AFTER the first pulse is sent.
        await connector.call(prompt="Hello, Buddy!", system_prompt="You are a test.", history=[])
    except Exception as e:
        print("\nNote: LLM Call failed as expected (we didn't provide keys), but did the Buddy react?")
        print(f"Error was: {e}")

if __name__ == "__main__":
    asyncio.run(test_pulse())
