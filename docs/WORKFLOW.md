# Safe development workflow

- `main` is production (GitHub Pages, legacy build, `CNAME` = puranenjenny.dev). Never push to it directly.
- Work on `feat/*` branches and open a PR; the `Checks` workflow must pass.
- Run locally before opening a PR: `python tools/check_site.py`
- Preview locally: `python -m http.server 8000` (case-sensitive checks run in CI on Linux).
- Do not change originals in `img/`; add new files alongside and wire them in only after approval.
- Baseline: tag `baseline-2026-11-02` at commit `440c6ba` (to be pushed after owner approval).

Pending owner approval: preview repository/deploy, branch ruleset on `main`, baseline tag push.
