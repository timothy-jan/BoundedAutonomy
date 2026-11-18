# Interfaces

For the Oct 21 check-in.

| From | To | What | Where |
|---|---|---|---|
| Harbor (Person B) | Scoring (Person E) | Job folder per run: one trial folder each with `reward.txt`, agent logs, trajectory, test output | `runs/` (not committed) |
| Agents (Persons C, D) | Harbor | Agent entries in the job configs; all four harnesses are Harbor built-ins | `harbor/configs/`, `agents/` |
| Tasks (Person A) | Harbor | Reworded instructions replace `instruction.md` in a task copy | `tasks/tasks.csv` |
| Faults (Person A) | Harbor | Faulted task copies: Dockerfile changes or a wrapper script | `faults/` |
| Trials | Reviewer (Person B) | `report.md` from each trial | Trial folders |
| Scoring | Analysis | The trial table | `scoring/schema/trial-table.md` |
