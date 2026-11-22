# Review Item Discrepancy (RID) ledger - ARKAGNI-main audit

Method: unpacked the uploaded zip, ran the API with the real CSVs, ran the test suite, built the frontend, read the code.
"Fixed" means changed in this repo and re-tested here. Not run here: Docker build, GitHub Actions, any live host.

| RID | Severity | Finding | Root cause | Status |
|---|---|---|---|---|
| 001 | CRITICAL | The API refuses to start: "results.sha256 sidecar disagrees with the results file" | `results.json` and `conformal.json` were edited after sealing; registry holds old hashes (results 6f6d09df..., conformal be22316a...) | Fixed: re-sealed (`scripts/reseal_artifacts.py`); `04_verify_release.py` passes |
| 002 | CRITICAL | A clean clone cannot start or build | The three CSVs and `data.db` are git-ignored; the Dockerfile copied files that are not in the repo (`MODIS_SP_cleaned.csv...`, `data/processed`) | Fixed: Dockerfile reads `data/cleaned` (Git LFS); LFS and ignore rules added; `data/processed` COPY removed (unused at start-up) |
| 003 | CRITICAL | No Cloudflare Worker exists, and the stack cannot run on one | Back end is FastAPI + pandas + scikit-learn, 2.0 GB RSS, 16 s start-up; Workers allow 128 MB / 10 ms | Resolved by design: host the API on Hugging Face Spaces; optional Pages proxy `_worker.js` (untested) |
| 004 | CRITICAL | Static-host deploy looks live but is broken | `vercel.json` rewrote every path (including `/results`, `/health`) to `index.html`; the client accepted the HTML as data | Fixed: root `vercel.json` removed (example with API proxy in `deploy/`); `api.ts` now throws on non-JSON 2xx |
| 005 | MAJOR | Tests and the legacy API fail on any machine but the author's; username leaked | `results.json` stores `C:/Users/<name>/OneDrive/...` as the model path | Fixed in `analysis.py` (relative path) and in the frozen results |
| 006 | MAJOR | Region-by-delay "validity map" shows coverage that was never measured per region | `analysis.py` copied the pooled per-bin coverage into every region cell | Mitigated: region coverage set to `null` with `coverage_scope: not_measured_per_region`. A real per-region nested evaluation is still to do |
| 007 | MAJOR | Duplicate or stale trees confuse builds | `FINAL_NASA/`, `web/`, Streamlit `app.py`, `processor.py`, 4 database scripts, duplicate Vite configs, tsbuildinfo, committed `dist/`, a second API (`src/pyroharmonize/api.py`) and private .docx files | Fixed: removed (legacy API and its test too) |
| 008 | MAJOR | Integrity checking is inconsistent | A results-hash mismatch only printed a warning, then the sidecar check raised anyway | Fixed: mismatch now raises |
| 009 | MAJOR | CORS is `*` while `config.yaml` lists allowed origins | `_origins = ["*"]` ignores the config | Fixed: origins come from `ARKAGNI_ALLOWED_ORIGINS` or config |
| 010 | MAJOR | Clean-clone tests: 3 failed, 46 errors | Missing processed tables and raw archive; Windows path (RID-005) | Fixed: 45 pass, 24 skip with explicit reasons (parity tests need `data/processed/pairs_aqua_snpp.parquet`) |
| 011 | MINOR | No CI | No workflow in the repo | Added `.github/workflows/ci.yml` (never executed) |
| 012 | MINOR | Charter mismatch | Charter locks model PR, RMSE 0.910, 2-3.5 h coverage 0.62 and reason `coverage_below_floor`; the repo serves H, RMSE 0.9916, coverage 0.66 and reason `delay_outside_calibrated_range` | Open: decide which is authoritative and align text or code |
| 013 | MINOR | `scan` is accepted as an angle in the charter (0-65 deg) | FIRMS `scan` is the along-scan pixel size in km | Open: the API range check already refuses implausible values; update the charter wording |

## Checked and clean
- No infinite `useEffect` loops: data loads once in `AppData`; the only timer is a short search debounce. Routing is a HashRouter, so there are no redirect loops.
- `tsc -b` and `vite build` pass (about 11 s). Dependency pins all exist on PyPI.
- Local boot with the three CSVs: `/health` ready in 16 s, `dataset_rows 1,382,752`, `pairs 6,313`, `data_hash 37423f49d223`.
- `/harmonize`: normal request 200; delay 2.3 h and 3.6 h return `applicable false`, FRP null; scan out of range refused; FRP <= 0, wrong config hash and raw pixel payloads return 422.
