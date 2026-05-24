---
name: Fix heredoc/indentation in manual-patch workflow
---

This PR replaces the python -c heredoc in .github/workflows/manual-patch.yml with a safe heredoc invocation and fixes indentation issues that caused an IndentationError during Actions runs.

- Replaces python -c "..." blocks with python - "<args>" <<'PY' ... PY
- Passes the filename and version as argv to the python script to avoid accidental shell interpolation
- Ensures variables are quoted and heredocs are single-quoted to prevent expansion

This should fix the following error observed in Actions logs:

  File "<string>", line 2
    import json, sys, os
IndentationError: unexpected indent

Signed-off-by: dolfies <me@dolfi.es>
