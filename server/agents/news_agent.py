from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
import logging

from .prompts import information_extraction_prompt, sentiment_and_summary_prompt
from schemas.schemas import ExtractedInfo, SentimentAnalysisResult


class NewsAgent:
    """
    NewsAgent is responsible for extracting information from news articles.
    """

    def __init__(self, api_key):
        self.llm = ChatOpenAI(
            model="gpt-4o", temperature=0, api_key=api_key
        )
        self.logger = logging.getLogger(__name__)

    async def extract_info_from_text(self, article_content):
        """
        Extract structured information from article content.
        """
        self.logger.info("Starting information extraction from article")
        try:
            client = self.llm.with_structured_output(ExtractedInfo)

            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", information_extraction_prompt),
                    ("human", "{input}"),
                ]
            )

            chain = {"input": RunnablePassthrough()} | prompt | client
            result = await chain.ainvoke(article_content)
            
            # Validate result against schema
            validated_result = ExtractedInfo.model_validate(result)
            self.logger.info("Successfully extracted information from article")
            return validated_result
            
        except Exception as e:
            self.logger.error(f"Error extracting information from article: {str(e)}")
            raise

    async def analyze_sentiment_and_summarize(self, combined_content):
        """
        Analyze overall sentiment and create a summary from multiple articles.
        Returns a SentimentAnalysisResult with overall sentiment, confidence and summary.
        """
        self.logger.info("Starting sentiment analysis and summarization")
        try:
            # Use the appropriate schema for sentiment analysis
            client = self.llm.with_structured_output(SentimentAnalysisResult)

            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", sentiment_and_summary_prompt),
                    ("human", "{input}"),
                ]
            )

            chain = {"input": RunnablePassthrough()} | prompt | client

            # Process with LLM and return the structured result
            result = await chain.ainvoke(combined_content)
            
            # Validate result against schema
            validated_result = SentimentAnalysisResult.model_validate(result)
            self.logger.info("Successfully completed sentiment analysis and summarization")
            return validated_result
            
        except Exception as e:
            self.logger.error(f"Error during sentiment analysis and summarization: {str(e)}")
            raise
