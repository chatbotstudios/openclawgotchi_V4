import os
import litellm

os.environ["GEMINI_API_KEY"] = "AIzaSyA0PDsdrjp9b1KKpV7g5F9bGKzExMHx7ko"

models_to_test = [
    "gemini/gemini-1.5-flash",
    "gemini/gemini-1.5-flash-latest",
    "gemini/gemini-flash-latest",
    "gemini/gemini-1.0-pro",
]

for m in models_to_test:
    try:
        response = litellm.completion(
            model=m,
            messages=[{"role": "user", "content": "hi"}],
        )
        print(f"SUCCESS: {m}")
    except Exception as e:
        print(f"FAILED: {m} -> {e}")
