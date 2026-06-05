import os
import chromadb
from chromadb.utils import embedding_functions
from agents import Agent, function_tool

# --- ChromaDB setup ---
_client = chromadb.PersistentClient(path="./chroma_db")
_ef = embedding_functions.DefaultEmbeddingFunction()
_collection = _client.get_or_create_collection(
    name="papers",
    embedding_function=_ef,
)


def index_document(doc_id: str, text: str, metadata: dict = None) -> None:
    """Index a document (paper/article) into the vector store."""
    chunks = [text[i:i+500] for i in range(0, len(text), 400)]
    _collection.upsert(
        documents=chunks,
        ids=[f"{doc_id}_chunk_{i}" for i in range(len(chunks))],
        metadatas=[{**(metadata or {}), "source": doc_id} for _ in chunks],
    )


@function_tool
def retrieve_from_papers(query: str, n_results: int = 4) -> str:
    """
    Search the local vector database of indexed AI papers.
    Use this when the question is about specific papers, research findings,
    or when web search might not have the latest academic content.
    Returns relevant excerpts with source info.
    """
    count = _collection.count()
    if count == 0:
        return "No papers indexed yet. Use web search instead."

    results = _collection.query(
        query_texts=[query],
        n_results=min(n_results, count),
    )
    docs = results["documents"][0]
    metas = results["metadatas"][0]

    output_parts = []
    for doc, meta in zip(docs, metas):
        source = meta.get("source", "unknown")
        title = meta.get("title", source)
        output_parts.append(f"[Source: {title}]\n{doc}")

    return "\n\n---\n\n".join(output_parts)


RAG_INSTRUCTIONS = (
    "You are a research assistant specializing in AI/ML papers. "
    "Given a search query, use the retrieve_from_papers tool to find relevant excerpts "
    "from the local paper database. Summarize the findings in 2-3 paragraphs under 300 words. "
    "Always cite the source document name. If the database has no relevant results, say so clearly."
)

rag_agent = Agent(
    name="RAGAgent",
    model="gpt-4o-mini",
    instructions=RAG_INSTRUCTIONS,
    tools=[retrieve_from_papers],
)
