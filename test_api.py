import google.generativeai as genai

# Configure the API
genai.configure(api_key="AIzaSyD4STHIxu6QbF0i0o9vUFkBR9dv7LiNMDs")

try:
    # List available models
    for m in genai.list_models():
        print(m.name)
except Exception as e:
    print(f"Error accessing Gemini API: {str(e)}") 