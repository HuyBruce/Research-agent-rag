# Research Agent RAG Usage Guide

This project is designed to demonstrate a research-agent pipeline with three evidence channels: web search, local RAG, and model knowledge. Web search provides current external snippets and URLs. Local RAG retrieves documents that were ingested into ChromaDB. Model knowledge gives background explanation from the selected LLM provider.

The recommended default provider is Gemini 2.5 Flash when quota is available. If Gemini quota is exhausted, the user can switch to Hugging Face or Ollama with chat commands. Hugging Face can use hosted open models. Ollama can run local models such as llama3.2 when installed.

Useful chat commands include `/status`, `/provider gemini`, `/provider huggingface`, `/provider ollama`, `/model <model-name>`, `/web on`, `/web off`, `/fallback on`, and `/fallback off`.

For best RAG behavior, ingest local documents before asking questions about private or project-specific material. The agent stores indexed chunks in the ChromaDB directory and retrieves relevant excerpts when answering.
