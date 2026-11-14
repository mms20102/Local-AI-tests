"""Count real tokens for every CODE-Q1 prompt and reference answer. Offline; no model is run.

    python token_preflight.py --tokenizer <path to the model's tokenizer.json> [--system "text"]

Needs the `tokenizers` package (any environment that already has it). It reads the tokenizer
file and the fixtures, and prints one JSON document. Nothing is sent anywhere.

What is counted, per task:
  prompt_tokens     the request as the model would see it under ChatML framing:
                    <|im_start|>system\\n{system}<|im_end|>\\n<|im_start|>user\\n{prompt}<|im_end|>\\n<|im_start|>assistant\\n
  reference_tokens  the reference answer in the frozen answer format (one fenced block per file),
                    plus one end-of-turn token. The model's own answer may be longer or shorter.

Assumption to verify before relying on the numbers: that the serving engine frames messages with
plain ChatML and adds nothing else (no default system text, no tool or thinking preamble). The
engine's actual template was not read for this script.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_SYSTEM = "Provide concise code for review only. Never execute it."


def chatml(system: str, user: str) -> str:
    parts = []
    if system:
        parts.append(f"<|im_start|>system\n{system}<|im_end|>\n")
    parts.append(f"<|im_start|>user\n{user}<|im_end|>\n<|im_start|>assistant\n")
    return "".join(parts)


def answer_text(files: dict[str, str], multi: bool) -> str:
    blocks = []
    for name, code in files.items():
        head = f"# file: {name}\n" if multi else ""
        blocks.append("```python\n" + head + code + "```")
    return "\n\n".join(blocks) + "<|im_end|>"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--tokenizer", type=Path, required=True)
    parser.add_argument("--system", default=DEFAULT_SYSTEM)
    parser.add_argument("--context", type=int, default=2048)
    parser.add_argument("--output-ceiling", type=int, default=256)
    args = parser.parse_args()
    from tokenizers import Tokenizer
    tokenizer = Tokenizer.from_file(str(args.tokenizer))

    def count(text: str) -> int:
        return len(tokenizer.encode(text, add_special_tokens=False).ids)

    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    rows, worst_prompt, worst_answer = {}, 0, 0
    for task_id, entry in manifest["tasks"].items():
        base = ROOT / "fixtures" / task_id
        prompt = (base / "prompt.txt").read_text(encoding="utf-8")
        files = {p.name: p.read_text(encoding="utf-8") for p in sorted((base / "reference").iterdir())}
        prompt_tokens = count(chatml(args.system, prompt))
        reference_tokens = count(answer_text(files, len(entry["files"]) > 1))
        rows[task_id] = {
            "prompt_chars": len(prompt), "prompt_utf8_bytes": len(prompt.encode("utf-8")),
            "prompt_tokens": prompt_tokens, "reference_tokens": reference_tokens,
            "prompt_plus_ceiling": prompt_tokens + args.output_ceiling,
            "fits_context": prompt_tokens + args.output_ceiling <= args.context,
            "reference_fits_ceiling": reference_tokens <= args.output_ceiling,
            "reference_share_of_ceiling": round(reference_tokens / args.output_ceiling, 2)}
        worst_prompt = max(worst_prompt, prompt_tokens)
        worst_answer = max(worst_answer, reference_tokens)
    print(json.dumps({
        "fixture_revision": manifest["fixture_revision"], "context": args.context,
        "output_ceiling": args.output_ceiling, "system_tokens": count(args.system),
        "framing": "ChatML (assumed, not read from the engine)",
        "largest_prompt_tokens": worst_prompt, "largest_reference_tokens": worst_answer,
        "all_prompts_fit": all(r["fits_context"] for r in rows.values()),
        "all_references_fit": all(r["reference_fits_ceiling"] for r in rows.values()),
        "tasks": rows}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
