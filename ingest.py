"""
Ingest PDFs or text into the ChromaDB vector store.

Usage:
  python ingest.py --pdf path/to/paper.pdf --title "Attention Is All You Need"
  python ingest.py --file sample_documents/rag_overview.txt --title "RAG Overview" --id rag_overview
  python ingest.py --text "..." --title "My Note" --id note1
"""
import argparse
from pathlib import Path
import sys
from src_agents.rag_agent import index_document

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


def ingest_file(path: str, title: str, doc_id: str) -> None:
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")
    index_document(doc_id, text, metadata={"title": title, "path": str(file_path)})
    print(f"Indexed '{title}' from {file_path} ({len(text)} chars)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest documents into RAG store")
    parser.add_argument("--pdf", help="Path to PDF file")
    parser.add_argument("--file", help="Path to a UTF-8 text/markdown file")
    parser.add_argument("--text", help="Raw text to index")
    parser.add_argument("--title", required=True, help="Document title")
    parser.add_argument("--id", default="doc1", help="Document ID (for text input)")
    args = parser.parse_args()

    if args.pdf:
        ingest_pdf(args.pdf, args.title)
    elif args.file:
        ingest_file(args.file, args.title, args.id)
    elif args.text:
        ingest_text(args.text, args.title, args.id)
    else:
        print("Provide --pdf, --file, or --text")
        sys.exit(1)
