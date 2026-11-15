"""Step 2 of the rehearsal: LoRA fine-tuning of the small Qwen on the GPU, with before/after measurements.

Measures, on 100 held-out questions the model never trains on:
  - the loss on the reference answers before and after training (lower = closer to the dataset's answers);
  - three sample answers before and after.
Only small add-on matrices (LoRA) are trained; the model's own weights stay frozen."""
import json
import math
import sys
import time
from pathlib import Path

import torch
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer

HERE = Path(__file__).resolve().parent
MAX_LEN, BATCH, EPOCHS, LR, RANK = 384, 4, 1, 2e-4, 16
torch.manual_seed(20261115)
device = "cuda" if torch.cuda.is_available() else "cpu"
if device != "cuda":
    sys.exit("no GPU visible to PyTorch; not training on the CPU")

tokenizer = AutoTokenizer.from_pretrained(HERE / "model")
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
model = AutoModelForCausalLM.from_pretrained(HERE / "model", torch_dtype=torch.bfloat16).to(device)


def load(name):
    return [json.loads(line) for line in open(HERE / f"{name}.jsonl", encoding="utf-8")]


def prompt_text(row):
    messages = [{"role": "user", "content": row["instruction"]}]
    try:
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    except TypeError:
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)


def encode(row):
    """Token ids and labels. Only the answer counts towards the loss; the question part is masked out."""
    prompt = tokenizer(prompt_text(row), add_special_tokens=False)["input_ids"]
    answer = tokenizer(row["response"] + tokenizer.eos_token, add_special_tokens=False)["input_ids"]
    ids = (prompt + answer)[:MAX_LEN]
    labels = ([-100] * len(prompt) + answer)[:MAX_LEN]
    return ids, labels


def batches(rows, shuffle):
    order = torch.randperm(len(rows)).tolist() if shuffle else list(range(len(rows)))
    for start in range(0, len(order), BATCH):
        encoded = [encode(rows[i]) for i in order[start:start + BATCH]]
        width = max(len(ids) for ids, _ in encoded)
        ids = torch.full((len(encoded), width), tokenizer.pad_token_id)
        labels = torch.full((len(encoded), width), -100)
        mask = torch.zeros((len(encoded), width), dtype=torch.long)
        for n, (i, l) in enumerate(encoded):
            ids[n, :len(i)], labels[n, :len(l)], mask[n, :len(i)] = torch.tensor(i), torch.tensor(l), 1
        yield ids.to(device), mask.to(device), labels.to(device)


@torch.no_grad()
def held_out_loss(net, rows):
    net.eval()
    total, count = 0.0, 0
    for ids, mask, labels in batches(rows, shuffle=False):
        out = net(input_ids=ids, attention_mask=mask, labels=labels)
        tokens = int((labels != -100).sum())
        total += float(out.loss) * tokens
        count += tokens
    return total / count


@torch.no_grad()
def answer(net, row):
    net.eval()
    ids = tokenizer(prompt_text(row), return_tensors="pt", add_special_tokens=False).to(device)
    out = net.generate(**ids, max_new_tokens=80, do_sample=False)
    return tokenizer.decode(out[0][ids["input_ids"].shape[1]:], skip_special_tokens=True).strip()


train, held_out = load("train"), load("held_out")
result = {"device": torch.cuda.get_device_name(0), "torch": torch.__version__,
          "base_parameters": sum(p.numel() for p in model.parameters()),
          "settings": {"max_len": MAX_LEN, "batch": BATCH, "epochs": EPOCHS, "lr": LR, "lora_rank": RANK,
                       "train_rows": len(train), "held_out_rows": len(held_out)}}
result["held_out_loss_before"] = round(held_out_loss(model, held_out), 4)
samples = held_out[:3]
result["samples"] = [{"question": r["instruction"], "reference": r["response"], "before": answer(model, r)} for r in samples]
print("before:", result["held_out_loss_before"], flush=True)

model = get_peft_model(model, LoraConfig(r=RANK, lora_alpha=32, lora_dropout=0.05, task_type="CAUSAL_LM",
                                         target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]))
result["trained_parameters"] = sum(p.numel() for p in model.parameters() if p.requires_grad)
optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=LR)
steps_total = EPOCHS * math.ceil(len(train) / BATCH)
schedule = torch.optim.lr_scheduler.LambdaLR(optimizer, lambda step: max(0.0, 1 - step / steps_total))
torch.cuda.reset_peak_memory_stats()
started, step, curve = time.monotonic(), 0, []
for _ in range(EPOCHS):
    model.train()
    for ids, mask, labels in batches(train, shuffle=True):
        loss = model(input_ids=ids, attention_mask=mask, labels=labels).loss
        if not torch.isfinite(loss):
            sys.exit(f"loss is not finite at step {step}")
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        schedule.step()
        optimizer.zero_grad()
        step += 1
        if step % 25 == 0 or step == steps_total:
            curve.append({"step": step, "train_loss": round(float(loss), 4)})
            print(curve[-1], flush=True)
result.update(train_seconds=round(time.monotonic() - started, 1), steps=step, train_loss_curve=curve,
              peak_gpu_memory_mb=round(torch.cuda.max_memory_allocated() / 1048576))
result["held_out_loss_after"] = round(held_out_loss(model, held_out), 4)
for sample, row in zip(result["samples"], samples):
    sample["after"] = answer(model, row)
model.save_pretrained(HERE / "adapter")
result["adapter_bytes"] = sum(p.stat().st_size for p in (HERE / "adapter").rglob("*") if p.is_file())
(HERE / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("after:", result["held_out_loss_after"], "seconds:", result["train_seconds"], "peak MB:", result["peak_gpu_memory_mb"])
