import asyncio
import os
from .manager import ResearchManager


async def main() -> None:
    print("=== Research Agent RAG ===")
    print("Multi-agent pipeline: Planner → Search/RAG → Writer")
    print("Set OPENAI_API_KEY before running.\n")

    query = input("What would you like to research? ").strip()
    if not query:
        query = "Recent advances in LLM reasoning and chain-of-thought prompting"

    manager = ResearchManager()
    result = await manager.run(query)
    return result


if __name__ == "__main__":
    asyncio.run(main())
