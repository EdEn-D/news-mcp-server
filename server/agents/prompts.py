information_extraction_prompt = '''
# Goal
1. Process a news article's title and description
2. Extract structured information about people, organizations, locations, and key quotes
3. Return the information in a specific JSON format

# Task
Analyze the provided article content and extract:
1. All named people mentioned in the article
2. All organizations mentioned in the article
3. All locations mentioned in the article
4. Important quotes from the article (if any)

# Output Format
Return only a valid JSON object with the following structure:
```json
{{
  "fetched_article_title": "The exact title of the article processed",
  "people": ["Person 1", "Person 2", ...],
  "organizations": ["Organization 1", "Organization 2", ...],
  "locations": ["Location 1", "Location 2", ...],
  "key_quotes": ["Quote 1", "Quote 2", ...]
}}
```

# Guidelines for Extraction:
- For `people`: Extract full names of individuals mentioned
- For `organizations`: Include companies, institutions, government bodies, events, etc.
- For `locations`: Include countries, cities, regions, etc.
- For `key_quotes`: Extract direct quotes if present, identified by quotation marks
- If any category has no entries, return an empty array []
- Be precise and only extract entities that are explicitly mentioned
- Do not infer entities that aren't clearly stated in the text
- Do not add any explanation or commentary outside the JSON structure

# Example:
Title : "Apple announces new iPhone at California event"
Description: "CEO Tim Cook unveiled the latest iPhone model at their Cupertino headquarters, saying 'This is the best iPhone we've ever made'"

The output should be:
```json
{{
  "result": {{
    "fetched_article_title": "Apple announces new iPhone at California event",
    "people": ["Tim Cook"],
    "organizations": ["Apple"],
    "locations": ["California", "Cupertino"],
    "key_quotes": ["This is the best iPhone we've ever made"]
  }}
}}
```

Return only the JSON response without any additional explanation.
'''

sentiment_and_summary_prompt = '''
# Goal
Analyze multiple news articles about a specific topic to:
1. Determine overall sentiment across the articles
2. Generate a concise summary of key takeaways
3. Return the information in a specific JSON format

# Analysis Tasks
Collectively across all articles:
1. **Sentiment Analysis**:
   - Determine if the overall tone across articles is Positive, Negative, or Neutral
   - Assess confidence level in sentiment judgment (Low, Medium, High)
   - Consider language nuance, context, and consistency across articles

2. **Key Takeaway Summary**:
   - Generate a concise (1-2 sentence) summary capturing the most important findings
   - Focus on main trends, developments, or points of agreement across articles

# Output Format
Return only a valid JSON object with the following structure:
```json
{{
  "overall_sentiment": "Positive", // Positive, Negative, or Neutral
  "sentiment_confidence": "Medium", // Low, Medium, or High
  "key_takeaway_summary": "Concise 1-2 sentence summary of the main points from all articles."
}}
```

# Guidelines for Analysis:
- **Sentiment Analysis**:
  - "Positive": Articles generally express optimism, growth, opportunity, or success
  - "Negative": Articles generally express concern, decline, criticism, or failure
  - "Neutral": Articles present balanced view or factual reporting without clear bias
  - Confidence levels should reflect consistency across articles and clarity of sentiment

- **Takeaway Summary**:
  - Prioritize fact-based observations over speculation
  - Highlight trends, patterns, or significant developments
  - Focus on information that would be most valuable to someone researching the topic

## Example:
If analyzing 3 articles about "renewable energy investment trends" that generally discuss increasing investments but with some regional concerns, the output might be:

```json
{{
  "overall_sentiment": "Positive",
  "sentiment_confidence": "Medium",
  "key_takeaway_summary": "Global renewable energy investments are reaching record levels in 2025, with particularly strong growth in solar and wind sectors, though policy uncertainty in some regions threatens continued expansion."
}}
```

Return only the JSON response without any additional explanation.
'''