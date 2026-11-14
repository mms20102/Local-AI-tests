"""Shared pieces of the synthetic proxy/ASGI fixture: fake upstream, network guard, proxy lifespan.

Everything here is synthetic. The fake upstream generates nothing: it returns fixed text. The proxy is
LiteLLM's real ASGI application, started through its own lifespan with a handwritten config file.
"""
from __future__ import annotations

import asyncio
import contextlib
import json
import os
import socket
from pathlib import Path

HERE = Path(__file__).resolve().parent
FORBIDDEN_PORTS = {8000, 4001, 8080}
ANSWER_CHUNKS = ["```python\n", "x = {\"a\": 1}\n", "```"]
ANSWER_TEXT = "".join(ANSWER_CHUNKS)


class Guard:
    """Refuse and record any connection that is not loopback, or that targets a live-stack port."""

    def __init__(self):
        self.violations: list[str] = []
        self.loopback_ports: set[int] = set()
        self._real_connect = socket.socket.connect
        self._real_connect_ex = socket.socket.connect_ex

    def _check(self, address):
        if isinstance(address, tuple) and len(address) >= 2:
            host, port = address[0], address[1]
            if host not in ("127.0.0.1", "::1", "localhost") or port in FORBIDDEN_PORTS:
                self.violations.append(f"{host}:{port}")
                raise OSError("blocked by the fixture network guard")
            self.loopback_ports.add(port)

    def install(self):
        guard = self

        def connect(sock, address):
            guard._check(address)
            return guard._real_connect(sock, address)

        def connect_ex(sock, address):
            guard._check(address)
            return guard._real_connect_ex(sock, address)
        socket.socket.connect = connect
        socket.socket.connect_ex = connect_ex
        # On Windows asyncio connects through the proactor, not socket.connect: guard that path too.
        try:
            from asyncio import windows_events
            real = windows_events.IocpProactor.connect

            def proactor_connect(proactor, conn, address):
                guard._check(address)
                return real(proactor, conn, address)
            windows_events.IocpProactor.connect = proactor_connect
            self.proactor_guarded = True
        except Exception:
            self.proactor_guarded = False


class FakeUpstream:
    """A tiny HTTP/1.1 server on a fresh loopback port. Records every request body; generates nothing."""

    def __init__(self):
        self.captures: list[dict] = []
        self.headers: list[dict] = []
        self.stream_closed_early = 0
        self.stream_completed = 0
        self.hold_after_chunks: int | None = None     # for disconnect tests: pause the stream after N chunks
        self.hold_before_first = False
        self.release = asyncio.Event()
        self.reached_hold = asyncio.Event()
        self.server = None
        self.port = None

    async def start(self):
        self.server = await asyncio.start_server(self._handle, "127.0.0.1", 0)
        self.port = self.server.sockets[0].getsockname()[1]
        assert self.port not in FORBIDDEN_PORTS
        return self.port

    async def stop(self):
        if self.server is not None:
            self.server.close()
            with contextlib.suppress(Exception):
                await asyncio.wait_for(self.server.wait_closed(), 5)

    async def _handle(self, reader, writer):
        try:
            head = await reader.readuntil(b"\r\n\r\n")
            lines = head.decode("latin-1").split("\r\n")
            method, path, _ = lines[0].split(" ", 2)
            headers = {k.strip().lower(): v.strip() for k, v in (line.split(":", 1) for line in lines[1:] if ":" in line)}
            body = await reader.readexactly(int(headers.get("content-length", "0")))
            if method != "POST" or not path.endswith("/chat/completions"):
                writer.write(b"HTTP/1.1 404 Not Found\r\ncontent-length: 0\r\nconnection: close\r\n\r\n")
                await writer.drain()
                return
            parsed = json.loads(body.decode("utf-8"))
            self.captures.append(parsed)
            self.headers.append({k: ("<present>" if k == "authorization" else v) for k, v in headers.items()})
            if parsed.get("stream"):
                await self._stream(reader, writer, parsed)
            else:
                payload = json.dumps({
                    "id": "chatcmpl-fake", "object": "chat.completion", "created": 1, "model": parsed.get("model"),
                    "choices": [{"index": 0, "message": {"role": "assistant", "content": ANSWER_TEXT}, "finish_reason": "stop"}],
                    "usage": {"prompt_tokens": 11, "completion_tokens": 7, "total_tokens": 18}}).encode("utf-8")
                writer.write(b"HTTP/1.1 200 OK\r\ncontent-type: application/json\r\ncontent-length: "
                             + str(len(payload)).encode() + b"\r\nconnection: close\r\n\r\n" + payload)
                await writer.drain()
        except (asyncio.IncompleteReadError, ConnectionError):
            pass
        finally:
            with contextlib.suppress(Exception):
                writer.close()

    async def _hold(self, reader):
        """Wait until the test releases the stream OR the peer closes the connection. True if the peer closed."""
        self.reached_hold.set()
        peer = asyncio.ensure_future(reader.read(1))
        released = asyncio.ensure_future(self.release.wait())
        await asyncio.wait({peer, released}, return_when=asyncio.FIRST_COMPLETED)
        closed = peer.done() and not peer.cancelled() and peer.exception() is None and peer.result() == b""
        closed = closed or (peer.done() and not peer.cancelled() and peer.exception() is not None)
        for task in (peer, released):
            task.cancel()
        return closed

    async def _stream(self, reader, writer, parsed):
        writer.write(b"HTTP/1.1 200 OK\r\ncontent-type: text/event-stream\r\nconnection: close\r\n\r\n")
        await writer.drain()

        def frame(delta, finish=None):
            return ("data: " + json.dumps({"id": "chatcmpl-fake", "object": "chat.completion.chunk", "created": 1,
                                           "model": parsed.get("model"),
                                           "choices": [{"index": 0, "delta": delta, "finish_reason": finish}]}) + "\n\n").encode()
        try:
            if self.hold_before_first and await self._hold(reader):
                self.stream_closed_early += 1
                return
            writer.write(frame({"role": "assistant", "content": ""}))
            await writer.drain()
            for n, text in enumerate(ANSWER_CHUNKS, 1):
                writer.write(frame({"content": text}))
                await writer.drain()
                if self.hold_after_chunks == n and await self._hold(reader):
                    self.stream_closed_early += 1
                    return
            writer.write(frame({}, "stop"))
            writer.write(b"data: [DONE]\n\n")
            await writer.drain()
            self.stream_completed += 1
        except (ConnectionError, OSError):
            self.stream_closed_early += 1


def write_scratch_files(upstream_port: int) -> Path:
    """Handwritten synthetic settings and proxy config. Same SHAPE as a text-only gateway; no real value."""
    app = HERE / "app"
    (app / "settings.json").write_text(json.dumps({
        "model_alias": "local-qwen36-chat", "upstream_model": "qwen3.6-colibri", "context_tokens": 2048,
        "default_output_tokens": 256, "max_output_tokens": 256, "context_reserve_units": 256,
        "per_message_overhead_units": 32, "max_messages": 32, "max_request_bytes": 32768,
        "max_concurrent_requests": 1, "request_timeout_seconds": 120, "temperature": 0}), encoding="utf-8")
    config = {
        "model_list": [{"model_name": "local-qwen36-chat", "litellm_params": {
            "model": "openai/qwen3.6-colibri", "api_base": f"http://127.0.0.1:{upstream_port}/v1",
            "api_key": "os.environ/SCRATCH_UPSTREAM_KEY", "temperature": 0, "max_tokens": 256, "max_retries": 0,
            "timeout": 30, "additional_drop_params": ["stream_options"]},
            "model_info": {"mode": "chat"}}],
        "general_settings": {"custom_auth": "gateway_auth.authenticate", "background_health_checks": False,
                             "always_include_stream_usage": False, "master_key": "os.environ/LITELLM_MASTER_KEY"},
        "litellm_settings": {"num_retries": 0, "request_timeout": 30, "drop_params": False, "telemetry": False,
                             "turn_off_message_logging": True, "callbacks": ["integration_candidate.teach"]},
        "router_settings": {"num_retries": 0, "timeout": 30, "fallbacks": [], "context_window_fallbacks": [],
                            "content_policy_fallbacks": []}}
    path = HERE / "scratch-config.yaml"
    path.write_text(json.dumps(config, indent=1), encoding="utf-8")       # JSON is valid YAML
    return path


@contextlib.asynccontextmanager
async def running_proxy(config_path: Path):
    """LiteLLM's real ASGI app, started through its OWN lifespan with the scratch config."""
    from litellm.proxy import proxy_server
    os.environ["WORKER_CONFIG"] = json.dumps({"config": str(config_path)})
    async with proxy_server.app.router.lifespan_context(proxy_server.app):
        yield proxy_server
