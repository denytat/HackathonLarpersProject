
import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    AnalyzeUrlsRequest,
    AnalyzeUrlsResponse,
    UrlPostResult,
)
from backend.phase2 import run_phase2
from backend.collectors.url_parser import parse_url
from backend.collectors.webpage_collector import (
    collect_webpage,
    WebpageFetchError,
)
from backend.services.nemotron import classify_post

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Swarmwatch",
    description="Detects potentially coordinated social media activity",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
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
        return run_phase2(req.posts)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception:
        logger.exception("Post analysis failed")

        raise HTTPException(
            status_code=500,
            detail="An unexpected analysis error occurred.",
        )


@app.post("/analyze/urls", response_model=AnalyzeUrlsResponse)
def analyze_urls(req: AnalyzeUrlsRequest):
    results = []
    collected_count = 0

    ai_enabled = os.getenv("ENABLE_AI", "false").lower() == "true"

    for index, url in enumerate(req.urls):
        try:
            parsed = parse_url(url)

        except ValueError as error:
            results.append(
                UrlPostResult(
                    input_index=index,
                    url=url,
                    status="invalid",
                    error=str(error),
                )
            )
            continue

        if parsed.platform != "web":
            results.append(
                UrlPostResult(
                    input_index=index,
                    url=url,
                    platform=parsed.platform,
                    post_id=parsed.post_id,
                    content_type=parsed.content_type,
                    domain=parsed.domain,
                    status="access_required",
                    error=(
                        "The link was recognized, but retrieving its content "
                        "requires authorized platform access or imported data."
                    ),
                )
            )
            continue

        try:
            webpage = collect_webpage(url)

        except WebpageFetchError as error:
            results.append(
                UrlPostResult(
                    input_index=index,
                    url=url,
                    platform="web",
                    content_type=parsed.content_type,
                    domain=parsed.domain,
                    status="failed",
                    error=str(error),
                )
            )
            continue

        except Exception:
            logger.exception("Unexpected webpage collection error")

            results.append(
                UrlPostResult(
                    input_index=index,
                    url=url,
                    platform="web",
                    content_type=parsed.content_type,
                    domain=parsed.domain,
                    status="failed",
                    error="An unexpected webpage collection error occurred.",
                )
            )
            continue

        collected_count += 1

        article_text = webpage["text"]
        analysis = None

        if ai_enabled:
            try:
                analysis = classify_post(article_text[:12000])

            except Exception:
                logger.exception(
                    "Nemotron URL analysis failed for %s",
                    url,
                )

                analysis = {
                    "status": "unavailable",
                    "error": "AI classification could not be completed.",
                }

        results.append(
            UrlPostResult(
                input_index=index,
                url=url,
                platform="web",
                content_type=webpage["content_type"],
                domain=webpage["domain"],
                title=webpage["title"],
                text=article_text[:12000],
                status="collected",
                analysis=analysis,
            )
        )

    return AnalyzeUrlsResponse(
        results=results,
        collected_count=collected_count,
    )
