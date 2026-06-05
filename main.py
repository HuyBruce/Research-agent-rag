import asyncio
import argparse
import os
from manager import ResearchManager


def print_banner() -> None:
    print("=== Research Agent RAG ===")
    print("Provider pipeline: Ollama/Gemini -> Knowledge/RAG -> Writer")
    print("Ollama is used first when running locally; Gemini and fallback are backups.\n")

    if not os.getenv("GEMINI_API_KEY"):
        print("[Config] GEMINI_API_KEY not found. Ollama or local fallback will be used.")


async def run_once(manager: ResearchManager, query: str) -> None:
    if not query:
        query = "Recent advances in LLM reasoning and chain-of-thought prompting"
    await manager.run(query)


async def main(query_arg: str | None = None, chat: bool = False) -> None:
    print_banner()
    manager = ResearchManager()

    if chat:
        print("Chat mode. Type a research question, or type 'exit' to quit.\n")
        while True:
            try:
                query = input("research> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nExiting chat mode.")
                return

            if query.lower() in {"exit", "quit", "q"}:
                print("Exiting chat mode.")
                return
            if not query:
                continue

            await run_once(manager, query)
            print()
        return

    query = query_arg or input("What would you like to research? ").strip()
    await run_once(manager, query)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Research Agent RAG pipeline")
    parser.add_argument("--query", "-q", help="Research question to run non-interactively")
    parser.add_argument("--chat", action="store_true", help="Run multiple questions in one session")
    args = parser.parse_args()
    asyncio.run(main(args.query, args.chat))
