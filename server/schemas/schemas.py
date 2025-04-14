from pydantic import BaseModel
from typing import List

# Schemas for search_news tool
class SearchNewsRequest(BaseModel):
    query: str
    language: str = "en"
    pageSize: int = 5

class Article(BaseModel):
    title: str
    description: str
    url: str
    source_name: str
    published_at: str

class SearchNewsResponse(BaseModel):
    articles: List[Article]

# Schemas for extract_information_from_article tool
class ExtractInfoRequest(BaseModel):
    query: str
    language: str = "en"

class ExtractedInfo(BaseModel):
    people: List[str]
    organizations: List[str]
    locations: List[str]
    key_quotes: List[str]

class ExtractedInfoResult(ExtractedInfo):
    fetched_article_title: str

class ExtractInfoResponse(BaseModel):
    result: ExtractedInfoResult


# Schemas for extract_key_info_and_sentiment tool
class ExtractInfoSentinmentRequest(BaseModel):
    query: str
    language: str = "en"
    max_articles_to_analyze: int = 5

class SentimentAnalysisResult(BaseModel):
    overall_sentiment: str
    sentiment_confidence: str
    key_takeaway_summary: str


class KeyInfoResult(SentimentAnalysisResult):
    query: str
    analyzed_article_count: int
    key_entities: ExtractedInfo


class ExtractInfoSentinmentResponse(BaseModel):
    status: str
    result: KeyInfoResult