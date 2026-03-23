"""Filter and deduplicate papers from search results."""
import json, os, re

STEPS_DIR = r"C:\Users\23294\.gemini\antigravity\brain\e9c3c668-1736-4304-ba17-f9fa06417ec4\.system_generated\steps"
STEP_IDS = [56, 57, 58, 59, 60, 64, 65, 66, 67, 68]

# Relevance keywords - must match at least 2
CORE_KEYWORDS = [
    "world model", "dreamer", "rssm", "model-based reinforcement", "model based reinforcement",
    "mbrl", "imagination", "rollout", "dyna", "model predictive control rl",
    "model staleness", "model error", "compound error", "compounding error",
    "adaptive horizon", "rollout length", "rollout horizon", "imagination horizon",
    "model update", "update ratio", "model:actor", "model-actor",
    "policy-aware", "policy aware", "policy weighted", "policy-weighted",
    "replay buffer", "experience replay", "off-policy", "distribution shift",
    "ensemble", "uncertainty", "epistemic", "aleatoric", "disagreement",
    "sample efficiency", "data efficiency", "training stability", "training dynamics",
    "td-mpc", "tdmpc", "muzero", "efficientzero", "plan2explore",
    "latent dynamics", "latent state", "state space model",
    "value estimation", "value expansion", "model-based value",
    "trust region", "model accuracy", "model error accumulation",
    "mopo", "mbpo", "pets", "planet", "simpl", 
]

EXCLUDE_PATTERNS = [
    "autonomous driv", "self-driving", "vehicle", "traffic", 
    "energy", "power grid", "microgrid", "frequency control",
    "federated learning", "communication", "network scheduling",
    "battery", "charging", "medical", "clinical", "brain stimulation",
    "chemistry", "molecular", "protein", "drug",
    "natural language", "large language model", "llm", "gui agent",
    "computer vision survey", "attention mechanism survey",
    "6g", "5g", "oran", "o-ran", "iot", "internet of things",
    "metaverse", "quantum", "fintech", "cryptocurrency",
    "urban", "building", "hvac", "heating",
    "autonomous driving car following",
    "pdf form", "word doc",
    "event horizon telescope", "black hole",
    "supply chain", "logistics", "warehouse",
    "covid", "vaccine", "epidem", "health policy",
    "vulnerability", "cybersecurity", "forensic",
    "pollution", "ventilation",
    "astronomy", "astrophys",
    "video generation", "video world model",
    "robot manipulation", "humanoid",
    "mobile gui", "web agent",
    "sepsis", "cardiovascular",
    "financial", "stock",
]

def is_relevant(paper):
    title = (paper.get("title") or "").lower()
    abstract = (paper.get("abstract") or "").lower()
    text = title + " " + abstract
    
    if not paper.get("title") or len(paper["title"].strip()) < 5:
        return False
    
    for pat in EXCLUDE_PATTERNS:
        if pat in text:
            if any(k in text for k in ["dreamer", "rssm", "dyna-style", "model-based reinforcement learning", "mbrl", "model-based policy optimization"]):
                break
            return False
    
    matches = sum(1 for k in CORE_KEYWORDS if k in text)
    title_signals = sum(1 for k in ["world model", "dreamer", "rssm", "model-based", "imagination", "rollout", "dyna", "mbrl", "model error", "uncertainty", "ensemble"] if k in title)
    
    if title_signals >= 2:
        return True
    if matches >= 3:
        return True
    if title_signals >= 1 and matches >= 2:
        return True
    
    return False

all_papers = []
for sid in STEP_IDS:
    fpath = os.path.join(STEPS_DIR, str(sid), "output.txt")
    if not os.path.exists(fpath):
        print(f"Missing: {fpath}")
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        data = json.loads(f.read())
    papers = data.get("papers", [])
    all_papers.extend(papers)
    print(f"Step {sid}: {len(papers)} papers")

print(f"\nTotal raw papers: {len(all_papers)}")

seen = {}
for p in all_papers:
    title = (p.get("title") or "").strip().lower()
    title_norm = re.sub(r'[^a-z0-9]', '', title)
    if not title_norm or len(title_norm) < 10:
        continue
    if title_norm in seen:
        existing = seen[title_norm]
        if len(p.get("abstract") or "") > len(existing.get("abstract") or ""):
            seen[title_norm] = p
    else:
        seen[title_norm] = p

deduped = list(seen.values())
print(f"After dedup: {len(deduped)}")

relevant = [p for p in deduped if is_relevant(p)]
relevant.sort(key=lambda x: x.get("cited_by_count", 0) or 0, reverse=True)
print(f"Relevant papers: {len(relevant)}")

print("\n" + "=" * 130)
print(f"{'#':>3} | {'Title':65} | {'Year':>4} | {'Cites':>5} | {'OA':>3} | {'Source':12}")
print("-" * 130)
for i, p in enumerate(relevant, 1):
    title = (p.get("title") or "")[:65]
    year = p.get("year") or "?"
    cites = p.get("cited_by_count", 0)
    oa = "Y" if p.get("is_oa") else ""
    src = p.get("source", "")[:12]
    print(f"{i:>3} | {title:65} | {year:>4} | {cites:>5} | {oa:>3} | {src:12}")

corpus_entries = []
for i, p in enumerate(relevant, 1):
    entry = {
        "id": i,
        "title": p.get("title", ""),
        "authors": p.get("authors", []),
        "year": p.get("year"),
        "venue": p.get("venue", ""),
        "doi": p.get("doi"),
        "arxiv_id": p.get("arxiv_id"),
        "cited_by_count": p.get("cited_by_count", 0),
        "is_oa": p.get("is_oa", False),
        "pdf_url": p.get("pdf_url", ""),
        "source": p.get("source", ""),
        "abstract": (p.get("abstract") or "")[:500],
        "access_state": "pending",
        "publishable": True,
    }
    corpus_entries.append(entry)

corpus = {"entries": corpus_entries, "total": len(corpus_entries)}
out_path = r"e:\桌面\world model idea3\corpus_ledger.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(corpus, f, indent=2, ensure_ascii=False)

print(f"\nCorpus ledger saved to {out_path} with {len(corpus_entries)} entries.")
