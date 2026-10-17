# Scoring and metrics (§4.4, Table 2)

Reads only retained session exports. Owner: Person E.

| Construct | Measure |
|---|---|
| Correctness | Share of tasks within tolerance; normalized error on numeric tasks |
| Consistency | Pass or fail agreement across repeats; spread of tokens, tool calls, rounds |
| Robustness | Accuracy change across paraphrases |
| Predictability | Stated confidence against actual pass rate |
| Traceability | Claims linked to retained artifacts; decisions rebuildable from logs |
| Recovery | Detection, repair, persistence after an introduced fault |
| Review quality | Reviewer score against share of tasks correct |
| Harness | Variant against default on each model; variance share by harness and model |
| Autonomy | Intervention count and cause; accuracy and cost per condition |
| Efficiency | Time, tokens, and cost per successful task |

`schema/` holds the session log schema agreed with the driver. `src/` holds scorers.
