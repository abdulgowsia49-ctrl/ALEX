"""Apply the RID-005 / RID-007 corrections to the frozen results and re-seal every hash.

Run once after editing artifacts; `python scripts/04_verify_release.py` then checks the chain.
NOTE: a full regeneration (scripts/03_run_analysis.py --force) on the source machine should replace this.
"""
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BA, AR = ROOT / "backend" / "artifacts", ROOT / "artifacts"

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

R = json.loads((BA / "results.json").read_text(encoding="utf-8"))
R["provenance"]["model_artifact"] = "artifacts/models/model_H.pkl"
for region in R["validity_map"].values():
    for label, cell in region["bins"].items():
        if cell.get("n", 0) and "coverage_scope" not in cell:
            cell["pooled_bin_coverage"] = cell.get("coverage")
            cell["coverage"] = None
            cell["coverage_scope"] = "not_measured_per_region"
text = json.dumps(R, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
for target in (BA / "results.json", AR / "results" / "results.json", AR / "reports" / "l2_l5_analysis.json"):
    target.write_text(text, encoding="utf-8", newline="\n")
digest = sha(BA / "results.json")
for sidecar in (BA / "results.sha256", AR / "results" / "results.sha256"):
    sidecar.write_text(digest + "\n", encoding="utf-8", newline="\n")
reg = json.loads((BA / "registry.json").read_text(encoding="utf-8"))
reg["results"]["sha256"] = digest
reg["conformal"]["sha256"] = sha(BA / "conformal.json")
reg["model"]["sha256"] = sha(BA / "model_H.pkl")
(BA / "registry.json").write_text(json.dumps(reg, indent=2) + "\n", encoding="utf-8", newline="\n")
print("results", digest[:12], "conformal", reg["conformal"]["sha256"][:12], "model", reg["model"]["sha256"][:12])
