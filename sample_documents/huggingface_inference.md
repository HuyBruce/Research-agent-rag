# Hugging Face Inference

Hugging Face hosts model repositories and provides multiple ways to run open models. The simplest integration is the Hugging Face Inference API, which accepts HTTP requests for supported hosted models. Some models work on the free serverless endpoint, while others require a token, paid endpoint, or local deployment.

Using Hugging Face can reduce reliance on a single provider such as Gemini. Developers can switch between model IDs and test smaller open models for demos. However, hosted Hugging Face inference still has rate limits, cold starts, model availability constraints, and possible token requirements.

For stronger control, developers can run Hugging Face models locally with the Transformers library, Text Generation Inference, vLLM, or llama.cpp-compatible exports when available. Local hosting requires more setup but avoids serverless endpoint limitations.

In a research-agent project, Hugging Face is best treated as another provider option. The agent should expose provider and model selection, report errors clearly, and allow fallback to local or offline modes.
