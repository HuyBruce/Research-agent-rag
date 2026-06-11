# Vector Databases

Vector databases store numeric embeddings that represent text, images, audio, or other data. In a RAG system, a document chunk is converted into an embedding vector, then stored with metadata. At query time, the user's question is embedded and compared with stored vectors to find semantically similar chunks.

ChromaDB is a lightweight vector database commonly used in local prototypes. It can persist data to disk, manage collections, and run similarity queries. Other vector databases include FAISS, Milvus, Weaviate, Pinecone, Qdrant, and Elasticsearch with vector support.

A vector database is not a replacement for clean data preparation. Poor chunking, duplicated content, missing metadata, and weak embeddings can make retrieval unreliable. For production systems, developers often combine vector search with filters, reranking, keyword search, and observability logs.

Common metadata fields include source, title, document type, page number, section, timestamp, and access level. Metadata makes it possible to filter retrieval results and produce meaningful citations.
