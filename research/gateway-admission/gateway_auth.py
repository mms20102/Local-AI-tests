"""One documented LiteLLM custom-auth hook; no extra proxy or tool runtime."""
from __future__ import annotations

import json
import os
from secrets import compare_digest

from fastapi import Request
from litellm.proxy._types import ProxyException, UserAPIKeyAuth

from chat_contract import ContractError, unique_object, validate_chat, validate_settings
from token_count import load_counter

LIMITS = validate_settings(json.loads(os.environ["TRYOUT_LIMITS_JSON"]))
# Real token counting when the pinned tokenizer file and library are present; otherwise None
# and the conservative byte rule applies unchanged.
COUNT_TOKENS = load_counter()
print("[admission] " + ("real token counting" if COUNT_TOKENS else "byte rule only"), flush=True)
KEY = os.environ["WEBUI_GATEWAY_KEY"]
APPROVAL = os.environ["ALLOW_CHAT_REQUESTS"]
if not KEY or KEY.startswith("__") or not KEY.isascii() or len(KEY) < 43:
    raise RuntimeError("Gateway credential is unresolved.")
if APPROVAL not in {"true", "false"}:
    raise RuntimeError("Explicit chat-request approval is required.")


def reject(message: str, code: int) -> None:
    # Never include a request body, supplied key, or environment value in errors.
    raise ProxyException(message=message, type="local_chat_policy",
                         param="request", code=code)


async def authenticate(request: Request, api_key: str) -> UserAPIKeyAuth:
    if not api_key or not compare_digest(api_key.encode("utf-8"), KEY.encode("utf-8")):
        reject("Invalid gateway credential.", 401)
    route = (request.method, request.url.path)
    reads = {("GET", "/models"), ("GET", "/v1/models"),
             ("GET", "/health/liveliness"), ("GET", "/health/readiness")}
    chats = {("POST", "/chat/completions"), ("POST", "/v1/chat/completions")}
    if route not in reads | chats or request.query_params:
        reject("Route is not allowed for this chat-only application credential.", 403)
    if route in chats:
        if request.headers.get("content-type", "").split(";")[0].strip().lower() != "application/json":
            reject("Use application/json.", 415)
        raw = await request.body()
        if len(raw) > LIMITS["max_request_bytes"]:
            reject("Request exceeds the configured byte limit.", 413)
        try:
            body = json.loads(raw, object_pairs_hook=unique_object)
            validate_chat(body, LIMITS, COUNT_TOKENS)
        except ContractError as error:
            reject(str(error), error.status)
        except (ValueError, UnicodeDecodeError):
            reject("Invalid JSON request.", 400)
        if APPROVAL != "true":
            reject("Chat requests are disabled pending separate execution authorization.", 403)
    return UserAPIKeyAuth(api_key=api_key, user_id="tryout-local-chat",
                         models=[LIMITS["model_alias"]])
