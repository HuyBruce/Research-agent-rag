import chromadb
from chromadb.utils import embedding_functions

from src_agents.llm_client import generate_text

# --- ChromaDB setup ---
_client = chromadb.PersistentClient(path="./chroma_db")
_ef = embedding_functions.DefaultEmbeddingFunction()
_collection = _client.get_or_create_collection(
    name="papers",
    embedding_function=_ef,
)
MAX_RELEVANCE_DISTANCE = 1.35


def index_document(doc_id: str, text: str, metadata: dict = None) -> None:
    """Index a document (paper/article) into the vector store."""
    chunks = [text[i:i+500] for i in range(0, len(text), 400)]
    _collection.upsert(
        documents=chunks,
        ids=[f"{doc_id}_chunk_{i}" for i in range(len(chunks))],
        metadatas=[{**(metadata or {}), "source": doc_id} for _ in chunks],
    )


def retrieve_from_papers(query: str, n_results: int = 4) -> str:
    """
    Search the local vector database of indexed AI papers.
    Use this when the question is about specific papers, research findings,
    or when web search might not have the latest academic content.
    Returns relevant excerpts with source info.
    """
    count = _collection.count()
    if count == 0:
        return "No papers indexed yet. Use the knowledge summary instead."

    results = _collection.query(
        query_texts=[query],
        n_results=min(n_results, count),
        include=["documents", "metadatas", "distances"],
    )
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]

    output_parts = []
    for doc, meta, distance in zip(docs, metas, distances):
        if distance > MAX_RELEVANCE_DISTANCE:
            continue
        source = meta.get("source", "unknown")
        title = meta.get("title", source)
        output_parts.append(f"[Source: {title}]\n{doc}")

    if not output_parts:
        return "No relevant papers found in the local ChromaDB collection."

    return "\n\n---\n\n".join(output_parts)


RAG_INSTRUCTIONS = (
    "You are a research assistant specializing in AI/ML papers. "
    "Given local paper excerpts, summarize the findings in 2-3 paragraphs under 300 words. "
    "Always cite the source document name. If the database has no relevant results, say so clearly."
)


async def run_rag(query: str) -> str:
    excerpts = retrieve_from_papers(query)
    if excerpts.startswith("No papers indexed") or excerpts.startswith("No relevant papers"):
        return excerpts

    prompt = f"""{RAG_INSTRUCTIONS}

Search query: {query}

Local paper excerpts:
{excerpts}
"""
    return await generate_text(prompt)
