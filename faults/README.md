# Fault injection set (§4.3)

Three fault types per paper, five papers, fifteen faults. Each runs on both harnesses with one model (Table 1, 30 sessions). Owner: Person A.

1. Faults are injected into the task environment, never the prompt.
2. Each fault is reproducible from a seed and behaves identically on both harnesses.
3. Each fault states how to tell whether the agent detected it, repaired it, or carried it into the final answer.

Injector code lives in `injectors/`.
