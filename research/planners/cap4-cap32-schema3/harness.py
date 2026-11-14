"""Offline benchmark planning/contracts only. No inference or generated-code execution."""
import argparse, hashlib, json, math
from pathlib import Path
PROTOCOL_SHA = "03f0b8b04c7a8f772d2890322b486917476f33af"
ARMS = {"A":4,"B":32}
CORRECTNESS_COVERAGE = {"format":"exact_fixture","edit":"exact_fixture","tool":"schema_only",
                      "function":"unverified","bugfix":"unverified","arabic":"unverified"}
TASKS = [
 {"id":"format","prompt":'Return exactly {"capital":"Paris"} and nothing else.'},
 {"id":"function","prompt":"Write Python unique_sorted(xs), returning sorted distinct integers. Code only."},
 {"id":"bugfix","prompt":"Fix maximum(xs), currently max(xs+[0]), to return the greatest integer, or None for empty input. Code only."},
 {"id":"edit","prompt":"Replace old_name with new_name in these lines, preserving everything else. Return only lines.\nold_name=1\nprint(old_name)\n# old_name"},
 {"id":"tool","prompt":"Use add to add 2 and 3, not prose.","tool_choice":"required",
  "tools":[{"type":"function","function":{"name":"add","description":"Add integers",
   "parameters":{"type":"object","properties":{"a":{"type":"integer"},"b":{"type":"integer"}},
   "required":["a","b"],"additionalProperties":False}}}]},
 {"id":"arabic","prompt":"\u0627\u0634\u0631\u062d \u0627\u0644\u0641\u0631\u0642 \u0628\u064a\u0646 \u0627\u0644\u0642\u0627\u0626\u0645\u0629 \u0648\u0627\u0644\u0645\u062c\u0645\u0648\u0639\u0629 \u0641\u064a \u0628\u0627\u064a\u062b\u0648\u0646 \u0628\u0627\u062e\u062a\u0635\u0627\u0631 \u062b\u0645 \u0627\u0643\u062a\u0628 \u062f\u0627\u0644\u0629 \u062a\u0639\u062f \u0627\u0644\u0639\u0646\u0627\u0635\u0631 \u0627\u0644\u0641\u0631\u064a\u062f\u0629."}]
# NEVER include hidden fixtures in requests. No execution adapter is supplied.
FIXTURES = {"function":[[[],[]],[[2,1,2],[1,2]],[[-1,0,-1],[-1,0]]],
 "bugfix":[[[],None],[[-4,-2],-2],[[0],0],[[1,5,2],5]],
 "tool_recovery":{"simulated_error":{"error":"synthetic_unavailable"},"expected":"explain failure without claiming success"}}
def digest(x):
 return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()).hexdigest()
def plan():
 rows=[]
 for pair in range(1,6):
  for arm in ("AB" if pair%2 else "BA"):
   start=f"p{pair}-{arm}"
   rows.append({"id":start+"-warmup","pair":pair,"arm":arm,"scored":False,"task":"warmup"})
   for task in TASKS:
    rows.append({"id":start+"-"+task["id"],"pair":pair,"arm":arm,"scored":True,
                 "task":task["id"],"prompt_hash":digest(task)})
 p={"schema":3,"protocol_sha":PROTOCOL_SHA,"arms":ARMS,"schedule":rows,"tasks":TASKS,
    "fixed":{"model":"Qwen3.6-35B-A3B","ctx":2048,"ngen":256,"kvslots":1,"vulkan":1,"cuda":0,
             "tier_gib":3,"omp_threads":8,"usage_save":0,"COLI_LOOKUP":None},
    "execution_supported":False,"stop_after_consecutive_infrastructure_faults":2,
    "invalid_conditions":["transport_error","deadline","cancelled","memory_pressure","truncated",
                          "identity_mismatch","history_mismatch","unrelated_traffic"]}
 p["stop_policy"] = {
  "immediate_stop_reasons":["cancelled","memory_pressure","identity_mismatch","history_mismatch","unrelated_traffic"],
  "consecutive_infrastructure_fault_reasons":["transport_error","deadline"],
  "consecutive_infrastructure_fault_limit":2,
  "truncation_resets_infrastructure_counter":True,
  "received_complete_response_resets_infrastructure_counter":True,
  "hash_mismatch_behavior":"fail_closed_without_mutating_raw_artifact"}
 p["eligible_pair_ceiling"]=10
 p["eligible_pair_ceiling_is_planned_not_passed"]=True
 p["correctness_coverage"] = {
  "task_labels":dict(CORRECTNESS_COVERAGE),
  "planned_measured_counts":{label:sum(r["scored"] and CORRECTNESS_COVERAGE[r["task"]]==label for r in rows)
                             for label in ("exact_fixture","schema_only","unverified")},
  "overall_no_regression_claim_supported":False,
  "full_semantic_execution_validated":False,
  "counts_are_planned_not_observed":True}
 p["plan_hash"]=digest(p)
 return p
def tool_fixture(call):
 if not isinstance(call,dict) or set(call)!={"name","arguments"} or call["name"]!="add":
  raise ValueError("Unknown/malformed tool")
 a=call["arguments"]
 if not isinstance(a,dict) or set(a)!={"a","b"} or any(type(v) is not int for v in a.values()):
  raise ValueError("Schema violation")
 if a!={"a":2,"b":3}: raise ValueError("Incorrect arguments")
 return {"simulated":True,"result":5}
def correctness(task,output):
 if task=="format":
  try: ok=type(output) is str and output=='{"capital":"Paris"}'
  except (TypeError,ValueError): ok=False
  return "pass" if ok else "fail"
 if task=="edit": return "pass" if output=="new_name=1\nprint(new_name)\n# new_name" else "fail"
 if task=="tool":
  try: tool_fixture(output)
  except ValueError: return "fail"
  return "schema_only"
 if task in ("function","bugfix","arabic"): return "unverified"
 if task=="warmup": return "unscored"
 raise ValueError("Unknown task")
REQUIRED={"id","plan_hash","state","output","correctness","total_seconds","ttft_seconds",
          "input_tokens","output_tokens","history_before_sha","history_after_sha","identity_sha",
          "invalid_reason","finish_reason","child_env_names"}
def valid_sha(value):
 return isinstance(value,str) and len(value)==64 and all(c in "0123456789abcdef" for c in value)
def validate_env_names(names):
 if not isinstance(names,list) or any(not isinstance(n,str) for n in names):
  raise ValueError("child_env_names must be a names-only list")
 if len(names)>128 or len(set(names))!=len(names): raise ValueError("Duplicate/oversized environment inventory")
 for n in names:
  if not n.isascii() or not n.isidentifier() or n!=n.upper() or not (n.startswith(("COLI_","OMP_")) or n=="USAGE_SAVE"):
   raise ValueError("Invalid environment name; values and unrelated names prohibited")
 if "COLI_LOOKUP" in names: raise ValueError("COLI_LOOKUP must be absent from resolved child environment")
 if not {"COLI_VULKAN","COLI_CUDA","COLI_VK_TIER_GB","OMP_NUM_THREADS","USAGE_SAVE"}<=set(names):
  raise ValueError("Missing required resolved environment names")
def coverage_summary(records,p):
 observed={r["id"]:r for r in records}
 counts={}
 for task in [t["id"] for t in TASKS]+["warmup"]:
  counts[task]={}
  for arm in ARMS:
   slots=[s for s in p["schedule"] if s["task"]==task and s["arm"]==arm]
   rows=[observed[s["id"]] for s in slots if s["id"] in observed]
   counts[task][arm]={"n_planned":len(slots),"n_observed":len(rows),
    "n_complete":sum(r["state"]=="complete" for r in rows),
    "n_complete_with_token_counts":sum(r["state"]=="complete" and r["input_tokens"] is not None and r["output_tokens"] is not None for r in rows),
    "n_failed":sum(r["state"]!="complete" for r in rows),
    "n_truncated":sum(r["finish_reason"]=="length" for r in rows),
    "n_unobserved":len(slots)-len(rows)}
 pairs=[]
 for task in TASKS:
  for pair in range(1,6):
   slots=[s for s in p["schedule"] if s["task"]==task["id"] and s["pair"]==pair]
   rows=[observed[s["id"]] for s in slots if s["id"] in observed]
   full=len(rows)==2
   complete=full and all(r["state"]=="complete" for r in rows)
   reasons=[]
   if not full: reasons.append("unobserved_arm")
   if any(r["state"]!="complete" for r in rows): reasons.append("failed_or_cancelled")
   if any(r["finish_reason"]=="length" for r in rows): reasons.append("truncated")
   if any(r["correctness"]=="fail" for r in rows): reasons.append("incorrect_fixture")
   category=CORRECTNESS_COVERAGE[task["id"]]
   if category!="exact_fixture": reasons.append(category)
   eligible=complete and category=="exact_fixture" and all(r["correctness"]=="pass" for r in rows)
   known=full and all(r["input_tokens"] is not None and r["output_tokens"] is not None for r in rows)
   comparable=known and rows[0]["input_tokens"]==rows[1]["input_tokens"] and rows[0]["output_tokens"]==rows[1]["output_tokens"]
   speed_reasons=list(reasons)
   if not known: speed_reasons.append("unknown_token_counts")
   elif not comparable: speed_reasons.append("unequal_input_or_output_token_counts")
   pairs.append({"task":task["id"],"pair":pair,"fully_observed":full,
                 "both_transport_complete":complete,"eligible_complete_pair":eligible,"exact_fixture_qualified":eligible,"speed_comparison_eligible":eligible and comparable,"exclusions":reasons,"speed_comparison_exclusions":speed_reasons})
 return {"measured_by_task_arm":{t["id"]:counts[t["id"]] for t in TASKS},"warmups_by_arm":counts["warmup"],
  "measured_denominator":60,"warmup_denominator":10,"pair_denominator":30,
  "eligible_pair_ceiling":10,"eligible_pair_ceiling_is_planned_not_passed":True,
  "count_relationships":{"n_truncated_subset_of":"n_failed","cancelled_included_in":"n_failed",
                         "n_complete_with_token_counts_requires":"both input_tokens and output_tokens known"},
  "exact_fixture_qualified_pairs":sum(x["exact_fixture_qualified"] for x in pairs),
  "speed_comparison_eligible_pairs":sum(x["speed_comparison_eligible"] for x in pairs),
  "speed_comparison_definition":"Exact fixture qualified, with known identical input and output counts across arms; no speed claim calculated.",
  "fully_observed_pairs":sum(x["fully_observed"] for x in pairs),
  "both_transport_complete_pairs":sum(x["both_transport_complete"] for x in pairs),
  "eligible_complete_pairs":sum(x["eligible_complete_pair"] for x in pairs),
  "eligible_definition":"Both arms complete and pass an exact fixture; excludes schema-only/unverified tasks.",
  "pairs":pairs,"overall_no_regression_claim_supported":False}
def validate_records(records,header):
 if not isinstance(records,list): raise ValueError("Expected list")
 p=plan()
 if not isinstance(header,dict) or set(header)!={"plan_hash","expected_history_sha","expected_identity_sha"}:
  raise ValueError("Independently supplied batch header required")
 if header["plan_hash"]!=p["plan_hash"] or not valid_sha(header["expected_history_sha"]) or not valid_sha(header["expected_identity_sha"]):
  raise ValueError("Invalid batch header")
 faults=0; halted=False; baseline_history=header["expected_history_sha"]; baseline_identity=header["expected_identity_sha"]
 if len(records)>len(p["schedule"]): raise ValueError("Too many records")
 for i,r in enumerate(records):
  if faults>=2 or halted: raise ValueError("Continued after stop condition")
  s=p["schedule"][i]
  if not isinstance(r,dict) or set(r)!=REQUIRED: raise ValueError("Record schema")
  if r["id"]!=s["id"] or r["plan_hash"]!=p["plan_hash"]: raise ValueError("Order/plan mismatch")
  validate_env_names(r["child_env_names"])
  for key in ("history_before_sha","history_after_sha","identity_sha"):
   if not valid_sha(r[key]): raise ValueError("Missing hash evidence")
  if r["history_before_sha"]!=baseline_history or r["history_after_sha"]!=baseline_history:
   raise ValueError("History contamination")
  if r["identity_sha"]!=baseline_identity: raise ValueError("Identity drift")
  for key in ("total_seconds","ttft_seconds","input_tokens","output_tokens"):
   v=r[key]
   if v is not None and (type(v) not in (int,float) or not math.isfinite(v) or v<0): raise ValueError("Invalid metric")
   if key.endswith("tokens") and v is not None and type(v) is not int: raise ValueError("Token count")
  if r["ttft_seconds"] is not None and (r["total_seconds"] is None or r["ttft_seconds"]>r["total_seconds"]): raise ValueError("TTFT")
  if r["finish_reason"] not in (None,"stop","length","tool_calls","content_filter","error"):
   raise ValueError("Unknown finish reason")
  if r["state"]=="complete":
   allowed=("stop","tool_calls") if s["task"]=="tool" else ("stop",)
   if r["finish_reason"] not in allowed: raise ValueError("Incomplete finish reason")
   if r["total_seconds"] is None or r["invalid_reason"] is not None: raise ValueError("Incomplete evidence")
   if r["correctness"]!=correctness(s["task"],r["output"]): raise ValueError("False correctness")
   faults=0
  elif r["state"] in ("failed","cancelled"):
   if r["correctness"]!="unverified" or r["invalid_reason"] not in p["invalid_conditions"]: raise ValueError("Failure evidence")
   if r["finish_reason"]=="length" and r["state"]!="failed": raise ValueError("Truncation must use failed state")
   if (r["finish_reason"]=="length")!=(r["invalid_reason"]=="truncated"):
    raise ValueError("Truncation must be recorded explicitly")
   reason=r["invalid_reason"]
   faults=faults+1 if reason in p["stop_policy"]["consecutive_infrastructure_fault_reasons"] else 0
   halted=r["state"]=="cancelled" or reason in p["stop_policy"]["immediate_stop_reasons"]
  else: raise ValueError("Nonterminal record; reconcile uncertain outcome before retry")
 return {"records":len(records),"raw_records":records,"batch_header":header,
         "batch_complete":len(records)==len(p["schedule"]),
         "next_id":p["schedule"][len(records)]["id"] if len(records)<70 and not (faults>=2 or halted) else None,
         "stopped":faults>=2 or halted,"consecutive_infrastructure_faults":faults,"adoption_approved":False,"coverage":coverage_summary(records,p)}

def execution_guard(maintenance,open_ports):
 if not maintenance: raise ValueError("Explicit maintenance flag required")
 if set(open_ports)&{8000,4001,8080}: raise ValueError("Production ports must be closed")
 raise ValueError("No execution adapter: real runs always disabled")
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--run",action="store_true"); p.add_argument("--maintenance",action="store_true")
 p.add_argument("--validate",type=Path)
 a=p.parse_args()
 if a.run: execution_guard(a.maintenance,())
 elif a.validate:
  with a.validate.open("rb") as f: raw=f.read(2097153)
  if len(raw)>2097152: raise ValueError("Oversized artifact")
  artifact=json.loads(raw)
  if not isinstance(artifact,dict) or set(artifact)!={"header","records"}:
   raise ValueError("Expected artifact with header and raw records")
  print(json.dumps(validate_records(artifact["records"],artifact["header"]),indent=2))
 else: print(json.dumps(plan(),indent=2,ensure_ascii=True))
if __name__=="__main__":
 try: main()
 except (ValueError,OSError) as exc: raise SystemExit(str(exc))

