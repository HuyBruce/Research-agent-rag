from pydantic import BaseModel
from agents import Agent, ModelSettings


PROMPT = (
    "You are a research planning assistant. Given a query, decide the best strategy:\n"
    "1. Come up with 3-8 web search terms to find current information.\n"
    "2. Come up with 1-3 paper retrieval queries for academic/technical depth.\n"
    "Output a combined plan with both web searches and paper queries."
)


class SearchItem(BaseModel):
    reason: str
    "Why this search helps answer the query."
    query: str
    "The search term."
    source: str
    "Either 'web' or 'papers'"


class ResearchPlan(BaseModel):
    searches: list[SearchItem]
    "List of searches to perform across web and paper database."


planner_agent = Agent(
    name="PlannerAgent",
    instructions=PROMPT,
    model="gpt-4o-mini",
    output_type=ResearchPlan,
)
