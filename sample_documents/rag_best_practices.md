# RAG Best Practices

Retrieval-Augmented Generation (RAG) improves language model answers by retrieving relevant source material before generation. A basic RAG system ingests documents, splits them into chunks, embeds those chunks, stores them in a vector database, retrieves relevant chunks for a query, and passes those chunks to a model as context.

Good RAG quality depends heavily on chunking. Chunks that are too large may include unrelated material and waste context. Chunks that are too small may lose meaning. Overlapping chunks can preserve continuity across section boundaries. Metadata such as title, source path, author, and date helps the final answer cite and filter sources.

Retrieval quality also depends on the embedding model and search strategy. Dense vector search is useful for semantic similarity. Keyword search is useful for exact names, IDs, and rare terms. Hybrid search combines both approaches and often performs better than either one alone.

The generation prompt should instruct the model to answer only from retrieved context when source grounding matters. If the retrieved context is weak, the model should say so instead of inventing a confident answer. A strong RAG application exposes source citations so users can verify claims.

Evaluation should measure retrieval recall, citation accuracy, answer correctness, latency, and robustness to ambiguous queries.
