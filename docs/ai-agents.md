---
title: "AI Agents"
description: "Use SerpApi search tools, Markdown results, and API references in AI agents."
---

# AI Agents

An AI agent can call SerpApi to search the web and use the returned text and links when answering a question.

## SerpApi Search Tools

If you use a Python agent SDK, we recommend [SerpApi Search Tools](https://github.com/serpapi/serpapi-search-tools-python). It is a separate package for plugging SerpApi search tools into your agents.

## Request Markdown Results

To write your own search tool with `serpapi.Client`, pass `output="md"`. Markdown is plain text with formatting for headings, links, and tables.

Set your API key as described in [Getting Started](user_guide/getting-started.md#installation), then run:

```python
import os
import serpapi

client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"])
markdown = client.search(engine="google", q="Python release news", output="md")
print(markdown[:500])
```

The example prints the first 500 characters. Pass the full `markdown` string back to your agent as the search tool's result. See [Output Formats](user_guide/output-formats.md) for JSON, Markdown, and HTML examples and the Python values they return.

## API Parameter Reference

Give your coding agent [SerpApi's `llms.txt`](https://serpapi.com/llms.txt) when asking it to write search code. This file lists the Markdown documentation for each API. Ask the agent to read the relevant API page for required parameters, optional filters, and response fields.
