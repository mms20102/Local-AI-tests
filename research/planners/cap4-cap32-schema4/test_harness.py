import ast, copy, unittest
from pathlib import Path
import harness as h
class Tests(unittest.TestCase):
 def header(self):
  return {"plan_hash":h.plan()["plan_hash"],"expected_history_sha":"a"*64,"expected_identity_sha":"b"*64}
 def validate(self,records):
  return h.validate_records(records,self.header())
 def record(self,i=0):
  s=h.plan()["schedule"][i]
  return dict(id=s["id"],plan_hash=h.plan()["plan_hash"],state="complete",output="READY",
   correctness="unscored",total_seconds=1.,ttft_seconds=.2,input_tokens=8,output_tokens=1,
   history_before_sha="a"*64,history_after_sha="a"*64,identity_sha="b"*64,invalid_reason=None,finish_reason="stop",child_env_names=["COLI_VULKAN","COLI_CUDA","COLI_VK_TIER_GB","OMP_NUM_THREADS","USAGE_SAVE"])
 def full_records(self):
  outputs={"warmup":"READY","format":'{"capital":"Paris"}',"function":"def f(): pass",
   "bugfix":"def maximum(xs): pass","edit":"new_name=1\nprint(new_name)\n# new_name",
   "tool":{"name":"add","arguments":{"a":2,"b":3}},"arabic":"placeholder"}
  rows=[]
  for i,s in enumerate(h.plan()["schedule"]):
   r=self.record(i);r["output"]=outputs[s["task"]];r["correctness"]=h.correctness(s["task"],r["output"])
   if s["task"]=="tool":r["finish_reason"]="tool_calls"
   rows.append(r)
  return rows
 def failure(self,i,reason):
  r=self.record(i);r.update(state="failed",correctness="unverified",invalid_reason=reason,
                            finish_reason="length" if reason=="truncated" else None)
  return r
 def test_schema3_policy_frozen(self):
  p=h.plan();self.assertEqual(p["schema"],4)
  self.assertEqual(p["stop_policy"]["consecutive_infrastructure_fault_reasons"],["transport_error","deadline"])
  self.assertEqual(p["eligible_pair_ceiling"],10)
  self.assertTrue(p["eligible_pair_ceiling_is_planned_not_passed"])
 def test_identity_header_required(self):
  header=self.header();del header["expected_identity_sha"]
  with self.assertRaises(ValueError):h.validate_records([],header)
  header=self.header();header["expected_identity_sha"]="bad"
  with self.assertRaises(ValueError):h.validate_records([],header)
 def test_first_identity_matches_header(self):
  r=self.record();r["identity_sha"]="c"*64
  with self.assertRaises(ValueError):self.validate([r])
 def test_all_immediate_reasons_halt(self):
  for reason in h.plan()["stop_policy"]["immediate_stop_reasons"]:
   rows=[self.failure(0,reason)];before=copy.deepcopy(rows)
   result=self.validate(rows);self.assertTrue(result["stopped"]);self.assertIsNone(result["next_id"])
   self.assertEqual(result["raw_records"],before)
   with self.assertRaises(ValueError):self.validate(rows+[self.record(1)])
 def test_repeated_truncations_do_not_stop(self):
  rows=[self.failure(i,"truncated") for i in range(4)]
  result=self.validate(rows)
  self.assertFalse(result["stopped"]);self.assertEqual(result["consecutive_infrastructure_faults"],0)
  self.assertEqual(result["raw_records"],rows)
 def test_truncation_resets_infrastructure_sequence(self):
  rows=[self.failure(0,"deadline"),self.failure(1,"truncated"),self.failure(2,"transport_error")]
  result=self.validate(rows)
  self.assertFalse(result["stopped"]);self.assertEqual(result["consecutive_infrastructure_faults"],1)
  result=self.validate(rows+[self.failure(3,"deadline")]);self.assertTrue(result["stopped"])
 def test_quality_failure_resets_not_counts_infrastructure(self):
  rows=self.full_records()[:3]
  rows[0]=self.failure(0,"deadline");rows[1].update(output="wrong",correctness="fail")
  rows[2]=self.failure(2,"transport_error")
  result=self.validate(rows);self.assertFalse(result["stopped"])
  self.assertEqual(result["consecutive_infrastructure_faults"],1)
 def test_both_infrastructure_reasons_count(self):
  for reasons in (("deadline","transport_error"),("transport_error","deadline")):
   result=self.validate([self.failure(i,r) for i,r in enumerate(reasons)])
   self.assertTrue(result["stopped"]);self.assertEqual(result["consecutive_infrastructure_faults"],2)
 def test_full_token_eligibility_ceiling(self):
  c=self.validate(self.full_records())["coverage"]
  self.assertEqual(c["pair_denominator"],30);self.assertEqual(c["eligible_pair_ceiling"],10)
  self.assertEqual(c["exact_fixture_qualified_pairs"],10);self.assertEqual(c["speed_comparison_eligible_pairs"],10)
  self.assertEqual(c["count_relationships"]["n_truncated_subset_of"],"n_failed")
  self.assertEqual(c["count_relationships"]["cancelled_included_in"],"n_failed")
 def test_unknown_tokens_preserved_and_excluded(self):
  for key in ("input_tokens","output_tokens"):
   rows=self.full_records();rows[1][key]=None
   result=self.validate(rows);c=result["coverage"]
   self.assertIsNone(result["raw_records"][1][key])
   self.assertEqual(c["exact_fixture_qualified_pairs"],10)
   self.assertEqual(c["speed_comparison_eligible_pairs"],9)
   self.assertEqual(c["measured_by_task_arm"]["format"]["A"]["n_complete_with_token_counts"],4)
   self.assertIn("unknown_token_counts",c["pairs"][0]["speed_comparison_exclusions"])
 def test_unequal_tokens_excluded_not_quality_failure(self):
  for key in ("input_tokens","output_tokens"):
   rows=self.full_records();rows[1][key]+=1
   c=self.validate(rows)["coverage"]
   self.assertEqual(c["exact_fixture_qualified_pairs"],10)
   self.assertEqual(c["speed_comparison_eligible_pairs"],9)
   self.assertEqual(c["measured_by_task_arm"]["format"]["A"]["n_complete_with_token_counts"],5)
   self.assertIn("unequal_input_or_output_token_counts",c["pairs"][0]["speed_comparison_exclusions"])
 def test_unverified_known_counts_do_not_qualify(self):
  c=self.validate(self.full_records())["coverage"]
  for pair in c["pairs"]:
   if pair["task"] in ("function","bugfix","arabic","tool"):
    self.assertFalse(pair["speed_comparison_eligible"])
    self.assertFalse(pair["exact_fixture_qualified"])

 def test_hash_mismatch_not_valid_failure_reason(self):
  for reason,key in (("identity_mismatch","identity_sha"),("history_mismatch","history_before_sha")):
   self.assertNotIn(reason,h.plan()["invalid_conditions"])
   self.assertNotIn(reason,h.plan()["stop_policy"]["immediate_stop_reasons"])
   r=self.failure(0,reason);before=copy.deepcopy(r)
   with self.assertRaises(ValueError):self.validate([r])
   self.assertEqual(r,before)
   r=self.record();r[key]="c"*64;before=copy.deepcopy(r)
   with self.assertRaises(ValueError):self.validate([r])
   self.assertEqual(r,before)
 def test_cumulative_alternating_faults_stop_at_four(self):
  rows=self.full_records()[:7]
  for i in (0,2,4,6):rows[i]=self.failure(i,"deadline")
  original=copy.deepcopy(rows);result=self.validate(rows)
  self.assertTrue(result["stopped"]);self.assertEqual(result["cumulative_infrastructure_faults"],4)
  self.assertEqual(result["consecutive_infrastructure_faults"],1)
  self.assertEqual(result["raw_records"],original);self.assertIsNone(result["next_id"])
  with self.assertRaises(ValueError):self.validate(rows+[self.record(7)])
 def test_truncation_resets_streak_not_total(self):
  rows=[self.failure(0,"deadline"),self.failure(1,"truncated"),self.failure(2,"transport_error")]
  result=self.validate(rows)
  self.assertEqual(result["cumulative_infrastructure_faults"],2)
  self.assertEqual(result["consecutive_infrastructure_faults"],1)
  self.assertFalse(result["stopped"])
 def test_unverified_observation_table(self):
  rows=self.full_records();rows[2]["output_tokens"]=None
  result=self.validate(rows);table=result["coverage"]["response_complete_correctness_unverified"]
  self.assertEqual(set(table),{"function","bugfix","arabic"})
  cell=table["function"]["A"]
  self.assertEqual((cell["n_planned"],cell["n_observed"],cell["n_complete"]),(5,5,5))
  self.assertEqual(cell["label"],"response_complete_correctness_unverified")
  self.assertFalse(cell["quality_or_speedup_claim_supported"])
  observation=cell["complete_response_observations"][0]
  self.assertEqual(observation["id"],rows[2]["id"]);self.assertIsNone(observation["output_tokens"])
  self.assertEqual(observation["total_seconds"],rows[2]["total_seconds"])
 def test_unverified_table_excludes_failed_observations(self):
  rows=self.full_records()[:3];rows[2]=self.failure(2,"truncated")
  cell=self.validate(rows)["coverage"]["response_complete_correctness_unverified"]["function"]["A"]
  self.assertEqual(cell["n_observed"],1);self.assertEqual(cell["n_complete"],0)
  self.assertEqual(cell["complete_response_observations"],[])
 def test_empty_pairs_not_unknown_usage(self):
  counts=self.validate([])["coverage"]["speed_comparison_exclusion_counts"]
  self.assertEqual(counts["unobserved_arm"],30)
  self.assertNotIn("unknown_token_counts",counts)
  self.assertNotIn("unequal_input_or_output_token_counts",counts)
 def test_partial_pair_not_unknown_usage(self):
  rows=self.full_records()[:2];rows[1]["input_tokens"]=None
  c=self.validate(rows)["coverage"]
  self.assertNotIn("unknown_token_counts",c["speed_comparison_exclusion_counts"])
 def test_exclusion_counts_overlap(self):
  rows=self.full_records();rows[1]["input_tokens"]=None
  rows[2]["output_tokens"]=None
  rows[4]["output_tokens"]+=1
  c=self.validate(rows)["coverage"];counts=c["speed_comparison_exclusion_counts"]
  self.assertTrue(c["exclusion_counts_overlap"])
  self.assertEqual(counts["unknown_token_counts"],2)
  self.assertEqual(counts["unequal_input_or_output_token_counts"],1)
  self.assertEqual(counts["unverified"],15)
 def test_mock_plan_schedule_and_limits_respected(self):
  from unittest.mock import patch
  p=h.plan();p["schedule"]=p["schedule"][:14]
  p["stop_policy"]["consecutive_infrastructure_fault_limit"]=3
  p["stop_policy"]["cumulative_infrastructure_fault_limit"]=3
  p.pop("plan_hash");p["plan_hash"]=h.digest(p)
  with patch.object(h,"plan",return_value=p):
   rows=[self.failure(i,"deadline") for i in range(3)]
   self.assertFalse(self.validate(rows[:2])["stopped"])
   self.assertTrue(self.validate(rows)["stopped"])
   complete=self.full_records();result=self.validate(complete);c=result["coverage"]
   self.assertTrue(result["batch_complete"]);self.assertIsNone(result["next_id"])
   self.assertEqual(c["measured_denominator"],12);self.assertEqual(c["warmup_denominator"],2)
   self.assertEqual(c["pair_denominator"],6);self.assertEqual(c["eligible_pair_ceiling"],2)
 def test_mock_cumulative_limit_respected(self):
  from unittest.mock import patch
  p=h.plan();p["stop_policy"]["cumulative_infrastructure_fault_limit"]=2
  p.pop("plan_hash");p["plan_hash"]=h.digest(p)
  with patch.object(h,"plan",return_value=p):
   rows=[self.failure(0,"deadline"),self.failure(1,"truncated"),self.failure(2,"deadline")]
   self.assertTrue(self.validate(rows)["stopped"])
   with self.assertRaises(ValueError):self.validate(rows+[self.record(3)])

 def test_header_required(self):
  for header in (None,{},{"expected_history_sha":"a"*64},{"plan_hash":"wrong","expected_history_sha":"a"*64}):
   with self.assertRaises(ValueError):h.validate_records([],header)
 def test_first_history_must_match_independent_header(self):
  r=self.record();r["history_before_sha"]=r["history_after_sha"]="c"*64
  with self.assertRaises(ValueError):self.validate([r])
 def test_environment_evidence_names_only(self):
  for names in ([],{"COLI_CUDA":"0"},["COLI_CUDA=0"],["coli_lookup"],["COLI_FOO SECRET"],
                ["PATH"],["OMP_A","OMP_A"]):
   r=self.record();r["child_env_names"]=names
   with self.assertRaises(ValueError):self.validate([r])
 def test_lookup_resolved_environment_rejected(self):
  r=self.record();r["child_env_names"].append("COLI_LOOKUP")
  with self.assertRaises(ValueError):self.validate([r])
 def test_extra_relevant_names_allowed(self):
  r=self.record();r["child_env_names"]+=["COLI_NO_OMP_TUNE","OMP_WAIT_POLICY"]
  self.assertEqual(self.validate([r])["records"],1)
 def test_complete_finish_reasons(self):
  for finish in (None,"length","tool_calls","content_filter","error"):
   r=self.record();r["finish_reason"]=finish
   with self.assertRaises(ValueError):self.validate([r])
 def test_tool_calls_allowed_only_tool(self):
  rows=self.full_records()
  self.assertTrue(self.validate(rows)["batch_complete"])
  rows[1]["finish_reason"]="tool_calls"
  with self.assertRaises(ValueError):self.validate(rows)
 def test_truncation_explicit_failure(self):
  r=self.record();r.update(state="failed",correctness="unverified",finish_reason="length",invalid_reason="truncated")
  result=self.validate([r])
  self.assertEqual(result["coverage"]["warmups_by_arm"]["A"]["n_truncated"],1)
  self.assertEqual(result["raw_records"],[r])
  for finish,reason in (("length","deadline"),("stop","truncated")):
   bad=copy.deepcopy(r);bad.update(finish_reason=finish,invalid_reason=reason)
   with self.assertRaises(ValueError):self.validate([bad])
 def test_full_denominators_and_honest_coverage(self):
  result=self.validate(self.full_records());c=result["coverage"]
  self.assertTrue(result["batch_complete"]);self.assertFalse(result["adoption_approved"])
  self.assertEqual(c["measured_denominator"],60);self.assertEqual(c["warmup_denominator"],10)
  self.assertEqual(c["pair_denominator"],30);self.assertEqual(c["fully_observed_pairs"],30)
  self.assertEqual(c["both_transport_complete_pairs"],30);self.assertEqual(c["eligible_complete_pairs"],10)
  self.assertFalse(c["overall_no_regression_claim_supported"])
  self.assertEqual(c["measured_by_task_arm"]["arabic"]["A"]["n_complete"],5)
  self.assertEqual(c["warmups_by_arm"]["B"]["n_complete"],5)
 def test_truncation_is_failed_not_cancelled(self):
  r=self.record();r.update(state="cancelled",correctness="unverified",finish_reason="length",invalid_reason="truncated")
  with self.assertRaises(ValueError):self.validate([r])

 def test_failure_and_truncation_not_dropped(self):
  rows=self.full_records()
  rows[1].update(state="failed",correctness="unverified",finish_reason="length",invalid_reason="truncated")
  original=copy.deepcopy(rows);result=self.validate(rows);c=result["coverage"]
  self.assertEqual(rows,original);self.assertEqual(result["raw_records"],original)
  self.assertTrue(result["batch_complete"]);self.assertEqual(c["fully_observed_pairs"],30)
  self.assertEqual(c["both_transport_complete_pairs"],29);self.assertEqual(c["eligible_complete_pairs"],9)
  count=c["measured_by_task_arm"]["format"]["A"]
  self.assertEqual(count,{"n_planned":5,"n_observed":5,"n_complete":4,"n_complete_with_token_counts":4,"n_failed":1,"n_truncated":1,"n_unobserved":0})
  self.assertIn("truncated",c["pairs"][0]["exclusions"])
 def test_partial_pairs_not_complete(self):
  result=self.validate(self.full_records()[:9]);c=result["coverage"]
  self.assertFalse(result["batch_complete"]);self.assertEqual(c["fully_observed_pairs"],1)
  self.assertEqual(c["pair_denominator"],30);self.assertEqual(c["eligible_complete_pairs"],1)
 def test_incorrect_fixture_pair_excluded(self):
  rows=self.full_records();rows[1].update(output="wrong",correctness="fail")
  result=self.validate(rows)
  self.assertEqual(result["coverage"]["both_transport_complete_pairs"],30)
  self.assertEqual(result["coverage"]["eligible_complete_pairs"],9)
  self.assertIn("incorrect_fixture",result["coverage"]["pairs"][0]["exclusions"])

 def test_lookup_explicitly_unset(self):
  self.assertIn("COLI_LOOKUP",h.plan()["fixed"])
  self.assertIsNone(h.plan()["fixed"]["COLI_LOOKUP"])
 def test_coverage_does_not_claim_no_regression(self):
  c=h.plan()["correctness_coverage"]
  self.assertEqual(c["planned_measured_counts"],{"exact_fixture":20,"schema_only":10,"unverified":30})
  self.assertFalse(c["overall_no_regression_claim_supported"])
  self.assertFalse(c["full_semantic_execution_validated"])
  self.assertTrue(c["counts_are_planned_not_observed"])
  for task in ("function","bugfix","arabic"):
   self.assertEqual(c["task_labels"][task],"unverified")
   self.assertEqual(h.correctness(task,"anything"),"unverified")
  self.assertEqual(c["task_labels"]["tool"],"schema_only")
 def test_history_before_and_after_strict(self):
  for key in ("history_before_sha","history_after_sha"):
   rs=[self.record(),self.record(1)]
   rs[1].update(output='{"capital":"Paris"}',correctness="pass")
   rs[1][key]="c"*64
   with self.assertRaises(ValueError):self.validate(rs)
 def test_schedule(self):
  s=h.plan()["schedule"]; self.assertEqual(len(s),70)
  self.assertEqual(sum(r["scored"] for r in s),60)
  self.assertEqual(len({r["id"] for r in s}),70)
 def test_order(self):
  self.assertEqual([r["arm"] for r in h.plan()["schedule"] if not r["scored"]],list("ABBAABBAAB"))
 def test_pairs(self):
  s=h.plan()["schedule"]
  for t in h.TASKS:
   for p in range(1,6):
    self.assertEqual({r["arm"] for r in s if r["task"]==t["id"] and r["pair"]==p},{"A","B"})
 def test_plan_hash(self):
  p=h.plan(); saved=p.pop("plan_hash"); self.assertEqual(saved,h.digest(p))
 def test_hidden(self):
  self.assertNotIn("fixtures",h.plan())
  self.assertNotIn("synthetic_unavailable",str(h.TASKS))
 def test_empty_checkpoint(self): self.assertEqual(self.validate([])["next_id"],"p1-A-warmup")
 def test_prefix(self): self.assertEqual(self.validate([self.record()])["next_id"],"p1-A-format")
 def test_duplicate(self):
  with self.assertRaises(ValueError): self.validate([self.record(),self.record()])
 def test_foreign_plan(self):
  r=self.record(); r["plan_hash"]="x"
  with self.assertRaises(ValueError): self.validate([r])
 def test_uncertain(self):
  r=self.record();r["state"]="sent"
  with self.assertRaises(ValueError): self.validate([r])
 def test_history(self):
  r=self.record();r["history_after_sha"]="c"*64
  with self.assertRaises(ValueError): self.validate([r])
 def test_no_metrics_invention(self):
  r=self.record();r["input_tokens"]=None;r["ttft_seconds"]=None
  self.assertFalse(self.validate([r])["adoption_approved"])
 def test_bad_metrics(self):
  for v in (-1,float("nan"),float("inf"),True):
   r=self.record();r["total_seconds"]=v
   with self.assertRaises(ValueError): self.validate([r])
 def test_deadline_failure_retained(self):
  r=self.record();r.update(state="failed",correctness="unverified",invalid_reason="deadline")
  self.assertEqual(self.validate([r])["records"],1)
 def test_immediate_stop(self):
  for state,reason in (("failed","cancelled"),("failed","memory_pressure"),("cancelled","cancelled")):
   r=self.record();r.update(state=state,correctness="unverified",invalid_reason=reason)
   self.assertTrue(self.validate([r])["stopped"])
   with self.assertRaises(ValueError):self.validate([r,self.record(1)])
 def test_arabic_preserved(self):
  self.assertTrue(any(0x600<=ord(c)<=0x6ff for c in h.TASKS[-1]["prompt"]))
  self.assertNotIn("?",h.TASKS[-1]["prompt"])
 def test_stop(self):
  rs=[self.record(i) for i in range(3)]
  for r in rs:r.update(state="failed",correctness="unverified",invalid_reason="deadline")
  self.assertTrue(self.validate(rs[:2])["stopped"])
  with self.assertRaises(ValueError): self.validate(rs)
 def test_fake_success(self):
  rs=[self.record(),self.record(1)];rs[1]["correctness"]="pass"
  with self.assertRaises(ValueError):self.validate(rs)
 def test_exact_format_rejects_duplicate_keys(self):
  for output in ('{"capital":"Rome","capital":"Paris"}','{"capital":"Paris","capital":"Paris"}',' {"capital":"Paris"}'):
   self.assertEqual(h.correctness("format",output),"fail")
 def test_stopped_checkpoint_has_no_next_id(self):
  for reason in ("cancelled","memory_pressure"):
   r=self.record();r.update(state="failed",correctness="unverified",invalid_reason=reason)
   self.assertIsNone(self.validate([r])["next_id"])
  rs=[self.record(i) for i in range(2)]
  for r in rs:r.update(state="failed",correctness="unverified",invalid_reason="deadline")
  self.assertIsNone(self.validate(rs)["next_id"])
 def test_format(self):
  self.assertEqual(h.correctness("format",'{"capital":"Paris"}'),"pass")
  self.assertEqual(h.correctness("format",'{"capital":"Rome"}'),"fail")
 def test_edit(self):
  self.assertEqual(h.correctness("edit","new_name=1\nprint(new_name)\n# new_name"),"pass")
 def test_code_not_executed(self):
  for t in ("function","bugfix","arabic"):
   self.assertEqual(h.correctness(t,"raise RuntimeError('must not execute')"),"unverified")
 def test_tool(self):
  self.assertEqual(h.tool_fixture({"name":"add","arguments":{"a":2,"b":3}}),{"simulated":True,"result":5})
  self.assertEqual(h.correctness("tool",{"name":"add","arguments":{"a":2,"b":3}}),"schema_only")
 def test_bad_tools(self):
  for c in ({"name":"shell","arguments":{}},{"name":"add","arguments":{"a":True,"b":3}},
            {"name":"add","arguments":{"a":2,"b":3,"cmd":"x"}},{"name":"add","arguments":{"a":1,"b":3}}):
   with self.assertRaises(ValueError):h.tool_fixture(c)
 def test_guards(self):
  for approved,ports in ((False,()),(True,(8000,)),(True,(4001,)),(True,(8080,)),(True,())):
   with self.assertRaises(ValueError): h.execution_guard(approved,ports)
 def test_no_execution_or_network_imports(self):
  tree=ast.parse(Path(h.__file__).read_text(encoding="utf-8-sig"))
  for n in ast.walk(tree):
   if isinstance(n,ast.Call) and isinstance(n.func,ast.Name):
    self.assertNotIn(n.func.id,{"eval","exec","compile","__import__"})
   if isinstance(n,ast.Import):
    self.assertTrue(all(a.name in {"argparse","hashlib","json","math"} for a in n.names))
   if isinstance(n,ast.ImportFrom):self.assertEqual(n.module,"pathlib")
if __name__=="__main__":unittest.main()

