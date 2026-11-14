from typing import Any, Optional

from pydantic import BaseModel, Field


class PostInput(BaseModel):
    id: str
    account: str
    text: str
    timestamp: str
    reply_to: Optional[str] = None
    image_url: Optional[str] = None


class AnalyzeRequest(BaseModel):
    posts: list[PostInput]


class SwarmAIAnalysis(BaseModel):
    status: str
    gemini: Optional[dict[str, Any]] = None
    verdict: str
    explanation: str


class SwarmResult(BaseModel):
    id: str
    accounts: list[str]
    score: float
    evidence: list[dict]
    ai_analysis: Optional[SwarmAIAnalysis] = None


class TechniqueResult(BaseModel):
    name: str
    span: str
    explanation: str


class PostAIAnalysis(BaseModel):
    status: str
    confidence: float = Field(ge=0, le=1)
    explanation: str


class PostResult(BaseModel):
    id: str
    techniques: list[TechniqueResult]
    verdict: str
    confidence: float
    flagged_by: list[str]
    ai_analysis: Optional[PostAIAnalysis] = None


class AnalyzeResponse(BaseModel):
    swarms: list[SwarmResult]
    posts: list[PostResult]