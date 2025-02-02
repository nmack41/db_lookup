# from pydantic_ai.models import KnownModelName, Model
# from pydantic_ai.models.ollama import OllamaModel

# def build_model_from_name_and_api_key(model_name: KnownModelName, api_key: str | None = None) -> Model:
#     if model_name.startswith("ollama:"):
#         return OllamaModel(model_name[7:], api_key=api_key or "ollama")
#     else:
#         raise ValueError(f"Unsupported model name: {model_name}")
    
from pydantic_ai.models.openai import OpenAIModel

def build_model_from_name_and_api_key(model_name: str, api_key: str | None = None) -> OpenAIModel:
    if model_name.startswith("ollama:"):
        return OpenAIModel(
            model_name=model_name.split(":", 1)[1],
            base_url='http://localhost:11434/v1',
            api_key=api_key or "ollama"
        )
    else:
        raise ValueError(f"Unsupported model name: {model_name}")

