# Frozen Lemonade Stand version

| Field | Value |
|---|---|
| Repository | 1seansean1/lemonade-stand |
| Version | 1.0.0-rc.57 (`VERSION` file) |
| Branch | `agent/codex/SEAN-20261015-001-owner-daily-cost-rc57` |
| Commit | `92ae62f586e2f325cc30460058674a6ecee236fa` |
| Release date | 2026-10-15 |
| Frozen on | 2026-10-20 (pinned to the last release before the Oct 18 milestone) |
| Frozen by | Timothy |

rc.57 was the newest release at the Oct 18 milestone. rc.65 followed on Oct 19. The sponsor's repo has no git tag for rc.57, so the study pins the commit hash above. Every session checks out exactly this commit:

```
git clone https://github.com/1seansean1/lemonade-stand
cd lemonade-stand
git checkout 92ae62f586e2f325cc30460058674a6ecee236fa
cat VERSION   # 1.0.0-rc.57
```

## Notes for the driver

- rc.57 replaced per-chat and per-bot dollar limits with one daily USD cost limit shared across all model work. It keeps Stop spending and the technical time, turn and call limits. The driver must enforce the 5M token and 6 hour caps per session itself.
- Set the daily USD limit high enough that four parallel sessions cannot hit it mid-session, or a session would stop for a reason outside the study.

If a variant needs code changes, pin a new commit before the pilot and log it in `docs/decisions/decision-log.md`.
