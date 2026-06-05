import re

from src_agents.llm_client import generate_text

INSTRUCTIONS = (
    "You are a research synthesis expert. You receive summaries from multiple sources "
    "(Gemini knowledge summaries and academic paper retrieval). Your job:\n"
    "1. Synthesize all findings into a coherent, well-structured report.\n"
    "2. Use only citation markers that appear in the provided sources, such as [Knowledge: model knowledge] or [Paper: document name].\n"
    "3. Organize with clear sections: Overview, Key Findings, Technical Details, Conclusion.\n"
    "4. Be honest about gaps - if no relevant paper source is provided, say that directly.\n"
    "5. Do not invent URLs, numbered references, footnotes, paper titles, or citations.\n"
    "6. Keep the report under 600 words unless the topic requires more depth."
)


def _citation_markers(text: str) -> list[str]:
    return re.findall(r"\[(?:Knowledge|Paper): [^\]]+\]", text)


async def write_report(query: str, combined_sources: str) -> str:
    prompt = f"""{INSTRUCTIONS}

Research query: {query}

Sources:
{combined_sources}
"""
    report = await generate_text(prompt)
    if not _citation_markers(report):
        available = list(dict.fromkeys(_citation_markers(combined_sources)))
        if available:
            report = f"{report.rstrip()}\n\nSource Markers\n" + "\n".join(f"- {item}" for item in available)
    return report
