"""
Tests for Modal provider configuration and request behavior.
"""

import json
import os
import sys

import pytest

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
)

import litellm
from litellm import completion
from litellm.llms.openai_like.dynamic_config import create_config_class
from litellm.llms.openai_like.json_loader import JSONProviderRegistry

MODAL_BASE_URL = "https://api.us-west-2.modal.direct/v1"
MODAL_MODEL = "modal/zai-org/GLM-5.1-FP8"
MODAL_ENDPOINT = f"{MODAL_BASE_URL}/chat/completions"


def _get_config():
    provider = JSONProviderRegistry.get("modal")
    assert provider is not None
    config_class = create_config_class(provider)
    return config_class()


def _mock_response(model_name: str = "zai-org/GLM-5.1-FP8") -> dict:
    return {
        "id": "chatcmpl-modal-123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": model_name,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": "3"},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 1, "total_tokens": 11},
    }


def test_modal_in_provider_lists():
    from litellm import LlmProviders

    assert hasattr(LlmProviders, "MODAL")
    assert LlmProviders.MODAL.value == "modal"
    assert "modal" in litellm.provider_list
    assert "modal" in litellm.openai_compatible_providers
    assert MODAL_BASE_URL in litellm.openai_compatible_endpoints


def test_modal_json_config_exists():
    provider = JSONProviderRegistry.get("modal")
    assert provider is not None
    assert provider.base_url == MODAL_BASE_URL
    assert provider.api_key_env == "MODAL_API_KEY"
    assert provider.api_base_env == "MODAL_API_BASE"
    assert provider.param_mappings.get("max_completion_tokens") == "max_tokens"


def test_modal_provider_resolution():
    from litellm.litellm_core_utils.get_llm_provider_logic import get_llm_provider

    model, provider, api_key, api_base = get_llm_provider(
        model=MODAL_MODEL,
        custom_llm_provider=None,
        api_base=None,
        api_key=None,
    )

    assert model == "zai-org/GLM-5.1-FP8"
    assert provider == "modal"
    assert api_base == MODAL_BASE_URL


def test_modal_provider_resolution_from_api_base():
    from litellm.litellm_core_utils.get_llm_provider_logic import get_llm_provider

    model, provider, api_key, api_base = get_llm_provider(
        model="zai-org/GLM-5.1-FP8",
        custom_llm_provider=None,
        api_base=MODAL_BASE_URL,
        api_key=None,
    )

    assert model == "zai-org/GLM-5.1-FP8"
    assert provider == "modal"
    assert api_base == MODAL_BASE_URL


def test_modal_env_override(monkeypatch):
    config = _get_config()
    custom_base = "https://workspace--glm.modal.run/v1"
    monkeypatch.setenv("MODAL_API_BASE", custom_base)
    monkeypatch.setenv("MODAL_API_KEY", "modal-key")

    api_base, api_key = config._get_openai_compatible_provider_info(None, None)
    assert api_base == custom_base
    assert api_key == "modal-key"


def test_modal_provider_config_manager():
    from litellm import LlmProviders
    from litellm.utils import ProviderConfigManager

    config = ProviderConfigManager.get_provider_chat_config(
        model="zai-org/GLM-5.1-FP8", provider=LlmProviders.MODAL
    )

    assert config is not None
    assert config.custom_llm_provider == "modal"


def test_modal_router_config():
    from litellm import Router

    router = Router(
        model_list=[
            {
                "model_name": "glm-5-1-fp8",
                "litellm_params": {
                    "model": MODAL_MODEL,
                    "api_key": "test-key",
                },
            }
        ]
    )

    assert len(router.model_list) == 1
    assert router.model_list[0]["model_name"] == "glm-5-1-fp8"


def test_modal_model_metadata():
    import os

    os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"
    litellm.model_cost = litellm.get_model_cost_map(url="")

    model_info = litellm.model_cost[MODAL_MODEL]
    assert model_info["litellm_provider"] == "modal"
    assert model_info["mode"] == "chat"
    assert model_info["input_cost_per_token"] == 0.0
    assert model_info["output_cost_per_token"] == 0.0


@pytest.mark.asyncio
async def test_modal_async_completion_request_shape(respx_mock, monkeypatch):
    monkeypatch.setenv("MODAL_API_KEY", "test-modal-key")
    litellm.disable_aiohttp_transport = True

    route = respx_mock.post(MODAL_ENDPOINT).respond(json=_mock_response())

    response = await litellm.acompletion(
        model=MODAL_MODEL,
        messages=[{"role": "user", "content": "How many r-s are in strawberry?"}],
        max_completion_tokens=20,
    )

    assert response.choices[0].message.content == "3"
    assert route.called is True

    request = route.calls[0].request
    assert request.headers["Authorization"] == "Bearer test-modal-key"
    payload = json.loads(request.content.decode("utf-8"))
    assert payload["model"] == "zai-org/GLM-5.1-FP8"
    assert payload["max_tokens"] == 20
    assert "max_completion_tokens" not in payload


def test_modal_sync_completion_request_shape(respx_mock, monkeypatch):
    monkeypatch.setenv("MODAL_API_KEY", "test-modal-key")
    litellm.disable_aiohttp_transport = True

    route = respx_mock.post(MODAL_ENDPOINT).respond(json=_mock_response())

    response = completion(
        model=MODAL_MODEL,
        messages=[{"role": "user", "content": "How many r-s are in strawberry?"}],
        max_completion_tokens=12,
    )

    assert response.choices[0].message.content == "3"
    assert route.called is True

    request = route.calls[0].request
    assert request.headers["Authorization"] == "Bearer test-modal-key"
    payload = json.loads(request.content.decode("utf-8"))
    assert payload["max_tokens"] == 12
    assert "max_completion_tokens" not in payload


def test_modal_live_completion_if_configured():
    if not os.getenv("MODAL_API_KEY"):
        pytest.skip("MODAL_API_KEY not set")

    response = completion(
        model=MODAL_MODEL,
        messages=[{"role": "user", "content": "Reply with the digit 3 only."}],
        max_tokens=8,
    )

    assert response.choices[0].message.content is not None
