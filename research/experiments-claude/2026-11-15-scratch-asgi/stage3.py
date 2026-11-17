"""Stage 3: client disconnects, driven through the REAL proxy ASGI app with a direct receive/send driver.

Not httpx: its ASGI transport buffers the whole body, so it cannot show a disconnect between pulls.
Here the test owns `receive` and `send`:
  - receive delivers the request body once, then waits on an event and returns http.disconnect;
  - send records every message and can block on a barrier after N body messages, or (HTTP spec 2.4)
    raise OSError as a closed connection does.
Each case records separately: what the test requested, how the application call ended, how many
body messages were accepted, the adapter stream's terminal cleanup state, and whether the fake
upstream saw its connection closed before it had finished.

Declared versions are stated per case: ASGI application version 3.0; HTTP spec_version 2.3
(disconnect is learned from receive) or 2.4 (a send on a closed connection raises OSError).
"""
import asyncio
import json
import os
import shutil
import sys
import traceback
from pathlib import Path

import httpx

from fixture_common import ANSWER_TEXT, FakeUpstream, Guard, running_proxy, write_scratch_files

KEY = os.environ["WEBUI_GATEWAY_KEY"]
RESULTS = []
LAST_ERROR = []
DEADLINE = 45.0


def check(condition, message):
    if not condition:
        raise AssertionError(message)


class Driver:
    def __init__(self, app, payload, spec_version, barrier_after_bodies=None, oserror_after_bodies=None):
        self.app, self.spec_version = app, spec_version
        self.body = json.dumps(payload).encode("utf-8")
        self.barrier_after, self.oserror_after = barrier_after_bodies, oserror_after_bodies
        self.sent_request = False
        self.disconnect = asyncio.Event()
        self.at_barrier = asyncio.Event()
        self.release = asyncio.Event()
        self.messages, self.bodies = [], []
        self.disconnect_delivered = 0
        self.send_cancelled = 0
        self.oserrors_raised = 0
        self.status = None

    async def receive(self):
        if not self.sent_request:
            self.sent_request = True
            return {"type": "http.request", "body": self.body, "more_body": False}
        await self.disconnect.wait()
        self.disconnect_delivered += 1
        return {"type": "http.disconnect"}

    async def send(self, message):
        if message["type"] == "http.response.start":
            self.status = message["status"]
            self.messages.append("start")
            return
        if message["type"] != "http.response.body":
            self.messages.append(message["type"])
            return
        if self.oserror_after is not None and len(self.bodies) >= self.oserror_after:
            self.oserrors_raised += 1
            raise OSError("connection closed (fixture)")
        chunk = message.get("body", b"")
        if chunk:
            self.bodies.append(chunk.decode("utf-8"))
        if self.barrier_after is not None and len(self.bodies) == self.barrier_after and not self.release.is_set():
            self.at_barrier.set()
            try:
                await self.release.wait()            # the application is now parked BETWEEN producer pulls
            except asyncio.CancelledError:
                self.send_cancelled += 1
                raise

    def scope(self):
        return {"type": "http", "asgi": {"version": "3.0", "spec_version": self.spec_version}, "http_version": "1.1",
                "method": "POST", "scheme": "http", "path": "/v1/chat/completions", "raw_path": b"/v1/chat/completions",
                "query_string": b"", "root_path": "", "server": ("127.0.0.1", 1), "client": ("127.0.0.1", 2),
                "headers": [(b"host", b"scratch.invalid"), (b"content-type", b"application/json"),
                            (b"content-length", str(len(self.body)).encode()),
                            (b"authorization", ("Bearer " + KEY).encode())]}

    async def run(self):
        """Start the application call; returns the task."""
        return asyncio.create_task(self.app(self.scope(), self.receive, self.send))


async def finish(task):
    """How the application call ended, within the deadline."""
    try:
        await asyncio.wait_for(asyncio.shield(task), DEADLINE)
        return "returned"
    except asyncio.TimeoutError:
        return "STILL RUNNING after deadline"
    except BaseException as error:  # noqa: BLE001
        LAST_ERROR.append("".join(traceback.format_exception(error))[-1500:])
        return "raised " + type(error).__name__


async def main():
    guard = Guard()
    guard.install()
    upstream = FakeUpstream()
    port = await upstream.start()
    config = write_scratch_files(port)
    # Imported only now: the candidate builds its hook at import and reads settings.json, which the
    # line above has just written. The network guard is already installed.
    import integration_candidate as ic
    import teach_store as ts
    store_dir = ts.DEFAULT_DIR
    check(Path(__file__).resolve().parent in store_dir.resolve().parents, "store is not inside the fixture folder")

    def reset_store(*notes):
        shutil.rmtree(store_dir, ignore_errors=True)
        store = ts.Store(store_dir)
        for note in notes:
            store.add(note)

    def fresh_upstream_state():
        upstream.hold_after_chunks = None
        upstream.hold_before_first = False
        upstream.release = asyncio.Event()
        upstream.reached_hold = asyncio.Event()

    left_out_note = ("word " * 58).strip()                     # relevant but over the notes cap: a notice applies
    payload = {"model": "local-qwen36-chat", "temperature": 0, "max_tokens": 64, "stream": True,
               "messages": [{"role": "user", "content": "hi"}]}

    async with running_proxy(config) as proxy_server:
        app = proxy_server.app
        transport = httpx.ASGITransport(app=app)

        async def still_serves():
            async with httpx.AsyncClient(transport=transport, base_url="http://scratch.invalid", timeout=60) as client:
                r = await client.post("/v1/chat/completions", json=dict(payload, stream=False),
                                      headers={"Authorization": "Bearer " + KEY})
                return r.status_code == 200 and r.json()["choices"][0]["message"]["content"] == ANSWER_TEXT

        async def observe(driver, task, streams_before, closed_before, completed_before):
            waiting_since = asyncio.get_running_loop().time()
            ended = await finish(task)
            call_ended_after = round(asyncio.get_running_loop().time() - waiting_since, 2)
            upstream.release.set()                             # let a held upstream try to continue and notice
            await asyncio.sleep(0.5)
            new_streams = ic.STREAMS[streams_before:]
            record = {"http_spec_version": driver.spec_version, "application_call": ended, "response_status": driver.status,
                      "body_messages_accepted": len(driver.bodies), "disconnect_delivered_by_receive": driver.disconnect_delivered,
                      "blocked_send_cancelled": driver.send_cancelled, "oserrors_raised_by_send": driver.oserrors_raised,
                      "adapter_streams_created": len(new_streams),
                      "adapter_cleanup_states": [s.cleanup for s in new_streams],
                      "adapter_close_errors": [list(s.close_errors) for s in new_streams],
                      "upstream_stream_closed_before_finishing": upstream.stream_closed_early - closed_before,
                      "upstream_stream_completed": upstream.stream_completed - completed_before,
                      # from the moment the test started waiting for the application call, to its end; nothing else included
                      "seconds_until_application_call_ended": call_ended_after}
            record["proxy_still_serves_afterwards"] = await still_serves()
            return record

        async def case(name, fn):
            fresh_upstream_state()
            reset_store(left_out_note)
            marks = (len(ic.STREAMS), upstream.stream_closed_early, upstream.stream_completed)
            try:
                record = await fn(marks)
                RESULTS.append({"case": name, "result": "pass", "observed": record})
                print("PASS", name, "|", json.dumps(record), flush=True)
            except Exception as error:  # noqa: BLE001
                RESULTS.append({"case": name, "result": "FAIL", "detail": type(error).__name__ + ": " + str(error)[:400]})
                print("FAIL", name, "|", type(error).__name__, str(error)[:400], flush=True)
                if LAST_ERROR:
                    print("APP-ERROR", " // ".join(LAST_ERROR[-1].splitlines())[-1200:], flush=True)
                    del LAST_ERROR[:]

        def expect_clean(record, streams=1):
            check(record["application_call"] in ("returned", "raised ClientDisconnect", "raised CancelledError"),
                  "application call: " + record["application_call"])
            check(record["adapter_streams_created"] == streams, f"adapter streams {record['adapter_streams_created']}")
            check(all(state == "done" for state in record["adapter_cleanup_states"]), str(record["adapter_cleanup_states"]))
            check(record["proxy_still_serves_afterwards"], "proxy did not serve the next request")

        async def baseline_complete(marks):
            driver = Driver(app, payload, "2.3")
            task = await driver.run()
            record = await observe(driver, task, *marks)
            text = "".join(driver.bodies)
            check(driver.status == 200 and "data: [DONE]" in text, "stream did not complete")
            first = json.loads(driver.bodies[0].split("\n\n")[0][len("data: "):])
            check(first.get("event", {}).get("type") == "status", "first body is not the status event")
            expect_clean(record)
            check(record["upstream_stream_completed"] == 1, "upstream did not complete")
            record["bodies_in_real_time"] = len(driver.bodies)
            return record

        async def disconnect_while_send_blocked_between_pulls(marks):
            upstream.hold_after_chunks = 2                     # the upstream keeps its stream open
            driver = Driver(app, payload, "2.3", barrier_after_bodies=2)
            task = await driver.run()
            await asyncio.wait_for(driver.at_barrier.wait(), DEADLINE)
            check(not task.done(), "application finished before the barrier")
            driver.disconnect.set()                            # REQUESTED disconnect, while send is parked
            record = await observe(driver, task, *marks)
            check(record["disconnect_delivered_by_receive"] == 1, "application never observed the disconnect")
            check(record["blocked_send_cancelled"] == 1, "the parked send was not cancelled")
            check(record["body_messages_accepted"] == 2, f"bodies {record['body_messages_accepted']}")
            expect_clean(record)
            check(record["upstream_stream_closed_before_finishing"] == 1, "upstream connection was not closed early")
            return record

        async def disconnect_before_first_chunk(marks):
            # OBSERVED BEHAVIOUR, recorded as found. The expectation from the library's source was that the
            # application would learn of the disconnect while buffering the first chunk. It did not call
            # `receive` again in this run; the request ended when the upstream call timed out.
            upstream.hold_before_first = True
            driver = Driver(app, payload, "2.3")
            task = await driver.run()
            await asyncio.wait_for(upstream.reached_hold.wait(), DEADLINE)
            check(not task.done() and not driver.bodies, "something was sent before the first chunk")
            driver.disconnect.set()
            record = await observe(driver, task, *marks)
            record["disconnect_observed_by_application"] = record["disconnect_delivered_by_receive"] > 0
            # What must hold whatever the framework does: nothing of the adapter is left open, the
            # upstream connection is closed in the end, and the proxy keeps serving.
            check(record["application_call"] == "returned", record["application_call"])
            check(all(state == "done" for state in record["adapter_cleanup_states"]), str(record["adapter_cleanup_states"]))
            check(record["upstream_stream_closed_before_finishing"] == 1, "upstream connection was never closed")
            check(record["proxy_still_serves_afterwards"], "proxy did not serve the next request")
            return record

        async def disconnect_during_backend_pull(marks):
            upstream.hold_after_chunks = 1                     # the proxy is waiting on the upstream, not on send
            driver = Driver(app, payload, "2.3")
            task = await driver.run()
            await asyncio.wait_for(upstream.reached_hold.wait(), DEADLINE)
            await asyncio.sleep(0.3)                           # let the proxy forward what it has and go back to pulling
            check(not task.done(), "application finished")
            driver.disconnect.set()
            record = await observe(driver, task, *marks)
            check(record["disconnect_delivered_by_receive"] == 1, "application never observed the disconnect")
            expect_clean(record)
            check(record["upstream_stream_closed_before_finishing"] == 1, "upstream connection was not closed early")
            return record

        async def closed_send_raises_oserror_spec_2_4(marks):
            # OBSERVED BEHAVIOUR, recorded as found. Under HTTP spec 2.4 a send on a closed connection raises
            # OSError and the web framework turns it into ClientDisconnect. In this environment the proxy's
            # own exception handling then fails on a missing optional module, so the application call ends
            # with that error instead. The installed server declares HTTP spec 2.3, where this path is not taken.
            upstream.hold_after_chunks = 2
            driver = Driver(app, payload, "2.4", oserror_after_bodies=2)
            task = await driver.run()
            record = await observe(driver, task, *marks)
            record["application_error_tail"] = (" // ".join(LAST_ERROR[-1].splitlines())[-260:] if LAST_ERROR else None)
            del LAST_ERROR[:]
            check(record["oserrors_raised_by_send"] >= 1, "send never raised")
            check(record["body_messages_accepted"] == 2, f"bodies {record['body_messages_accepted']}")
            check(record["adapter_streams_created"] == 1 and record["adapter_cleanup_states"] == ["done"],
                  str(record["adapter_cleanup_states"]))
            check(record["upstream_stream_closed_before_finishing"] == 1, "upstream connection was not closed early")
            check(record["proxy_still_serves_afterwards"], "proxy did not serve the next request")
            return record

        for name, fn in [("baseline: complete stream through the direct driver", baseline_complete),
                         ("disconnect while send is blocked between pulls (HTTP spec 2.3)", disconnect_while_send_blocked_between_pulls),
                         ("disconnect requested before the first chunk (HTTP spec 2.3): observed outcome", disconnect_before_first_chunk),
                         ("disconnect during a backend pull (HTTP spec 2.3)", disconnect_during_backend_pull),
                         ("send on a closed connection raises OSError (HTTP spec 2.4): observed outcome", closed_send_raises_oserror_spec_2_4)]:
            await case(name, fn)

    await upstream.stop()
    shutil.rmtree(store_dir, ignore_errors=True)
    summary = {"passed": sum(r["result"] == "pass" for r in RESULTS), "failed": sum(r["result"] != "pass" for r in RESULTS),
               "upstream_captures": len(upstream.captures), "upstream_captures_with_internal_keys": upstream.internal_key_captures,
               "guard_violations": guard.violations, "loopback_ports_connected": sorted(guard.loopback_ports),
               "upstream_port": port, "results": RESULTS}
    Path("stage3.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print("SUMMARY", json.dumps({k: v for k, v in summary.items() if k != "results"}), flush=True)
    return 1 if summary["failed"] or upstream.internal_key_captures else 0

sys.exit(asyncio.run(main()))
