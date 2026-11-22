# Deploying Arkagni (PyroHarmonize) so anyone can open it

## What this app is, and why it cannot run on Cloudflare Workers
The back end is Python (FastAPI + pandas + scikit-learn). It reads the three cleaned FIRMS CSV files at start-up
(1,382,752 rows), needs about 2.0 GB of RAM and about 16 s to become ready (measured locally).
Cloudflare Workers allow 128 MB and 10 ms of CPU, and cannot run pandas or scikit-learn, so the API cannot live there.
Run the API on a host with >= 3 GB RAM; optionally put Cloudflare Pages in front (section C).

## A. Hugging Face Spaces (free, no card, 16 GB RAM) - recommended
1. Create a Space: huggingface.co/new-space -> SDK **Docker** -> Blank -> Public.
2. On your machine:
   ```
   git lfs install
   git clone https://huggingface.co/spaces/YOUR-USER/arkagni && cd arkagni
   # copy the contents of this folder into it (this repo's root files, backend/, frontend/, data/, ...)
   mkdir -p data/cleaned
   cp /path/to/MODIS_SP_cleaned.csv /path/to/VIIRS_SNPP_SP_cleaned.csv /path/to/VIIRS_NOAA20_SP_cleaned.csv data/cleaned/
   git add . && git commit -m "deploy" && git push
   ```
   `.gitattributes` already sends `data/cleaned/*.csv` through Git LFS (files are 33, 113 and 142 MB).
3. The first build takes a few minutes. Open https://YOUR-USER-arkagni.hf.space and check `/health`:
   it must show `"model_loaded": true`, `"dataset_rows": 1382752`, `"pairs": 6313`, `"data_hash_begins": "37423f49d223"`.
4. A free Space sleeps after inactivity and takes about a minute to wake. Open it once before a demo.

## B. Any Docker host (Render paid, Fly, Railway, a VM)
```
docker build -t arkagni .
docker run -p 8000:8000 arkagni      # needs >= 3 GB RAM
```
Render's free tier (512 MB) will run out of memory; do not use it.

## C. Optional: Cloudflare Pages in front (untested)
`frontend/public/_worker.js` serves the built dashboard and proxies the API paths to your Space.
Pages -> Create project -> connect the GitHub repo -> Build command `cd frontend && npm ci && npm run build`,
Output directory `frontend/dist` -> Settings -> Variables: `API_ORIGIN = https://YOUR-USER-arkagni.hf.space`.
This path was written but not executed here.

## D. Vercel
`deploy/vercel.example.json` shows the rewrites that proxy the API to your Space. The old root `vercel.json`
sent every path to index.html, so API calls returned a web page (that is the "deployed but broken" symptom).

## E. Before every release
```
python scripts/04_verify_release.py     # hash chain; must report pass or pass_with_skips
python -m pytest -q                     # 45 pass, 24 skip on a clean clone
```
If you change `results.json` or `conformal.json`, re-seal: `python scripts/reseal_artifacts.py`.
