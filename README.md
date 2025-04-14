# News Analysis MCP Server

A Model Context Protocol (MCP) server for fetching, analyzing, and extracting information from news articles using NewsAPI.org and LLMs.

## Features

- Search for recent news articles by keyword
- Extract structured information (people, organizations, locations, quotes) from articles
- Analyze sentiment and summarize key information across multiple articles
- Implemented as an MCP server for easy integration with LLM applications

## Project Structure

```
latent-task/
├── server/                    # Server implementation
│   ├── agents/                # LLM agents for information extraction
│   ├── integrations/          # External API integrations
│   ├── schemas/               # Pydantic data models
│   └── mcp_server.py          # Main MCP server implementation
├── .env                       # Environment variables (not in version control)
├── Dockerfile                 # Container definition
├── pyproject.toml             # Project dependencies
├── requirements.txt           # Direct dependencies list
└── README.md                  # This file
```

## Prerequisites

- Python 3.11+ recommended
- NewsAPI.org API key
- OpenAI API key (for LLM functionality)
- Docker (optional, for containerized deployment)
- uv (Python package manager)

## Environment Setup

1. Install uv if you don't have it already:
   ```bash
   pip install uv
   # or
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e .
   # or
   uv pip install -r requirements.txt
   ```

3. Create a `.env` file with the required API keys:
   ```
   NEWS_API_KEY="your_news_api_key"
   LLM_API_KEY="your_openai_api_key"

   FASTMCP_PORT=port_number  # Optional, default is 3000
   FASTMCP_HOST="host_name"    # Optional, default is 0.0.0.0
   ```

## Running the Server

### Direct Execution

```bash
python server/mcp_server.py
```

### With Docker

Build the Docker image:
```bash
docker build . -t news-mcp-server
```

Run the container:
```bash
docker run -p 3000:3000 \
  -e NEWS_API_KEY="your_news_api_key" \
  -e LLM_API_KEY="your_openai_api_key" \
  news-mcp-server
```

## MCP Tools

The server implements the following MCP tools:

1. `search_news`: Search for recent news articles matching a specific query
   - Parameters: `query` (string), `language` (string, default "en"), `pageSize` (int, default 5)
   
2. `extract_information_from_article`: Extract structured information from news articles
   - Parameters: `query` (string), `language` (string, default "en")
   
3. `extract_info_and_sentiment`: Analyze news articles for key entities and sentiment
   - Parameters: `query` (string), `language` (string, default "en"), `max_articles_to_analyze` (int, default 5)

## Testing

You can test the MCP server using the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector uv --directory . run server/mcp_server.py
```

1. Set "Transport Type" to "SSE" and "Server URL" to `http://0.0.0.0:3000/sse`.
2. Click "Connect" to establish a connection to the server.
3. Click "Tools" and "List Tools" to see the available tools.
4. You can test each tool with the minimum requrired input such as:
    - `{"query": "latest news"}`

## Use with MCP host such as Claude Desktop

Allow Claude desktop to access the MCP server by adding the following to your `claude_desktop_config.json` file:

### With Docker

```json
{
    "mcpServers": {
        "news_mcp": {
            "command": "docker",
            "args": [
                "run",
				"-i",
				"-p",
				"3000:3000",
				"-e",
				"NEWS_API_KEY=<your_news_api_key>",
				"-e",
				"LLM_API_KEY=<your_openai_api_key>",
				"news-mcp-server"
            ]
        }
    }
}
```

### With remote-mcp
Run the MCP server locally and use the `remote-mcp` tool to connect to it. You can install `remote-mcp` from this repo:
https://github.com/latentsp/remote-mcp


```json
{
    "mcpServers": {
        "news_test": {
            "command": "remote-mcp",
            "args": ["--endpoint-url", "http://0.0.0.0:3000"],
        }
    }
}
```

## Design choices

- The server is designed to be modular, with separate directories for agents, integrations, and schemas.
- The use of Pydantic for data validation and serialization ensures that the input and output data is well-defined and easy to work with.
- LLM calls are instructed to return structured outputs which allow consistent parsing and extraction of information.
- The extract_info_and_sentiment function combines multiple tasks (information extraction and sentiment analysis) into a single call, allowing for more efficient processing of news articles. From several tests, performance is not significantly affected by this design choice, while it simplifies the API and reduces the number of calls to the LLM.