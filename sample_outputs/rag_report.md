# Sample Output: RAG Overview

Query:

```text
What is RAG and how does ChromaDB help?
```

Report:

```text
Overview
Retrieval-Augmented Generation (RAG) improves LLM answers by retrieving relevant external documents before generation. Instead of relying only on model parameters, the system embeds a user query, searches a vector database for similar chunks, and passes those chunks into the model as context.

Key Findings
- RAG combines retrieval and generation: retrieval finds relevant context, and generation turns that context into a natural-language answer.
- Vector databases such as ChromaDB are commonly used to store and search document embeddings for semantic similarity.
- RAG quality depends heavily on chunking, embedding quality, retrieval ranking, prompt construction, and citation handling. [Knowledge: local fallback]

Technical Details
The local ChromaDB retrieval results were included as paper context. [Paper: RAG Overview]

Conclusion
RAG is useful when an LLM must answer from private, changing, or source-grounded data. It does not guarantee correctness by itself, but it gives the model better evidence and makes the system easier to evaluate.
```
