from src_agents.llm_client import generate_text

INSTRUCTIONS = (
    "You are a research assistant. Given a search term, produce a concise model-knowledge "
    "summary. The summary must be 2-3 paragraphs and under 300 words. "
    "Do not claim live web browsing or include fake URLs. "
    "End with [Knowledge: model knowledge]."
)


async def run_search(query: str) -> str:
    prompt = f"{INSTRUCTIONS}\n\nSearch term: {query}"
    return await generate_text(prompt)


async def run_knowledge_search(query: str) -> str:
    return await run_search(query)
