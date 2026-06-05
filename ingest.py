"""
Ingest PDFs or text into the ChromaDB vector store.

Usage:
  python -m research_agent_rag.ingest --pdf path/to/paper.pdf --title "Attention Is All You Need"
  python -m research_agent_rag.ingest --text "..." --title "My Note" --id note1
"""
import argparse
import sys
from .agents.rag_agent import index_document

try:
    from pypdf import PdfReader
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False


def ingest_pdf(path: str, title: str) -> None:
    if not HAS_PYPDF:
        print("pypdf not installed. Run: pip install pypdf")
        sys.exit(1)
    reader = PdfReader(path)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    doc_id = path.replace("/", "_").replace(".pdf", "")
    index_document(doc_id, text, metadata={"title": title, "path": path})
    print(f"Indexed '{title}' ({len(text)} chars, {len(reader.pages)} pages)")


def ingest_text(text: str, title: str, doc_id: str) -> None:
    index_document(doc_id, text, metadata={"title": title})
    print(f"Indexed '{title}' ({len(text)} chars)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest documents into RAG store")
    parser.add_argument("--pdf", help="Path to PDF file")
    parser.add_argument("--text", help="Raw text to index")
    parser.add_argument("--title", required=True, help="Document title")
    parser.add_argument("--id", default="doc1", help="Document ID (for text input)")
    args = parser.parse_args()

    if args.pdf:
        ingest_pdf(args.pdf, args.title)
    elif args.text:
        ingest_text(args.text, args.title, args.id)
    else:
        print("Provide --pdf or --text")
        sys.exit(1)
