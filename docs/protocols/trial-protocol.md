# Trial protocol

1. A trial is one attempt by one agent configuration on one task, in a fresh Harbor container.
2. Limits: 3,600 s agent time, 1 CPU, 4 GB memory, no GPU (adapter defaults). A trial that hits the time limit is marked capped.
3. Every agent receives the same instruction, ending with the report request in `report-template.md`.
4. Tokens and cost are recorded for every trial, not capped.
5. Harbor keeps every trial's outputs, logs and trajectory in its job folder. Nothing is scored inside the trial.
