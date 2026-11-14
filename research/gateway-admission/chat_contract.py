"""Pure local validation. Standard library only; no network or model calls."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


class ContractError(ValueError):
    def __init__(self, message: str, status: int = 422):
        super().__init__(message)
        self.status = status


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ContractError("Duplicate JSON keys are not accepted.", 400)
        result[key] = value
    return result


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"),
                      object_pairs_hook=unique_object)


def integer(value: Any, name: str, low: int, high: int) -> int:
    if type(value) is not int or not low <= value <= high:
        raise ContractError(f"{name} must be an integer between {low} and {high}.")
    return value


def validate_settings(s: dict[str, Any]) -> dict[str, Any]:
    numeric = {
        "context_tokens": (512, 32768),
        "default_output_tokens": (1, 4096),
        "max_output_tokens": (1, 4096),
        "context_reserve_units": (128, 4096),
        "per_message_overhead_units": (16, 128),
        "max_messages": (1, 128),
        "max_request_bytes": (1024, 65536),
        "max_concurrent_requests": (1, 4),
        "request_timeout_seconds": (30, 600),
    }
    expected = set(numeric) | {"model_alias", "upstream_model", "temperature"}
    if not isinstance(s, dict) or set(s) != expected:
        raise ContractError("settings.json has missing or unknown fields.")
    if s["model_alias"] != "local-qwen36-chat" or s["upstream_model"] != "qwen3.6-colibri":
        raise ContractError("This candidate is restricted to its recorded local model.")
    if type(s["temperature"]) not in (int, float) or s["temperature"] != 0:
        raise ContractError("Only the verified temperature 0 is configured here.")
    for name, bounds in numeric.items():
        integer(s[name], name, *bounds)
    if s["default_output_tokens"] > s["max_output_tokens"]:
        raise ContractError("Default output cannot exceed maximum output.")
    minimum = s["max_output_tokens"] + s["context_reserve_units"] + 2 * s["per_message_overhead_units"]
    if minimum >= s["context_tokens"]:
        raise ContractError("Context leaves no useful prompt allowance.")
    return s


# Added to a real token count before comparing with the context. It covers request shapes
# whose render is read from the engine source but not yet confirmed against engine usage.
TOKEN_MARGIN = 32


def validate_chat(body: Any, s: dict[str, Any], count_tokens: Any = None) -> int:
    """Admit or refuse a chat request; never trim messages. Returns what was compared with
    the context size.

    Without count_tokens this is the original conservative rule: UTF-8 bytes plus fixed
    overheads ("admission units", not tokens). With count_tokens(messages) -> prompt tokens,
    the request is admitted when prompt tokens + requested output + TOKEN_MARGIN fit the
    context. The full output allowance is reserved here because the engine would otherwise
    shorten the answer silently. If counting fails for any reason the byte rule decides, so a
    counting fault can only make admission stricter. A text of n bytes is never more than n
    tokens, and the byte rule's overheads exceed the chat frames, so every request the byte
    rule admits is also within the token rule.
    """
    if not isinstance(body, dict):
        raise ContractError("Expected a JSON object.", 400)
    tool_fields = {"tools", "tool_choice", "parallel_tool_calls", "functions", "function_call"}
    if tool_fields & body.keys():
        raise ContractError("Tool calling/execution is disabled in this text-only gateway.", 403)
    allowed = {"model", "messages", "temperature", "max_tokens", "stream"}
    if body.keys() - allowed:
        raise ContractError("Unsupported request field; only text chat is configured.")
    if body.get("model") != s["model_alias"]:
        raise ContractError("Only the configured local model is permitted.", 403)
    output = integer(body.get("max_tokens", s["default_output_tokens"]),
                     "max_tokens", 1, s["max_output_tokens"])
    temperature = body.get("temperature", s["temperature"])
    if type(temperature) not in (int, float) or temperature != s["temperature"]:
        raise ContractError("temperature must remain 0 for this candidate.")
    if "stream" in body and type(body["stream"]) is not bool:
        raise ContractError("stream must be a JSON boolean.")
    messages = body.get("messages")
    if not isinstance(messages, list) or not 1 <= len(messages) <= s["max_messages"]:
        raise ContractError("Conversation has no messages or exceeds the message limit.")
    units = s["context_reserve_units"] + output
    for index, message in enumerate(messages):
        if not isinstance(message, dict) or set(message) != {"role", "content"}:
            raise ContractError("Each message must contain only role and text content.")
        if message["role"] not in ("system", "user", "assistant"):
            raise ContractError("Only system, user and assistant text messages are allowed.")
        if message["role"] == "system" and index:
            # The engine refuses this shape with its own error; say so here, clearly.
            raise ContractError("A system message is only accepted as the first message.")
        if not isinstance(message["content"], str):
            raise ContractError("Attachments and multimodal messages are disabled.")
        if message["role"] == "assistant" and "</think>" in message["content"]:
            # The engine moves text before this tag into a reasoning block. That treatment is
            # not mirrored by the byte rule or the token counter, so the shape is not served.
            raise ContractError("Assistant history containing a reasoning tag is not supported.")
        try:
            size = len(message["content"].encode("utf-8"))
        except UnicodeEncodeError:
            raise ContractError("Message contains invalid Unicode.") from None
        units += size + s["per_message_overhead_units"]
    if messages[-1]["role"] != "user":
        raise ContractError("Send a new user message to continue the conversation.")
    if count_tokens is not None and units > s["context_tokens"]:
        try:
            prompt = count_tokens(messages)
        except Exception:
            prompt = None
        if type(prompt) is int and prompt > 0:
            needed = prompt + output + TOKEN_MARGIN
            if needed > s["context_tokens"]:
                raise ContractError(
                    "Conversation is too long for this model's context. Start a new chat "
                    "or shorten the text; history was NOT silently truncated.", 413)
            return needed
    if units > s["context_tokens"]:
        raise ContractError(
            "Conversation exceeds the conservative input budget. Start a new chat "
            "or shorten the text; history was NOT silently truncated.", 413)
    return units


def load_local_env(path: Path) -> dict[str, str]:
    """Read ONLY the explicitly named project file. No dotenv discovery/expansion."""
    result: dict[str, str] = {}
    for number, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        name, sep, value = line.partition("=")
        name, value = name.strip(), value.strip()
        if not sep or not name or name in result:
            raise ContractError(f"Invalid or duplicate setting on local.env line {number}.")
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        result[name] = value
    return result


def deployment_values(values: dict[str, str], s: dict[str, Any]) -> dict[str, str]:
    required_names = {
        "COLIBRI_API_BASE", "COLIBRI_AUTH_MODE", "COLIBRI_API_KEY", "GATEWAY_PORT",
        "WEBUI_PORT", "WEBUI_GATEWAY_KEY", "LITELLM_MASTER_KEY", "WEBUI_SECRET_KEY", "WEBUI_ADMIN_EMAIL",
        "WEBUI_ADMIN_PASSWORD", "ALLOW_CHAT_REQUESTS", "COLIBRI_CONFIGURED_CONTEXT",
        "COLIBRI_CONFIGURED_GENERATION_LIMIT", "COLIBRI_CONFIGURED_KV_SLOTS",
    }
    if set(values) != required_names:
        raise ContractError("local.env must contain exactly the names in .env.example.")

    def required(name: str) -> str:
        value = values[name]
        if not value or value.startswith("__") or "\n" in value or "\r" in value:
            raise ContractError(f"{name} is unresolved or invalid.")
        return value

    def number(name: str, low: int, high: int) -> int:
        value = required(name)
        if not value.isascii() or not value.isdigit():
            raise ContractError(f"{name} must be a decimal integer.")
        return integer(int(value), name, low, high)

    base = urlsplit(required("COLIBRI_API_BASE"))
    try:
        upstream_port = base.port
    except ValueError:
        raise ContractError("Invalid Colibri port.") from None
    if (base.scheme != "http" or base.hostname != "127.0.0.1" or base.path != "/v1"
            or upstream_port is None or not 1024 <= upstream_port <= 65535
            or base.username or base.password or base.query or base.fragment):
        raise ContractError("Use the approved native http://127.0.0.1:<port>/v1 endpoint.")
    gateway = number("GATEWAY_PORT", 1024, 65535)
    webui = number("WEBUI_PORT", 1024, 65535)
    if len({gateway, webui, upstream_port}) != 3:
        raise ContractError("Colibri, gateway and WebUI must have distinct ports.")
    if gateway == 4000:
        raise ContractError("Select a non-4000 gateway port; avoid pinned CLI auto-port fallback.")
    mode, upstream_key = required("COLIBRI_AUTH_MODE"), required("COLIBRI_API_KEY")
    if mode == "bearer":
        if upstream_key == "unused-local-colibri":
            raise ContractError("Bearer mode requires the actual configured credential.")
    elif mode == "none-placeholder-approved":
        if upstream_key != "unused-local-colibri":
            raise ContractError("The explicit no-auth adapter mode requires its placeholder.")
    else:
        raise ContractError("Colibri authentication mode is unresolved.")
    for name in ("WEBUI_GATEWAY_KEY", "WEBUI_SECRET_KEY"):
        key = required(name)
        if not key.isascii() or len(key) < 43:
            raise ContractError(f"{name} must be a strong ASCII key of at least 43 characters.")
    master = required("LITELLM_MASTER_KEY")
    if not master.isascii() or not master.startswith("sk-") or len(master) < 67:
        raise ContractError("LITELLM_MASTER_KEY requires a separately approved strong sk- key of at least 67 characters.")
    secrets = [values["WEBUI_GATEWAY_KEY"], values["WEBUI_SECRET_KEY"], master]
    if len(set(secrets)) != len(secrets) or upstream_key in secrets:
        raise ContractError("Use distinct upstream, gateway, master and WebUI signing credentials.")
    if "@" not in required("WEBUI_ADMIN_EMAIL"):
        raise ContractError("Supply an email-shaped local administrator login.")
    password_bytes = len(required("WEBUI_ADMIN_PASSWORD").encode("utf-8"))
    if not 16 <= password_bytes <= 72:
        raise ContractError("Administrator password must be 16..72 UTF-8 bytes.")
    if required("ALLOW_CHAT_REQUESTS") not in ("true", "false"):
        raise ContractError("ALLOW_CHAT_REQUESTS must be explicitly true or false.")
    if values["ALLOW_CHAT_REQUESTS"] == "true":
        declarations = (
            ("COLIBRI_CONFIGURED_CONTEXT", s["context_tokens"]),
            ("COLIBRI_CONFIGURED_GENERATION_LIMIT", s["max_output_tokens"]),
            ("COLIBRI_CONFIGURED_KV_SLOTS", s["max_concurrent_requests"]),
        )
        for name, minimum in declarations:
            if number(name, 1, 1048576) < minimum:
                raise ContractError(f"{name} is smaller than the proposed chat setting.")
    return values
