# Swarmspotter

**Detect coordinated activity across groups of social-media accounts,
examine manipulation techniques, and make the evidence understandable.**

[Website](https://swarmspotter.tech) · Built at **Junction 2026** for
the Hostinger challenge, with entries in the Google Gemini, NVIDIA
Nemotron and Verda challenges.

---

## Why it matters

Manipulation campaigns are difficult to understand by looking at one
post in isolation. Coordination can become visible across many accounts:
repeated or near-identical messages, bursts of activity, and similar
account behaviour.

Swarmspotter analyses batches of posts to surface those patterns. It is
designed to show the evidence behind a result and to make false
positives visible---not to treat coordination as automatic proof of
malicious intent.

## What it does

- **Analyses batches of posts** supplied as CSV, JSON or by provided URL.
- **Looks for coordinated behaviour** across accounts using timing,
  text similarity and account-level patterns.
- **Explains suspicious patterns** with evidence that a reviewer can
  inspect.
- **Uses AI-assisted technique analysis** to identify possible
  manipulation techniques in post text and explain the reasoning.
- **Supports evaluation** on labelled datasets, including organic
  look-alike cases.

The exact output depends on the enabled analysis components and the data
supplied. Model-generated technique labels are suggestions for human
review, not verified facts.

## Try it with the example datasets

You do not need to collect your own social-media data to explore the
project. The [`examples/`](examples/) folder contains three small,
fictional CSV datasets:

---

Example What it demonstrates

---

[`coordinated_campaign.csv`](examples/coordinated_campaign.csv) A group of accounts posting closely
related alarming claims in short
bursts, mixed with unrelated
discussion.

[`organic_discussion.csv`](examples/organic_discussion.csv) An organic conversation about the
same event, with posts close
together in time but distinct
wording. Useful for inspecting
possible false positives.

[`mixed_activity.csv`](examples/mixed_activity.csv) A coordinated cluster alongside a
separate organic community
conversation.

---

**To try them:**

1.  Open the [Swarmspotter demo](https://swarmspotter.tech).
2.  Go to the batch/post analysis workflow.
3.  Upload one of the CSV files from `examples/`.
4.  Inspect the detected patterns, supporting evidence and post-level
    analysis.
5.  Compare the result with
    [`benchmark_labels.json`](examples/benchmark_labels.json), which
    contains the ground-truth account labels for each example.

The labels file is for evaluation; upload it only if the evaluation
workflow explicitly asks for ground-truth labels. More details are in
[`examples/README.md`](examples/README.md).

> These are fictional demonstration fixtures. They are not real-world
> campaign data and do not establish real-world accuracy.

## How We Used the Challenge Technologies

Swarmwatch combines Google Gemini, NVIDIA Nemotron and Verda to approach coordinated manipulation from different perspectives. Each technology has a specific role in the system.

### Google Gemini — Swarm-Level Intelligence

We use Google Gemini to analyse the wider context of potentially coordinated activity.

Rather than examining a single post in isolation, Gemini helps interpret groups of posts and identify:

- Shared narratives and recurring claims.
- Similar messaging and communication strategies.
- Common framing across different accounts.
- Potential manipulation patterns and campaign context.
- Explanations of why a group of posts may deserve further investigation.

Gemini adds contextual reasoning to the measurable coordination signals detected by our backend. Its findings are AI-generated assessments, not definitive proof of malicious activity.

### NVIDIA Nemotron — Manipulation Technique Detection

We use NVIDIA Nemotron for post-level analysis.

Nemotron examines individual posts and identifies possible manipulation techniques, including:

- Repetitive messaging.
- Hashtag spamming.
- Narrative amplification.
- Emotional manipulation.
- Impersonation.
- Misleading claims.

This allows Swarmwatch to go beyond detecting that accounts are behaving similarly. It can also help explain what communication techniques appear in their content.

Nemotron's classification is one piece of evidence. A post receiving a manipulation label does not automatically mean that its author is part of a coordinated campaign.

### Verda — GPU Infrastructure and Model Hosting

Verda provides the infrastructure used to deploy and serve NVIDIA Nemotron.

We deployed the Nemotron model in a dedicated GPU-backed container on Verda and connected it to our backend through an OpenAI-compatible inference API.

This approach allowed us to use a large AI model without running it directly on our application server.

The backend sends requests to the Verda-hosted inference endpoint, receives Nemotron's classification results and integrates them into the analysis workflow.

Verda therefore provides the computing infrastructure, while NVIDIA Nemotron performs the actual AI analysis.

### How the Technologies Work Together

The technologies complement our own coordination-detection system:

1. **Swarm detection:** Our backend identifies relationships between accounts using posting-time patterns, text similarity and account behaviour.
2. **Nemotron:** Examines individual posts and identifies possible manipulation techniques.
3. **Gemini:** Analyses the wider narrative and context across groups of posts.
4. **Verda:** Hosts the GPU-backed Nemotron inference service used by the backend.

By combining measurable behavioural signals with AI-assisted content analysis, Swarmwatch aims to provide more transparent and useful explanations of suspicious coordinated activity.

### Our Approach to Responsible AI

We do not treat AI-generated conclusions as facts. Similar posting patterns do not necessarily indicate malicious coordination, and AI models can make mistakes.

Swarmwatch is designed to present evidence and assessments that help users investigate potential manipulation, rather than automatically label accounts or individuals as malicious.

## How it works

---

Layer Role Technology

---

Batch analysis API Validates and processes Python, FastAPI,
structured post data. Pydantic

Coordination analysis Looks for timing bursts, Python, scikit-learn,
similar text and NetworkX
account-level patterns  
 across posts.

Technique analysis Produces AI-assisted NVIDIA Nemotron
explanations and  
 possible  
 manipulation-technique  
 labels.

Swarm-level Adds broader Google Gemini
interpretation narrative/context  
 analysis where enabled.

User interface Lets users submit data Streamlit
and inspect results.

Deployment Serves the application Docker Compose, Caddy,
over HTTPS. Hostinger VPS

---

AI outputs can be incomplete or wrong. Swarm-level coordination signals
and post-level technique classification answer different questions and
should be interpreted separately.

## Architecture

```text
Browser
  |
  | HTTPS
  v
Caddy (TLS / reverse proxy)
  |
  +----> Streamlit UI (:8501)
  |
  +----> FastAPI (:8000)
             |
             +----> Coordination analysis
             |
             +----> NVIDIA Nemotron inference
             |
             +----> Google Gemini analysis (when enabled)
```

The deployed application uses Docker Compose services for the API, UI
and Caddy reverse proxy.

## API

The API contract is documented in
[`docs/contract.md`](docs/contract.md).

### `POST /analyze`

Accepts a JSON object containing a `posts` array. Each post uses this
shape:

```json
{
	"posts": [
		{
			"id": "p1",
			"account": "user_a",
			"text": "Example post text",
			"timestamp": "2026-11-13T21:00:00Z",
			"reply_to": null,
			"image_url": null
		}
	]
}
```

### `GET /health`

Returns the service health status.

### URL analysis

The backend also provides `POST /analyze/urls` for supported webpage and
social-post URL inputs. Ordinary webpages can be collected and analyzed
as page content. Social-platform URLs may require platform API access or
authentication; URL recognition does not mean the post can always be
retrieved.

A single webpage/article can be analyzed for content and possible
techniques, but **one URL cannot establish coordinated behaviour**.
Swarm detection requires a batch of posts with account identifiers and
timestamps.

## Evaluation and reproducibility

The repository includes labelled synthetic datasets and evaluation
tooling. Before publication, benchmark results should be regenerated
from the committed code and datasets and saved under `reports/`.

Report at least:

- Dataset size and composition (posts and unique accounts)
- True positives, false positives, true negatives and false negatives
- Precision, recall and F1
- False-positive rate
- Results for each component separately and for any combined decision
  rule, where implemented
- Important failure cases and known limitations

Always identify synthetic data as synthetic. Small synthetic benchmarks
are useful for repeatable engineering checks, but they are not a
substitute for evaluation on representative real-world data. Do not
present synthetic scores as expected real-world performance.

## Limitations and responsible use

- **Coordination is not proof of malicious intent.** Activists,
  newsrooms, fandoms and ordinary communities can behave in
  coordinated ways.
- **AI classifications can be wrong.** Treat technique labels and
  explanations as decision support, not ground truth.
- **Synthetic examples are limited.** They may not capture the
  diversity and complexity of real campaigns.
- **Platform access is constrained.** Recognizing a social-media URL
  does not guarantee access to its post; platform APIs, authentication
  and rate limits may apply.
- **A single article is not a swarm.** Article analysis and
  multi-account coordination analysis are distinct tasks.

## Team

**Hackathon Larpers** --- Roman and Egor.

---

_Built at Junction 2026._
