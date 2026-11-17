"""Start a fixture script as a NEW process with an explicit synthetic environment.

    python launch.py <mode> <script.py> [args...]      mode: bound | nocounter

Nothing is inherited beyond a few named operating-system variables. No real key, no local.env, no
project setting is read. The interpreter is the gateway environment's, used read-only (-B: no bytecode).
"""
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PYTHON = os.environ.get("SCRATCH_PYTHON", sys.executable)   # an interpreter that has LiteLLM 1.108.5 installed
mode, script, rest = sys.argv[1], sys.argv[2], sys.argv[3:]

env = {name: os.environ[name] for name in ("PATH", "PATHEXT", "SYSTEMROOT", "WINDIR", "COMSPEC", "TEMP", "TMP",
                                           "USERPROFILE", "APPDATA", "LOCALAPPDATA", "PROGRAMDATA", "SYSTEMDRIVE",
                                           "HOMEDRIVE", "HOMEPATH") if name in os.environ}
limits = {"model_alias": "local-qwen36-chat", "upstream_model": "qwen3.6-colibri", "context_tokens": 2048,
          "default_output_tokens": 256, "max_output_tokens": 256, "context_reserve_units": 256,
          "per_message_overhead_units": 32, "max_messages": 32, "max_request_bytes": 32768,
          "max_concurrent_requests": 1, "request_timeout_seconds": 120, "temperature": 0}
env.update({
    "PYTHONPATH": str(HERE / "app") + os.pathsep + str(HERE), "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1",
    "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8", "NO_PROXY": "127.0.0.1,localhost,::1",
    "TRYOUT_LIMITS_JSON": json.dumps(limits),
    "WEBUI_GATEWAY_KEY": "synthetic-gateway-key-for-the-scratch-fixture-0001",
    "LITELLM_MASTER_KEY": "sk-synthetic-master-key-for-the-scratch-fixture-only-000000000000000000000001",
    "SCRATCH_UPSTREAM_KEY": "synthetic-upstream-key-for-the-scratch-fixture",
    "ALLOW_CHAT_REQUESTS": "true", "LITELLM_MODE": "PRODUCTION", "LITELLM_OFFLINE_MODE": "true",
    "LITELLM_LOCAL_MODEL_COST_MAP": "true", "LITELLM_LOG": "ERROR", "HF_HUB_OFFLINE": "1",
    "SCRATCH_MODE": mode,
})
if mode == "bound":
    # The profile the published counter is bound to, reported as a launcher would report it.
    sys.path.insert(0, str(HERE / "app"))
    import token_count
    env["TRYOUT_SERVED_PROFILE"] = json.dumps(token_count.PROFILE, sort_keys=True)
done = subprocess.run([PYTHON, "-B", str(HERE / script), *rest], cwd=HERE, env=env, timeout=600)
sys.exit(done.returncode)
