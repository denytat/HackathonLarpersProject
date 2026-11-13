
from pydantic import BaseModel
from typing import Optional


class PostInput(BaseModel):
    id: str
    account: str
    text: str
    timestamp: str
    reply_to: Optional[str] = None
    image_url: Optional[str] = None


class AnalyzeRequest(BaseModel):
    posts: list[PostInput]


class SwarmResult(BaseModel):
    id: str
    accounts: list[str]
    score: float
    evidence: list[dict]


class TechniqueResult(BaseModel):
    name: str
    span: str
    explanation: str


class PostResult(BaseModel):
    id: str
    techniques: list[TechniqueResult]
    verdict: str
    confidence: float
    flagged_by: list[str]


class AnalyzeResponse(BaseModel):
    swarms: list[SwarmResult]
    posts: list[PostResult]
