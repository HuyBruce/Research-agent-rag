# Large Language Models Overview

Large Language Models (LLMs) are neural networks trained on large text and code corpora to predict and generate language. They are commonly based on transformer architectures, where attention layers help the model relate tokens across a sequence. LLMs can summarize documents, answer questions, write code, classify text, translate language, and follow natural-language instructions.

LLMs do not store knowledge like a database. Their answers are generated from learned statistical patterns, which means they can be fluent but incorrect. This failure mode is often called hallucination. To reduce hallucination, production systems commonly add tools, retrieval-augmented generation, structured prompts, validation steps, or human review.

Cloud LLMs such as Gemini, Claude, or GPT models are hosted by providers and accessed through APIs. Local LLMs such as LLaMA-family models, Qwen, Mistral, or Gemma can run on a user's machine through runtimes such as Ollama or llama.cpp. Cloud models are usually easier to use and higher quality, while local models offer privacy, offline operation, and no provider quota.

Important tradeoffs when choosing an LLM include output quality, latency, context window, cost, rate limits, privacy, model size, hardware requirements, and tool-calling support.
