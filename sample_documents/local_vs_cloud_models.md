# Local vs Cloud Models

Cloud models run on provider infrastructure and are accessed through APIs. Examples include Gemini, Claude, GPT, and hosted Hugging Face endpoints. They are convenient because users do not need to manage GPU hardware, model weights, or serving infrastructure.

Local models run on a user's own machine or private server. Examples include LLaMA, Mistral, Qwen, Gemma, and Phi models served through tools like Ollama, LM Studio, or llama.cpp. Local models can work offline and keep data on the user's machine, but quality and speed depend on hardware.

Cloud models are usually stronger for complex reasoning, instruction following, and long-context tasks. Local models are attractive for privacy, cost control, offline demos, and avoiding provider quotas. Hybrid systems can use cloud models when available and local models as fallback.

When building a portfolio project, supporting multiple providers demonstrates engineering maturity. It shows the system is not locked to one API and can degrade gracefully when a provider is unavailable.
