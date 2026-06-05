import json
from dataclasses import dataclass

from src_agents.llm_client import generate_text


PROMPT = (
    "You are a research planning assistant. Given a query, decide the best strategy:\n"
    "1. Come up with 3-8 web search terms to find current information.\n"
    "2. Come up with 1-3 paper retrieval queries for academic/technical depth.\n"
    "Output a combined plan with both web searches and paper queries."
)


@dataclass
class SearchItem:
    reason: str
    query: str
    source: str


@dataclass
class ResearchPlan:
    searches: list[SearchItem]


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(line for line in lines if not line.strip().startswith("```"))
    return json.loads(text)


def _fallback_plan(query: str) -> ResearchPlan:
    return ResearchPlan(
        searches=[
            SearchItem(
                reason="Gather a high-level model-knowledge summary.",
                query=query,
                source="web",
            ),
            SearchItem(
                reason="Retrieve local paper excerpts for technical grounding.",
                query=query,
                source="papers",
            ),
        ]
    )


async def plan_research(query: str) -> ResearchPlan:
    prompt = f"""{PROMPT}

Return only valid JSON using this exact shape:
{{
  "searches": [
    {{"reason": "...", "query": "...", "source": "web"}},
    {{"reason": "...", "query": "...", "source": "papers"}}
  ]
}}

Use source="web" for model-knowledge research summaries and source="papers" for local ChromaDB retrieval.
Create 2-4 total searches.

User query: {query}
"""
    try:
        data = _extract_json(await generate_text(prompt))
        searches = [
            SearchItem(
                reason=str(item.get("reason", "")).strip(),
                query=str(item.get("query", query)).strip() or query,
                source=str(item.get("source", "web")).strip().lower(),
            )
            for item in data.get("searches", [])
        ]
        searches = [s for s in searches if s.source in {"web", "papers"}]
        return ResearchPlan(searches=searches or _fallback_plan(query).searches)
    except Exception:
        return _fallback_plan(query)
