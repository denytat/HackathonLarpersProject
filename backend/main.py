from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Swarmwatch")

class Post(BaseModel):
    id: str
    account: str
    text: str
    timestamp: str
    reply_to: Optional[str] = None
    image_url: Optional[str] = None

class AnalyzeRequest(BaseModel):
    posts: list[Post]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    return {
        "swarms": [{
            "id": "s1",
            "accounts": sorted({p.account for p in req.posts})[:3],
            "score": 0.87,
            "evidence": ["STUB: 3 accounts posted near-identical text within 90 seconds"],
        }],
        "posts": [{
            "id": p.id,
            "techniques": [{"name": "fear_appeal", "span": p.text[:40],
                            "explanation": "STUB explanation"}],
            "verdict": "uncertain",
            "confidence": 0.5,
            "flagged_by": ["timing"],
        } for p in req.posts],
    }