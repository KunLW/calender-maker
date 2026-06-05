from app.ai import get_ai_provider
from app.config import Settings


def test_qwen_provider_uses_openai_compatible_settings() -> None:
    settings = Settings(QWEN_API_KEY="qwen-key")

    provider = get_ai_provider(settings)

    assert provider is not None
    assert provider.api_key == "qwen-key"
    assert provider.model == "qwen-plus"
    assert provider.base_url == "https://dashscope.aliyuncs.com/compatible-mode/v1"
    assert provider.response_format == {"type": "json_object"}


def test_openai_provider_is_fallback() -> None:
    settings = Settings(OPENAI_API_KEY="openai-key")

    provider = get_ai_provider(settings)

    assert provider is not None
    assert provider.api_key == "openai-key"
    assert provider.model == "gpt-4.1-mini"
    assert provider.base_url is None
    assert provider.response_format["type"] == "json_schema"

