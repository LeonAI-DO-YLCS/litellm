import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Modal

## Overview

| Property | Details |
|-------|-------|
| Description | Modal hosts OpenAI-compatible LLM endpoints, including the hosted `modal.direct` GLM-5.1 endpoint and user-deployed `*.modal.run` endpoints. |
| Provider Route on LiteLLM | `modal/` |
| Link to Provider Doc | [Modal Docs ↗](https://modal.com/docs) |
| Default Base URL | `https://api.us-west-2.modal.direct/v1` |
| Supported Operations | [`/chat/completions`](#usage---litellm-python-sdk) |

<br />
<br />

**LiteLLM supports the hosted Modal endpoint by default and lets you override the base URL for any other Modal-hosted OpenAI-compatible endpoint with `MODAL_API_BASE`.**

## Required Variables

```python showLineNumbers title="Environment Variables"
os.environ["MODAL_API_KEY"] = ""  # your Modal API token
```

Optional base URL override:

```python showLineNumbers title="Optional Base URL Override"
os.environ["MODAL_API_BASE"] = "https://your-workspace--your-app.modal.run/v1"
```

## Usage - LiteLLM Python SDK

### Non-streaming

```python showLineNumbers title="Modal Non-streaming Completion"
import os
from litellm import completion

os.environ["MODAL_API_KEY"] = ""

response = completion(
    model="modal/zai-org/GLM-5.1-FP8",
    messages=[{"role": "user", "content": "How many r-s are in strawberry?"}],
    max_tokens=500,
)

print(response)
```

### Streaming

```python showLineNumbers title="Modal Streaming Completion"
import os
from litellm import completion

os.environ["MODAL_API_KEY"] = ""

response = completion(
    model="modal/zai-org/GLM-5.1-FP8",
    messages=[{"role": "user", "content": "Count to 3"}],
    max_tokens=50,
    stream=True,
)

for chunk in response:
    print(chunk)
```

## Usage - LiteLLM Proxy

Add the following to your LiteLLM Proxy configuration file:

```yaml showLineNumbers title="config.yaml"
model_list:
  - model_name: glm-5-1-fp8
    litellm_params:
      model: modal/zai-org/GLM-5.1-FP8
      api_key: os.environ/MODAL_API_KEY

  - model_name: my-modal-endpoint
    litellm_params:
      model: modal/my-custom-model
      api_key: os.environ/MODAL_API_KEY
      api_base: os.environ/MODAL_API_BASE
```

Start your LiteLLM Proxy server:

```bash showLineNumbers title="Start LiteLLM Proxy"
litellm --config config.yaml
```

<Tabs>
<TabItem value="openai-sdk" label="OpenAI SDK">

```python showLineNumbers title="Modal via Proxy - OpenAI SDK"
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:4000",
    api_key="your-proxy-api-key",
)

response = client.chat.completions.create(
    model="glm-5-1-fp8",
    messages=[{"role": "user", "content": "hello from litellm"}],
)

print(response.choices[0].message.content)
```

</TabItem>

<TabItem value="litellm-sdk" label="LiteLLM SDK">

```python showLineNumbers title="Modal via Proxy - LiteLLM SDK"
import litellm

response = litellm.completion(
    model="litellm_proxy/glm-5-1-fp8",
    messages=[{"role": "user", "content": "hello from litellm"}],
    api_base="http://localhost:4000",
    api_key="your-proxy-api-key",
)

print(response.choices[0].message.content)
```

</TabItem>

<TabItem value="curl" label="cURL">

```bash showLineNumbers title="Modal via Proxy - cURL"
curl http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-proxy-api-key" \
  -d '{
    "model": "glm-5-1-fp8",
    "messages": [{"role": "user", "content": "hello from litellm"}]
  }'
```

</TabItem>
</Tabs>

## Direct Modal cURL

```bash showLineNumbers title="Modal Direct Endpoint"
curl -X POST "https://api.us-west-2.modal.direct/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MODAL_API_KEY" \
  -d '{
    "model": "zai-org/GLM-5.1-FP8",
    "messages": [{"role": "user", "content": "How many r-s are in strawberry?"}],
    "max_tokens": 500
  }'
```

## Notes

- Use `model="modal/<provider-model-id>"` for hosted Modal endpoints exposed in OpenAI-compatible format.
- Use `MODAL_API_BASE` or per-call `api_base` when targeting your own Modal deployment, including `*.modal.run` endpoints.
- The initial LiteLLM metadata entry is `modal/zai-org/GLM-5.1-FP8`.
