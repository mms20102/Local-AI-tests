"""Step 1 of the rehearsal: download a small Qwen and a public, human-written dataset; make fixed splits.
Runs on the CPU and needs no GPU, so the chat can stay up while it runs."""
import json
import random
from pathlib import Path

from datasets import load_dataset
from huggingface_hub import snapshot_download

HERE = Path(__file__).resolve().parent
MODEL = "Qwen/Qwen3-0.6B"                        # official Qwen repository, Apache-2.0
DATASET = "databricks/databricks-dolly-15k"      # written by Databricks employees, CC BY-SA 3.0

model_dir = snapshot_download(MODEL, local_dir=HERE / "model",
                              allow_patterns=["*.json", "*.safetensors", "*.txt", "LICENSE", "*.jinja"])
rows = load_dataset(DATASET, split="train")
picked = [r for r in rows if not r["context"].strip() and 20 <= len(r["response"]) <= 600 and len(r["instruction"]) <= 300]
random.Random(20261115).shuffle(picked)
train, held_out = picked[:1000], picked[1000:1100]
for name, part in (("train", train), ("held_out", held_out)):
    with open(HERE / f"{name}.jsonl", "w", encoding="utf-8") as out:
        for r in part:
            out.write(json.dumps({"instruction": r["instruction"], "response": r["response"], "category": r["category"]},
                                 ensure_ascii=False) + "\n")
size = sum(p.stat().st_size for p in Path(model_dir).rglob("*") if p.is_file())
print(json.dumps({"model": MODEL, "model_bytes": size, "dataset": DATASET, "usable_rows": len(picked),
                  "train": len(train), "held_out": len(held_out)}))
