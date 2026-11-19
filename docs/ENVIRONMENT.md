# Cloud environment notes

Checked 2026-11-19.

## The recurring failure

| Question | Finding |
|---|---|
| Where it fails | Environment start-up, in the **setup script** of the cloud environment named "BB". The command is `pip install --upgrade pip`, exit code 1 |
| Why | The container's pip was installed by the operating system (Debian), so pip cannot uninstall it to upgrade itself: "Cannot uninstall pip 24.0, RECORD file not found" |
| Not the cause | Repository clone, Python, memory (16 GB, 15.5 free), disk (59 GB free), dataset size (repository is 30 MB to clone) |
| Introduced by a recent change? | No. The script lives in the environment's settings, not in this repository, and it failed on the very first session start, before any commit existed |
| Effect on an interactive session | Non-fatal: the session starts without whatever the script would have installed, and shows the failure each time |
| Effect on a scheduled stand-alone session | **Fatal**: the session ends in about 4 seconds with "Setup script failed" |

## The fix (one change, made in the environment settings)

In the Claude app, open the cloud environment menu in the session's title bar, choose the "BB"
environment, Edit, Setup script. Delete the line `pip install --upgrade pip`. If the script should
also install this project's libraries, the whole script can be:

```bash
pip install -q pandas numpy pyarrow scikit-learn statsmodels tabulate openpyxl || true
```

That line was run in the container and exits cleanly. The `|| true` means a failed install can never
block a session from starting. New sessions pick up the change; running ones are unaffected.

## What does not need the fix

- The hourly odds job runs on GitHub, not in this environment.
- Everything needed to reproduce the research is committed. Raw downloads (about 550 MB) are not
  committed and are not needed for the forward test; `src/forward_log.py` fetches the few current-season
  files it uses.
