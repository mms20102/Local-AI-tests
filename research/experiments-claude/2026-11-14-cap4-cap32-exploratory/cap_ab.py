"""Exploratory cap 4 vs cap 32 comparison through the existing launchers and draft helper.

NOT the PC worker's schema-4 plan: no identity pinning, no per-request resource surveillance.
One model stack at a time. Each arm: fresh stack start, one unscored warm-up, then the twelve
CODE-Q1 prompts through the gateway with the project's own draft helper (max 256 tokens).
Model output is never executed; answers get the static structure grade only.

    python cap_ab.py --smoke          one request on whatever stack is running; changes nothing
    python cap_ab.py --run A B B A    full run; stops the running stack, restores cap 32 at the end
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(r"C:\Users\User\Documents\TryOut-Project\private-ai\local-chat")
PY = ROOT.parent / "runtimes" / "cpython-3.12.16-20261110" / "python" / "python.exe"
SUITE = Path(r"C:\Users\User\Documents\TryOut-Project\Local-AI-tests\research\coding-quality-v1")
OUT = Path(__file__).resolve().parent / "cap-ab"
PORTS = (8000, 4001, 8080)
ARMS = {"A": 4, "B": 32}
NO_WINDOW = 0x08000000
sys.path.insert(0, str(SUITE))
import grade  # noqa: E402  (static grading only)


def now() -> str:
    return datetime.datetime.now().strftime("%H:%M:%S")


def listening() -> list[int]:
    found = []
    for port in PORTS:
        with socket.socket() as sock:
            sock.settimeout(0.5)
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                found.append(port)
    return found


def health() -> bool:
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open("http://127.0.0.1:8080/health", timeout=3) as response:
            return response.status == 200
    except OSError:
        return False


def newest_session() -> Path:
    return max((p for p in (ROOT / ".runtime" / "sessions").iterdir() if p.is_dir()), key=lambda p: p.name)


def memory() -> dict:
    script = ("$c=(Get-Counter '\\Memory\\Committed Bytes','\\Memory\\Commit Limit','\\Memory\\Available MBytes').CounterSamples;"
              "$p=Get-Process qwen36 -ErrorAction SilentlyContinue | Select-Object -First 1;"
              "@{committed=$c[0].CookedValue;limit=$c[1].CookedValue;available_mb=$c[2].CookedValue;"
              "engine_private=$(if($p){$p.PrivateMemorySize64}else{0});engine_ws=$(if($p){$p.WorkingSet64}else{0})} | ConvertTo-Json -Compress")
    try:
        raw = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
                             capture_output=True, text=True, timeout=60, creationflags=NO_WINDOW).stdout
        d = json.loads(raw)
        gib = 2 ** 30
        return {"commit_gib": round(d["committed"] / gib, 2), "commit_limit_gib": round(d["limit"] / gib, 2),
                "available_gib": round(d["available_mb"] / 1024, 2),
                "engine_private_gib": round(d["engine_private"] / gib, 2), "engine_ws_gib": round(d["engine_ws"] / gib, 2)}
    except (OSError, ValueError, KeyError, subprocess.SubprocessError):
        return {}


def stop_stack(timeout: int = 150) -> None:
    """Stop whatever stack is running through the launcher's own path (web UI stop file)."""
    if not listening():
        return
    session = newest_session()
    (session / "webui.stop").write_text("stop\n", encoding="utf-8")
    started = time.monotonic()
    fallback_used = False
    while time.monotonic() < started + timeout:
        if not listening() and (session / "shutdown.json").exists():
            time.sleep(2)
            return
        if not fallback_used and time.monotonic() > started + 60 and 8080 not in listening():
            fallback_used = kill_hung_webui()
            print(now(), "web UI process hung after stop; ended it so the launcher can clean up", flush=True)
        time.sleep(2)
    raise RuntimeError("stack did not stop; ports still open: " + str(listening()))


def kill_hung_webui() -> bool:
    """Fallback seen to be needed once: the web UI stops listening but its process does not exit,
    so the launcher never runs its cleanup. End only the web UI service host; the launcher then
    stops the rest itself. This is what the launcher does on Ctrl+C after 45 s."""
    script = ("Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
              "Where-Object { $_.CommandLine -like '*service_host.py*webui*' } | ForEach-Object { $_.ProcessId }")
    out = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
                         capture_output=True, text=True, timeout=60, creationflags=NO_WINDOW).stdout.split()
    for pid in out:
        subprocess.run(["taskkill", "/PID", pid, "/T", "/F"], capture_output=True, timeout=30, creationflags=NO_WINDOW)
    return bool(out)


def start_stack(cap: int, timeout: int = 400) -> tuple[subprocess.Popen, Path, float]:
    if listening():
        raise RuntimeError("ports are busy before start")
    before = {p.name for p in (ROOT / ".runtime" / "sessions").iterdir()}
    log = open(OUT / f"launcher-cap{cap}-{int(time.time())}.log", "w", encoding="utf-8")
    started = time.monotonic()
    proc = subprocess.Popen([str(PY), "-B", "workbench.py", "--start", "--ram-cache-slots", str(cap)],
                            cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, creationflags=NO_WINDOW)
    deadline = started + timeout
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError("launcher exited during startup")
        if health():
            new = [p for p in (ROOT / ".runtime" / "sessions").iterdir() if p.name not in before]
            return proc, max(new, key=lambda p: p.name), round(time.monotonic() - started, 1)
        time.sleep(3)
    raise RuntimeError("stack not ready in time")


def ask(prompt: str, max_tokens: int = 256) -> dict:
    drafts = ROOT / ".runtime" / "drafts"
    before = {p.name for p in drafts.glob("*.json")}
    started = time.monotonic()
    done = subprocess.run([str(PY), "-B", "code_draft.py", "--task", prompt, "--max-tokens", str(max_tokens)],
                          cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
                          timeout=600, creationflags=NO_WINDOW)
    wall = round(time.monotonic() - started, 2)
    new = sorted(p for p in drafts.glob("*.json") if p.name not in before)
    if not new:
        return {"state": "no_draft_saved", "wall_seconds": wall, "helper_exit": done.returncode,
                "helper_tail": (done.stdout + done.stderr)[-300:]}
    data = json.loads(new[-1].read_text(encoding="utf-8"))
    return {"state": data.get("state"), "finish_reason": data.get("finish_reason"), "truncated": data.get("truncated"),
            "elapsed_seconds": data.get("elapsed_seconds"), "first_text_seconds": data.get("first_text_seconds"),
            "wall_seconds": wall, "content": data.get("content") or "", "helper_exit": done.returncode}


def engine_counters(session: Path) -> dict:
    text = (session / "colibri.log").read_text(encoding="utf-8", errors="replace")
    out = {}
    chain = re.findall(r"chain: (\d+) forwards.*?([\d.]+) ms waiting for the device, ([\d.]+) ms of routed experts on the host", text)
    if chain:
        out.update(forwards=int(chain[-1][0]), device_wait_s=round(float(chain[-1][1]) / 1000, 1),
                   host_expert_s=round(float(chain[-1][2]) / 1000, 1))
    tier = re.findall(r"CPU RAM hits (\d+), disk loads (\d+)", text)
    if tier:
        out.update(ram_hits=int(tier[-1][0]), disk_loads=int(tier[-1][1]))
    header = re.search(r"cache=(\d+)/layer", text)
    if header:
        out["cache_slots"] = int(header.group(1))
    out["chat_requests"] = text.count('"POST /v1/chat/completions')
    return out


def tasks() -> list[tuple[str, str]]:
    ids = sorted(grade.manifest()["tasks"])
    return [(i, (SUITE / "fixtures" / i / "prompt.txt").read_text(encoding="utf-8")) for i in ids]


def one_request(task_id: str, prompt: str) -> dict:
    got = ask(prompt)
    row = {k: v for k, v in got.items() if k != "content"}
    content = got.get("content", "")
    row["output_chars"] = len(content)
    row["output_sha256"] = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16] if content else None
    if content:
        result = grade.static_grade(grade.load_task(task_id), {"content": content, "finish_reason": got.get("finish_reason"),
                                                              "truncated": got.get("truncated")})
        row.update(transport=result["transport"], structure=result["structure"], problems=result["problems"])
    return row


def save(result: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    temp = OUT / "result.json.tmp"
    temp.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    temp.replace(OUT / "result.json")


def run(order: list[str]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    result = {"started": now(), "order": order, "arms": ARMS, "engine": "Colibri 2.0.0 (existing launchers)",
              "max_tokens": 256, "suite": "CODE-Q1 revision 2", "runs": [], "status": "running"}
    save(result)
    proc = None
    try:
        print(now(), "stopping the running stack", flush=True)
        stop_stack()
        for index, arm in enumerate(order, 1):
            cap = ARMS[arm]
            record = {"run": index, "arm": arm, "cap": cap, "memory_before_start": memory(), "requests": []}
            result["runs"].append(record)
            if record["memory_before_start"].get("available_gib", 99) < 8:
                raise RuntimeError("less than 8 GiB RAM available before an arm; stopping")
            print(now(), f"run {index}: starting cap {cap}", flush=True)
            proc, session, record["startup_seconds"] = start_stack(cap)
            record["session"] = session.name
            record["memory_idle"] = memory()
            warm = ask("Reply exactly READY.", max_tokens=16)
            record["warmup"] = {k: v for k, v in warm.items() if k != "content"}
            save(result)
            for task_id, prompt in tasks():
                row = dict(task=task_id, **one_request(task_id, prompt))
                record["requests"].append(row)
                save(result)
                print(now(), f"  {arm} {task_id}: {row.get('elapsed_seconds')} s, {row.get('finish_reason')}, "
                             f"structure {row.get('structure')}", flush=True)
            record["memory_after"] = memory()
            record["engine"] = engine_counters(session)
            save(result)
            stop_stack()
            proc.wait(timeout=120)
            proc = None
        result["status"] = "complete"
    except BaseException as error:               # includes Ctrl+C: always try to restore
        result["status"] = "aborted: " + repr(error)[:300]
        print(now(), "ABORTED", repr(error)[:300], flush=True)
    finally:
        save(result)
        try:
            stop_stack()
        except Exception as error:               # noqa: BLE001
            print(now(), "could not stop cleanly:", error, flush=True)
        if not listening():
            subprocess.Popen(["cmd.exe", "/c", "start", "Local Chat - Colibri 2.0.0", "Start-Fast-Local-Chat.cmd"],
                             cwd=ROOT, creationflags=NO_WINDOW)
            for _ in range(120):
                if health():
                    break
                time.sleep(3)
        result["restored_fast_stack"] = health()
        result["finished"] = now()
        save(result)
        print(now(), "finished; fast stack healthy:", result["restored_fast_stack"], flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--run", nargs="+", choices=sorted(ARMS))
    args = parser.parse_args()
    if args.smoke:
        task_id, prompt = tasks()[9]              # F01
        print(json.dumps(dict(task=task_id, **one_request(task_id, prompt)), indent=1))
        print(json.dumps(memory()), json.dumps(engine_counters(newest_session())))
        return 0
    if args.run:
        run(args.run)
        return 0
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
