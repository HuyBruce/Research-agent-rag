# Research Agent RAG

A provider-tolerant research assistant that combines live web search,
local retrieval-augmented generation (RAG), model-knowledge summaries, and report synthesis.

The project is designed to be demoable even when external model providers are unavailable:

- Web search mode: uses DuckDuckGo HTML search for live web snippets and source URLs.
- Hugging Face mode: uses the Hugging Face Inference API when selected.
- Local LLM mode: uses Ollama at `localhost:11434` when selected.
- Live model mode: uses Gemini through `google-genai` when `GEMINI_API_KEY` is configured.
- Fallback mode: runs deterministic local responses when the provider key is missing,
  out of quota, denied, or Ollama is not running.

## Features

- Planner stage that decomposes a research query into web, knowledge, and paper-retrieval tasks.
- Web search stage that retrieves current/external source snippets.
- Knowledge stage that calls Ollama/Gemini when available.
- RAG stage backed by persistent ChromaDB for local document retrieval.
- Writer stage that synthesizes a concise report with citation markers.
- Document ingestion from PDF, raw text, or UTF-8 text/markdown files.
- Runtime chat commands for provider/model/web/fallback selection.
- Evaluation script for success rate, latency, citation coverage, and source count.

## Architecture

```text
User Query
  -> PlannerAgent      Creates web, knowledge, and paper retrieval tasks
  -> WebSearchAgent    Retrieves live web snippets and URLs
  -> KnowledgeAgent    Produces Ollama/Gemini model-knowledge summaries
  -> RAGAgent          Retrieves local ChromaDB excerpts
  -> WriterAgent       Synthesizes a structured cited report
```

## Stack

- Python 3.11+
- DuckDuckGo HTML search for web snippets, no API key required
- Ollama local LLM, optional
- Gemini API via `google-genai`
- Hugging Face Inference API via stdlib HTTP, optional
- ChromaDB for persistent local vector search
- ChromaDB default embedding function
- pypdf for PDF ingestion

## Quick Start

From this repo on Windows:

```cmd
cd /d "D:\Github\Research-agent-rag"
copy .env.example .env
run.cmd --doctor
chat.cmd
```

Use `run.cmd --query "..."` for one-shot questions, or `chat.cmd` for the interactive research chatbot. The launchers use the local Python 3.11 install path on this Windows machine to avoid broken virtualenv launchers in non-ASCII paths.

Install dependencies if needed:

```cmd
"%LOCALAPPDATA%\Programs\Python\Python311\python.exe" -m pip install -r requirements.txt
```

## Ollama Setup

Recommended local LLM mode:

```cmd
"%LOCALAPPDATA%\Programs\Ollama\ollama.exe" pull llama3.2:1b
"%LOCALAPPDATA%\Programs\Ollama\ollama.exe" run llama3.2:1b
```

If `ollama` is already on PATH:

```cmd
ollama pull llama3.2:1b
ollama run llama3.2:1b
```

Select Ollama in chat with:

```cmd
/provider ollama
/model llama3.2:1b
```

`llama3.2:1b` is the easiest local demo model. `llama3.2:3b` is better quality if your machine can run it.

## Provider Setup

Create local config:

```cmd
copy .env.example .env
```

Edit `.env`:

```text
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
HF_API_TOKEN=
HF_MODEL=HuggingFaceTB/SmolLM2-1.7B-Instruct
HF_MAX_NEW_TOKENS=700
HF_TEMPERATURE=0.2
LLM_PROVIDER=gemini
DISABLE_OLLAMA=1
ALLOW_LOCAL_FALLBACK=0
ENABLE_WEB_SEARCH=1
WEB_SEARCH_PROVIDER=duckduckgo
WEB_SEARCH_LIMIT=5
```

`gemini-2.5-flash` is the recommended model for the Google AI Studio free tier.
With `LLM_PROVIDER=gemini`, the app uses Gemini first and does not call Ollama.
Use `LLM_PROVIDER=auto` only if you want Gemini first, then Ollama as fallback.
Keep `ALLOW_LOCAL_FALLBACK=0` if you want provider/API errors to fail loudly
instead of producing a generic offline demo answer.

Set `HF_API_TOKEN` only if your selected Hugging Face model requires authentication. Leaving it empty is safer than using a placeholder token.

Check the active config:

```cmd
run.cmd --doctor
```

## Chat Commands

```text
/status
/provider gemini
/provider huggingface
/provider ollama
/provider auto
/model gemini-2.5-flash
/fallback on
/fallback off
/web on
/web off
/help
```

Provider behavior:

```text
gemini = use Gemini only
huggingface = use Hugging Face Inference API only
ollama = use Ollama only
auto = try Gemini, then Hugging Face, then Ollama if enabled
```

Hugging Face examples:

```text
/provider huggingface
/model HuggingFaceTB/SmolLM2-1.7B-Instruct
```

Some Hugging Face hosted models require `HF_API_TOKEN` or may be unavailable on
the free serverless endpoint. If that happens, choose another public text
generation model or add your Hugging Face token in `.env`.

## Ingest Sample Data

The repo includes sample documents about RAG, agents, vector databases, web grounding, LLMs, Hugging Face, evaluation, and provider tradeoffs.

```cmd
ingest.cmd --file sample_documents\rag_overview.txt --title "RAG Overview" --id rag_overview
ingest.cmd --file sample_documents\rag_best_practices.md --title "RAG Best Practices" --id rag_best_practices
ingest.cmd --file sample_documents\huggingface_inference.md --title "Hugging Face Inference" --id huggingface_inference
```

Run a query against the indexed sample:

```cmd
run.cmd --query "Explain RAG best practices from my local documents."
```

Run chatbot mode so you do not need to restart for every question:

```cmd
chat.cmd
```

Type `exit` to quit chat mode.

Useful local-document questions:

```text
what does the local document say about Hugging Face provider?
explain RAG best practices from my local documents
compare local and cloud models using my documents
```

## Evaluation

```cmd
"%LOCALAPPDATA%\Programs\Python\Python311\python.exe" eval.py
```

Results are written to `sample_outputs/eval_results.json`.

## Project Structure

```text
research-agent-rag/
  src_agents/
    llm_client.py
    planner_agent.py
    search_agent.py
    web_search_agent.py
    runtime_config.py
    rag_agent.py
    writer_agent.py
  sample_documents/
    rag_overview.txt
    rag_best_practices.md
    huggingface_inference.md
    ...
  sample_outputs/
    rag_report.md
  run.cmd
  chat.cmd
  ingest.cmd
  ingest.py
  manager.py
  main.py
  eval.py
  PROJECT_SUMMARY.md
```

## Notes

- Do not commit `.venv`, `chroma_db`, API keys, or `__pycache__`.
- `chroma_db` is local runtime state; rebuild it with `ingest.py`.
- Default provider is Gemini with Ollama disabled.
- Web search is enabled by default with DuckDuckGo HTML search.
- Keep `ALLOW_LOCAL_FALLBACK=0` for honest errors instead of generic demo answers.
