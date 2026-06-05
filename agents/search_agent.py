from agents import Agent, WebSearchTool

INSTRUCTIONS = (
    "You are a research assistant. Given a search term, search the web and produce "
    "a concise summary of the results. The summary must be 2-3 paragraphs and under 300 words. "
    "Capture the main points and include the source URLs at the end. "
    "Do not include fluff — this will be consumed by a synthesis agent."
)

search_agent = Agent(
    name="SearchAgent",
    model="gpt-4o-mini",
    instructions=INSTRUCTIONS,
    tools=[WebSearchTool()],
)
