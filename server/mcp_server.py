import os
import logging
import traceback
from dotenv import load_dotenv, find_dotenv
from typing import Optional
from schemas.schemas import SearchNewsRequest, SearchNewsResponse
from schemas.schemas import (
    ExtractInfoRequest,
    ExtractedInfo,
    ExtractedInfoResult,
    ExtractInfoResponse,
)
from schemas.schemas import (
    ExtractInfoSentinmentRequest,
    KeyInfoResult,
    ExtractInfoSentinmentResponse,
)
from mcp.server.fastmcp import FastMCP

from integrations.news_api import search_news_api, get_top_headlines_api
from agents.news_agent import NewsAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("news_mcp_server.log")
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(find_dotenv())
logger.info("Environment variables loaded")

# Initialize FastMCP server
mcp = FastMCP("news-mcp")
logger.info("FastMCP server initialized")

# Constants
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
if not NEWS_API_KEY:
    logger.warning("NEWS_API_KEY not found in environment variables")

# Initialize NewsAgent
try:
    news_agent = NewsAgent(os.environ.get("LLM_API_KEY"))
    logger.info("NewsAgent initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize NewsAgent: {str(e)}")
    raise


@mcp.tool()
async def search_news(request: SearchNewsRequest) -> SearchNewsResponse:
    """
    Search for recent news articles matching a specific query.
    """
    try:
        return search_news_api(request, NEWS_API_KEY)
    except Exception as e:
        logger.error(f"Error in search_news: {str(e)}")
        logger.debug(traceback.format_exc())
        raise


async def _get_top_headlines(request: SearchNewsRequest) -> SearchNewsResponse:
    """
    Get top headlines matching a specific query.
    """
    try:
        return get_top_headlines_api(request, NEWS_API_KEY)
    except Exception as e:
        logger.error(f"Error in _get_top_headlines: {str(e)}")
        logger.debug(traceback.format_exc())
        raise


@mcp.tool()
async def extract_information_from_article(request: ExtractInfoRequest) -> ExtractInfoResponse:
    """
    Extract structured information from a news article.
    """
    try:
        # First fetch the article using search_news tool
        search_request = SearchNewsRequest(
            query=request.query, language=request.language, pageSize=1
        )
        search_response = await search_news(search_request)

        # Make sure we have at least one article
        if not search_response.articles:
            logger.warning("No articles found for the given query")
            return ExtractInfoResponse(
                result=ExtractedInfoResult(
                    fetched_article_title="",
                    people=[],
                    organizations=[],
                    locations=[],
                    key_quotes=[],
                )
            )

        # Get the first article
        article = search_response.articles[0]
        article_content = f"Title: {article.title}\nDescription: {article.description}"

        # Use NewsAgent to extract information
        extracted_info = await news_agent.extract_info_from_text(article_content)

        # Create and return the response using the correct schema
        response = ExtractInfoResponse(
            result=ExtractedInfoResult(
                fetched_article_title=article.title,
                people=extracted_info.people,
                organizations=extracted_info.organizations,
                locations=extracted_info.locations,
                key_quotes=extracted_info.key_quotes,
            )
        )

        return response
    except Exception as e:
        logger.error(f"Error in extract_information_from_article: {str(e)}")
        logger.debug(traceback.format_exc())
        raise


@mcp.tool()
async def extract_info_and_sentiment(
    request: ExtractInfoSentinmentRequest,
) -> ExtractInfoSentinmentResponse:
    """
    Analyze news articles for key entities and sentiment.
    """
    try:
        # First fetch articles using search_news tool
        search_request = SearchNewsRequest(
            query=request.query,
            language=request.language,
            pageSize=request.max_articles_to_analyze,
        )
        search_response = await _get_top_headlines(search_request)

        # Make sure we have at least one article
        if not search_response.articles:
            logger.warning("No articles found for the given query")
            return ExtractInfoSentinmentResponse(
                status="error",
                result=KeyInfoResult(
                    query=request.query,
                    analyzed_article_count=0,
                    overall_sentiment="Neutral",
                    sentiment_confidence="Low",
                    key_entities=ExtractedInfo(
                        people=[], organizations=[], locations=[], key_quotes=[]
                    ),
                    key_takeaway_summary="No articles found for the given query.",
                ),
            )

        # Combine all articles into one text
        article_contents = []
        for article in search_response.articles:
            article_content = f"Title: {article.title}\nDescription: {article.description}"
            article_contents.append(article_content)

        # Combine all articles into one text
        combined_content = "\n\n".join(article_contents)

        # Extract information once from the combined text
        extracted_info = await news_agent.extract_info_from_text(combined_content)

        # Use NewsAgent to analyze sentiment and summarize
        sentiment_result = await news_agent.analyze_sentiment_and_summarize(
            combined_content
        )

        # Prepare and return the final response
        return ExtractInfoSentinmentResponse(
            status="success",
            result=KeyInfoResult(
                query=request.query,
                analyzed_article_count=len(search_response.articles),
                overall_sentiment=sentiment_result.overall_sentiment,
                sentiment_confidence=sentiment_result.sentiment_confidence,
                key_entities=extracted_info,
                key_takeaway_summary=sentiment_result.key_takeaway_summary,
            ),
        )
    except Exception as e:
        logger.error(f"Error in extract_info_and_sentiment: {str(e)}")
        logger.debug(traceback.format_exc())
        raise


if __name__ == "__main__":
    try:
        # Verify environment variables
        required_env_vars = ["NEWS_API_KEY", "LLM_API_KEY"]
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )
        logger.info("All required environment variables are set")

        # Initialize and run the server
        # check if FASTMCP_PORT is set in env variables, if not set it to 3000
        mcp.settings.port = int(os.getenv("FASTMCP_PORT", 3000))
        logger.info(f"Starting FastMCP server on port {mcp.settings.port}")
        mcp.run(transport="sse")
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        logger.debug(traceback.format_exc())
        raise
