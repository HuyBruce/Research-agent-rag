# Prompt Engineering

Prompt engineering is the practice of designing instructions and context so a language model performs a task reliably. Good prompts specify the role, task, input format, output format, constraints, and failure behavior.

For research assistants, prompts should tell the model to separate facts from uncertainty, avoid fake citations, and say when sources are insufficient. Structured output such as JSON is useful for planning because downstream code can parse it. Natural-language output is useful for final reports.

Prompting alone cannot guarantee correctness. Models can ignore instructions, misread context, or generate plausible but false details. Retrieval, tools, validation, and tests are needed for stronger reliability.

Common prompt patterns include few-shot examples, step-by-step decomposition, explicit rubrics, citation requirements, and self-checking. In production, prompts should be versioned and evaluated with representative test cases.
