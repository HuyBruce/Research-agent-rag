# Research Agent RAG

A provider-tolerant multi-agent research assistant that combines structured planning,
local retrieval-augmented generation (RAG), and report synthesis.

The project is designed to be demoable even when external model providers are unavailable:

- Local LLM mode: uses Ollama at `localhost:11434` when available.
- Live mode: uses Gemini through `google-genai` when `GEMINI_API_KEY` is configured.
- Fallback mode: runs deterministic local responses when the provider key is missing,
  out of quota, denied, or Ollama is not running.

## Features

- Planner stage that decomposes a research query into knowledge and paper-retrieval tasks.
- Knowledge stage that calls Ollama/Gemini when available or a local fallback otherwise.
- RAG stage backed by persistent ChromaDB for local document retrieval.
- Writer stage that synthesizes a concise report with citation markers.
- Document ingestion from PDF, raw text, or UTF-8 text/markdown files.
- Evaluation script for success rate, latency, citation coverage, and source count.

## Architecture

```text
User Query
  -> PlannerAgent      Creates knowledge and paper retrieval tasks
  -> KnowledgeAgent    Produces Ollama/Gemini/fallback knowledge summary
  -> RAGAgent          Retrieves local ChromaDB excerpts
  -> WriterAgent       Synthesizes a structured cited report
```

## Stack

- Python 3.11+
- Ollama local LLM, optional but recommended
- Gemini API via `google-genai`
- ChromaDB for persistent local vector search
- ChromaDB default embedding function
- pypdf for PDF ingestion

## Quick Start

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe main.py --query "What is RAG?"
```

On Windows CMD:

```cmd
cd /d "D:\path\to\research-agent-rag"
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py --query "What is RAG?"
```

The app runs without an API key in local fallback mode.

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

The app calls Ollama at `http://localhost:11434` before trying Gemini. Override the model with:

```cmd
setx OLLAMA_MODEL "llama3.2:3b"
```

`llama3.2:1b` is the easiest local demo model. `llama3.2:3b` is better quality if your machine can run it.

## Gemini Setup

Optional cloud fallback:

```cmd
copy .env.example .env
```

Edit `.env`:

```text
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
LLM_PROVIDER=gemini
DISABLE_OLLAMA=1
ALLOW_LOCAL_FALLBACK=0
```

`gemini-2.5-flash` is the recommended model for the Google AI Studio free tier.
With `LLM_PROVIDER=gemini`, the app uses Gemini first and does not call Ollama.
Use `LLM_PROVIDER=auto` only if you want Gemini first, then Ollama as fallback.
Keep `ALLOW_LOCAL_FALLBACK=0` if you want provider/API errors to fail loudly
instead of producing a generic offline demo answer.

Check the active config:

```cmd
run.cmd --doctor
```

## Ingest Sample Data

```cmd
ingest.cmd --file sample_documents\rag_overview.txt --title "RAG Overview" --id rag_overview
```

Run a query against the indexed sample:

```cmd
run.cmd --query "What is RAG and how does ChromaDB help?"
```

Run chatbot mode so you do not need to restart for every question:

```cmd
chat.cmd
```

Type `exit` to quit chat mode.

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
    rag_agent.py
    writer_agent.py
  sample_documents/
    rag_overview.txt
  sample_outputs/
    rag_report.md
  ingest.py
  manager.py
  main.py
  eval.py
  PROJECT_SUMMARY.md
```

## Notes

- Do not commit `.venv`, `chroma_db`, API keys, or `__pycache__`.
- `chroma_db` is local runtime state; rebuild it with `ingest.py`.
- Provider order is Ollama, then Gemini, then deterministic fallback.
