import time
from typing import cast

import logfire
from pydantic_ai.exceptions import UnexpectedModelBehavior
from pydantic_ai.messages import ModelMessage, ModelResponse
from pydantic_ai.models import KnownModelName, Model
from pydantic_ai.models.gemini import GeminiAgentModel, GeminiModel, GeminiModelName
from pydantic_ai.settings import ModelSettings
from pydantic_ai.tools import ToolDefinition
from pydantic_ai.usage import Usage

MAX_RETRIES = 3


class GeminiAgentModelWithRetry(GeminiAgentModel):
    """
    Gemini model that retries on 503 "Overloaded" errors
    """

    async def request(
        self, messages: list[ModelMessage], model_settings: ModelSettings | None
    ) -> tuple[ModelResponse, Usage]:
        retries = 0
        while True:
            try:
                return await super().request(messages, model_settings)
            except UnexpectedModelBehavior as e:
                if "503" in str(e) and "overloaded" in str(e):
                    retries += 1
                    if retries < MAX_RETRIES:
                        logfire.warn(
                            f"Model overloaded, retrying request {retries}/{MAX_RETRIES}",
                            retries=retries,
                            max_retries=MAX_RETRIES,
                        )
                        time.sleep(0.1)  # Wait 100ms before retry
                        continue
                raise


class GeminiModelWithRetry(GeminiModel):
    """
    Gemini model that retries on 503 "Overloaded" errors
    """

    async def agent_model(
        self,
        *,
        function_tools: list[ToolDefinition],
        allow_text_result: bool,
        result_tools: list[ToolDefinition],
    ) -> GeminiAgentModelWithRetry:
        return GeminiAgentModelWithRetry(
            http_client=self.http_client,
            model_name=self.model_name,
            auth=self.auth,
            url=self.url,
            function_tools=function_tools,
            allow_text_result=allow_text_result,
            result_tools=result_tools,
        )


def build_model_from_name_and_api_key(model_name: KnownModelName, api_key: str | None = None) -> Model:
    if model_name.startswith("openai:"):
        from pydantic_ai.models.openai import OpenAIModel

        return OpenAIModel(model_name[7:], api_key=api_key)

    elif model_name.startswith("anthropic:"):
        from pydantic_ai.models.anthropic import AnthropicModel

        return AnthropicModel(model_name[10:], api_key=api_key)

    elif model_name.startswith("google-gla:"):
        return GeminiModelWithRetry(cast(GeminiModelName, model_name[11:]), api_key=api_key)

    elif model_name.startswith("groq:"):
        from pydantic_ai.models.groq import GroqModel, GroqModelName

        return GroqModel(cast(GroqModelName, model_name[5:]), api_key=api_key)

    elif model_name.startswith("mistral:"):
        from pydantic_ai.models.mistral import MistralModel

        return MistralModel(model_name[8:], api_key=api_key)

    elif model_name.startswith("ollama:"):
        from pydantic_ai.models.ollama import OllamaModel

        return OllamaModel(model_name[7:], api_key=api_key or "ollama")

    else:
        raise ValueError(f"Unsupported model name: {model_name}")
