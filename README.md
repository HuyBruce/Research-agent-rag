# Research Agent RAG

A multi-agent research pipeline built on [openai-agents-python](https://github.com/openai/openai-agents-python) with RAG (Retrieval-Augmented Generation) via ChromaDB.

## Architecture

```
User Query
    │
    ▼
PlannerAgent          → Decomposes query into web + paper search tasks
    │
    ▼ (parallel)
SearchAgent ×N        → Web search via WebSearchTool, returns summaries + URLs
RAGAgent    ×N        → Retrieves from local ChromaDB vector store, returns excerpts + citations
    │
    ▼
WriterAgent           → Synthesizes all sources into a structured report with citations
```

## Stack

- **Agent framework**: openai-agents-python (tool calling, handoffs, guardrails)
- **Vector DB**: ChromaDB (persistent local store)
- **Embeddings**: ChromaDB default (all-MiniLM-L6-v2)
- **Models**: gpt-4o-mini (search/rag/writer), gpt-4o-mini (planner)
- **PDF parsing**: pypdf

## Setup

```bash
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
```

## Usage

```bash
# Run the research agent
python -m research_agent_rag.main

# Index a paper into the RAG store
python -m research_agent_rag.ingest --pdf paper.pdf --title "Attention Is All You Need"

# Run eval suite
python -m research_agent_rag.eval
```

## Eval Results

| Metric | Value |
|---|---|
| Citation rate | ~80% |
| Avg latency | ~12s |
| Test queries | 10 |

## Project structure

```
research_agent_rag/
├── agents/
│   ├── planner_agent.py   # Decomposes query into search plan
│   ├── search_agent.py    # Web search via WebSearchTool
│   ├── rag_agent.py       # ChromaDB retrieval tool
│   └── writer_agent.py    # Synthesis + citation
├── manager.py             # Orchestrates the pipeline
├── ingest.py              # Index PDFs/text into ChromaDB
├── eval.py                # Automated evaluation suite
└── main.py                # CLI entry point
```
