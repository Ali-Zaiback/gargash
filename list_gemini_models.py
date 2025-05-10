import google.generativeai as genai

genai.configure(api_key="AIzaSyBWolI6Em5ce-Lt_KUUoW4rgx4jY615P0c")

print("Available Gemini models:")
for model in genai.list_models():
    print(model.name, model.supported_generation_methods) 