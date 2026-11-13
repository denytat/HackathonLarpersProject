# Swarmspotter

**Spots coordinated bot swarms and names the propaganda techniques they use, with measured precision and honest false-positive rates.**

Live demo: https://swarmspotter.tech
Built at Junction 2026 for the Hostinger challenge, also entered in the Google Gemini and NVIDIA Nemotron challenges.

---

## The problem

Propaganda and bot networks spread faster than fact-checkers can react. Most tools judge one post at a time, but manipulation shows up mainly in the *pattern*: many accounts posting near-identical text within seconds and amplifying each other. Detectors also rarely say how often they wrongly flag real people.

## What it does

Upload a batch of posts (CSV or JSON) and get:

1. **Suspected swarms**: groups of accounts acting in coordination, with plain-language evidence (for example "14 accounts posted near-identical text within 90 seconds").
2. **Named manipulation techniques** per post (loaded language, fear appeal, whataboutism, fabricated authority and so on), with the exact text span and an explanation, so a reader learns *why* something is propaganda.
3. **A verdict with confidence**: `flagged`, `uncertain` or `organic`.
4. **An evaluation page** with precision, recall and false-positive rate on a labeled test set, including hard cases such as organic viral posts.

## How it works

| Layer | What it does | Tech |
|---|---|---|
| 1. Swarm detection | Posting-time bursts, near-duplicate text, account-similarity graph, community detection. Deterministic and measurable. | Python, scikit-learn, networkx |
| 2. Technique classification | Labels manipulation techniques from a fixed list and explains each one. Its vision input can read screenshots of posts. | NVIDIA Nemotron 3.5 Super VL |
| 3. Cross-check and grounding | Reads a whole suspected swarm in one long-context call for a second opinion, and checks factual claims with search grounding. | Google Gemini |
| 4. Agreement rule | A post is flagged only when the swarm signals and the model verdicts agree. Otherwise it is shown as `uncertain`. This is the main defence against false positives. | Our code |

## Status

Work in progress, built over 48 hours.

- [x] Public deployment with HTTPS on a Hostinger VPS
- [x] FastAPI backend with a stub `/analyze` that follows the API contract
- [x] Streamlit UI shell
- [x] Nemotron and Gemini API calls verified
- [ ] Swarm detector (layer 1)
- [ ] Nemotron technique classifier (layer 2)
- [ ] Gemini cross-check (layer 3)
- [ ] Labeled evaluation set and evaluation page
- [ ] Agreement rule and `uncertain` verdict

## Architecture

```
Browser ──HTTPS──▶ Caddy ──▶ Streamlit UI (:8501) ──▶ FastAPI (:8000) ──▶ Nemotron endpoint
                      │                                        └────────▶ Gemini API
                      └──/api/*──▶ FastAPI (:8000)
```

Everything runs as three Docker containers (`api`, `ui`, `caddy`) on one Hostinger KVM 2 VPS. Caddy handles HTTPS certificates automatically.

## API contract

The full contract is in [`docs/contract.md`](docs/contract.md).

`POST /analyze`

```json
{
  "posts": [
    {"id": "p1", "account": "user_a", "text": "...",
     "timestamp": "2026-11-13T21:00:00Z", "reply_to": null, "image_url": null}
  ]
}
```

Returns swarms (accounts, score, evidence) and per-post techniques, verdict, confidence and which detectors flagged it.

`GET /health` returns `{"status": "ok"}`.

## Run it locally

Requirements: Python 3.11 or newer. Docker is optional for local work.

```powershell
git clone https://github.com/denytat/HackathonLarpersProject
cd HackathonLarpersProject
python -m venv .venv
.venv\Scripts\Activate.ps1            # macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
```

Create a `.env` file in the project root (never commit it):

```
VERDA_INFERENCE_KEY=your-nemotron-key
NEMOTRON_BASE_URL=https://containers.datacrunch.io/nemotron-3-5-super-vl-b300/v1
NEMOTRON_MODEL=nemotron-3.5-super-vl
GEMINI_API_KEY=your-gemini-key
GEMINI_MODEL=gemini-3.8-flash
API_URL=http://localhost:8000
```

Start the backend and the UI in two terminals:

```powershell
python -m uvicorn backend.main:app --reload
python -m streamlit run frontend/app.py
```

Check that the model keys work:

```powershell
python scripts\test_nvidia.py
python scripts\test_gemini.py
```

> Nemotron spends many tokens on hidden reasoning. Keep `max_tokens` at 4000 or higher, otherwise `message.content` can come back empty.

## Run it with Docker

```bash
docker compose up -d --build
docker compose ps
```

Set `API_URL=http://api:8000` in the server's `.env`. Put your domain in the first line of the `Caddyfile`.

## Deploy to the VPS

```bash
ssh root@<vps-ip>
cd /opt/swarmspotter
git pull origin main
docker compose up -d --build
docker compose logs --tail 30 caddy
```

Rebuild only when files in `backend/`, `frontend/`, `requirements.txt`, the Dockerfiles, `docker-compose.yml` or the `Caddyfile` change.

## Repository layout

```
backend/        FastAPI app and detection logic
frontend/       Streamlit UI
data/           Sample data and the labeled evaluation set
docs/           API contract
scripts/        Helper scripts (model connectivity tests)
docker-compose.yml
Caddyfile
requirements.txt
```

## Git workflow

- `main`: deployed. Merge into it only from `dev`.
- `dev`: integration branch. Both feature branches open pull requests into it.
- `roman`, `egor`: personal feature branches.
- Secrets live only in local `.env` files and are never committed.

## Evaluation

Results will be published here and on the dashboard's evaluation page: precision, recall and false-positive rate for each layer on its own and for the combined agreement rule, plus a list of real failure cases.

_Numbers to be added after the evaluation run. Synthetic test data is labeled as synthetic._

## Honest limitations

- Coordinated behaviour is not proof of bad intent. Fandoms, newsrooms and campaigns can look coordinated, which is why we test against organic look-alikes and report false positives.
- Technique labels come from a language model and can be wrong. They are shown with an explanation so a human can judge them.
- Part of the test data is synthetic and may not reflect real campaigns.

## Team

Hackathon Larpers: Roman and Egor.
