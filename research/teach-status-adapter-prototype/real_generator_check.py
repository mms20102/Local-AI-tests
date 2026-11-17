"""Offline: push a fake model stream through the INSTALLED LiteLLM proxy generator with the adapter
registered as a callback, and print the exact SSE frames. No server, no model, no network."""
import asyncio
import json
import sys

sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 else ".")
import teach_status_adapter as adapter  # noqa: E402

import litellm  # noqa: E402
from litellm.integrations.custom_logger import CustomLogger  # noqa: E402
from litellm.proxy import proxy_server  # noqa: E402
from litellm.proxy._types import UserAPIKeyAuth  # noqa: E402
from litellm.types.utils import ModelResponseStream  # noqa: E402


class Leaf(CustomLogger):
    def async_post_call_streaming_iterator_hook(self, user_api_key_dict, response, request_data):
        return adapter.status_stream(response, request_data)


def chunk(text, finish=None):
    return ModelResponseStream(id="chatcmpl-test", model="local-qwen36-chat", created=1,
                               choices=[{"index": 0, "delta": {"content": text}, "finish_reason": finish}])


async def fake_model():
    for text in ("```python\n", "x = {\"a\": 1}\n", "```"):
        yield chunk(text)
    yield chunk("", "stop")


async def main(with_notice):
    litellm.callbacks = [Leaf()]
    status = {"note_cap": 0, "no_room": 1 if with_notice else 0, "uncounted": 0, "byte_only": 0, "invalid": 0}
    request_data = adapter.attach({"model": "local-qwen36-chat", "stream": True},
                                  adapter.decision_from_hook([], "abc123abc123", status), "en")
    frames = []
    async for frame in proxy_server.async_data_generator(fake_model(), UserAPIKeyAuth(), request_data):
        frames.append(frame if isinstance(frame, str) else frame.decode("utf-8"))
    return frames


for flag in (True, False):
    frames = asyncio.run(main(flag))
    print("with notice" if flag else "without notice", len(frames), "frames")
    contents = []
    for n, frame in enumerate(frames):
        body = frame[len("data: "):].strip() if frame.startswith("data: ") else frame.strip()
        if body == "[DONE]":
            print(" ", n, "[DONE]")
            continue
        try:
            parsed = json.loads(body)
        except Exception:
            print(" ", n, "UNPARSEABLE", frame[:120])
            continue
        if "event" in parsed:
            print(" ", n, "EVENT", json.dumps(parsed, ensure_ascii=False), "| has choices:", "choices" in parsed)
        else:
            delta = parsed["choices"][0]["delta"].get("content")
            contents.append(delta or "")
            print(" ", n, "CHUNK", repr(delta), parsed["choices"][0].get("finish_reason"))
    print("  joined answer:", repr("".join(contents)))
