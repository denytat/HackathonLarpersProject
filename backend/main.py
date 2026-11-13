
from fastapi import FastAPI, HTTPException

from backend.schemas import AnalyzeRequest, AnalyzeResponse
from backend.detector import analyze_posts


app = FastAPI(
    title="Swarmwatch",
    description="Detects potentially coordinated social media activity",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Swarmwatch API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):

    try:
        result = analyze_posts(req.posts)
        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
