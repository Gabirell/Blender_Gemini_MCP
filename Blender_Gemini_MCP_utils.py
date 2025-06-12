# Blender_Gemini_MCP_utils.py

import re
try:
    import google.generativeai as genai
except ImportError:
    genai = None

SYSTEM_PROMPT = """You are an expert Blender assistant. Your responses must be focused on Blender.
When generating Python code for Blender, ensure it is correct and ready for execution.
Wrap all Python code in ```python ... ``` blocks.
The user is working in Blender, so you can assume the 'bpy' module is available."""

def get_available_models(api_key):
    """Fetches the list of available generative models from the Gemini API."""
    if not genai:
        return []
    try:
        genai.configure(api_key=api_key)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # --- CORRECTION ---
        # The first item in the tuple (the identifier) must be the full model name.
        # The second item (the label) can be the user-friendly version.
        return [(model, model.replace("models/", "").replace("-"," ").title(), "") for model in models]
    
    except Exception as e:
        print(f"Could not fetch models: {e}")
        return []

def send_prompt_to_gemini(api_key, model_name, prompt_text):
    """Sends a prompt to the specified Gemini model with a system instruction."""
    if not genai:
        return "Error: 'google-generativeai' library not installed."
        
    try:
        genai.configure(api_key=api_key)
        # model_name now correctly contains the "models/" prefix.
        model = genai.GenerativeModel(model_name, system_instruction=SYSTEM_PROMPT)
        response = model.generate_content(prompt_text)
        return response.text
    except Exception as e:
        # Return the actual error from the API for better debugging.
        return f"An API error occurred: {e}"

def extract_python_code(text):
    """Extracts code from a ```python ... ``` block."""
    match = re.search(r'```python\n(.*?)```', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None
