import requests
import os
import logging
from typing import List
from schemas.schemas import SearchNewsRequest, SearchNewsResponse, Article

# Create a logger for this module
logger = logging.getLogger(__name__)


def log_api_request(url: str, params: dict) -> None:
    """Log details about an outgoing API request (with sensitive data redacted)."""
    log_params = params.copy()
    if "apiKey" in log_params:
        log_params["apiKey"] = "REDACTED"

    logger.info(f"API Request: GET {url} with params: {log_params}")


def log_api_response(
    status_code: int, response_status: str, articles_count: int
) -> None:
    """Log summarized information about an API response."""
    logger.info(
        f"API Response: status_code={status_code}, api_status={response_status}, "
        f"articles_retrieved={articles_count}"
    )


def log_api_error(error_type: str, error_message: str, details: dict = None) -> None:
    """Log detailed information about API errors."""
    if details is None:
        details = {}
    logger.error(f"{error_type}: {error_message}", extra={"details": details})


def search_news_api(request: SearchNewsRequest, api_key: str) -> SearchNewsResponse:
    """
    Search for recent news articles matching a specific query.
    """
    try:
        url = "https://newsapi.org/v2/everything"

        params = {
            "q": request.query,
            "language": request.language,
            "sortBy": "publishedAt",
            "apiKey": api_key,
            "pageSize": request.pageSize,
        }

        # Log the API request (replacing the print statement)
        log_api_request(url, params)

        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors

        data = response.json()

        # Log the API response
        log_api_response(
            response.status_code, data["status"], len(data.get("articles", []))
        )

        if data["status"] != "ok":
            log_api_error(
                "NewsAPIError",
                data.get("message", "Unknown error"),
                {"status_code": response.status_code, "query": request.query},
            )
            raise Exception(f"News API error: {data.get('message', 'Unknown error')}")

        articles = []
        for article in data["articles"]:
            articles.append(
                Article(
                    title=article["title"],
                    description=article["description"] or "",
                    url=article["url"],
                    source_name=article["source"]["name"],
                    published_at=article["publishedAt"],
                )
            )

        return SearchNewsResponse(articles=articles)
    except requests.RequestException as e:
        log_api_error("RequestException", str(e), {"query": request.query})
        raise Exception(f"Error fetching news: {str(e)}")
    except Exception as e:
        log_api_error("UnexpectedException", str(e), {"query": request.query})
        raise Exception(f"Internal server error: {str(e)}")


def get_top_headlines_api(
    request: SearchNewsRequest, api_key: str
) -> SearchNewsResponse:
    """
    Get top headlines matching a specific query.
    """
    try:
        url = "https://newsapi.org/v2/top-headlines"

        params = {
            "q": request.query,
            "pageSize": request.pageSize,
            "apiKey": api_key,
        }

        # Log the API request
        log_api_request(url, params)

        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors

        data = response.json()

        # Log the API response
        log_api_response(
            response.status_code, data["status"], len(data.get("articles", []))
        )

        if data["status"] != "ok":
            log_api_error(
                "NewsAPIError",
                data.get("message", "Unknown error"),
                {"status_code": response.status_code, "query": request.query},
            )
            raise Exception(f"News API error: {data.get('message', 'Unknown error')}")

        articles = []
        for article in data["articles"]:
            articles.append(
                Article(
                    title=article["title"],
                    description=article["description"] or "",
                    url=article["url"],
                    source_name=article["source"]["name"],
                    published_at=article["publishedAt"],
                )
            )

        return SearchNewsResponse(articles=articles)
    except requests.RequestException as e:
        log_api_error("RequestException", str(e), {"query": request.query})
        raise Exception(f"Error fetching news: {str(e)}")
    except Exception as e:
        log_api_error("UnexpectedException", str(e), {"query": request.query})
        raise Exception(f"Internal server error: {str(e)}")
