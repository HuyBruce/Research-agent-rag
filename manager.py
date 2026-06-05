import asyncio
from dataclasses import dataclass, field

from src_agents.planner_agent import ResearchPlan, plan_research
from src_agents.search_agent import run_search
from src_agents.rag_agent import run_rag
from src_agents.writer_agent import write_report


@dataclass
class ResearchResult:
    query: str
    plan: ResearchPlan
    search_results: list[str] = field(default_factory=list)
    report: str = ""


class ResearchManager:
    async def run(self, query: str) -> ResearchResult:
        print(f"\n[Planner] Breaking down query: '{query}'")
        plan = await plan_research(query)

        print(f"[Planner] Created {len(plan.searches)} search tasks:")
        for s in plan.searches:
            label = "KNOWLEDGE" if s.source == "web" else s.source.upper()
            print(f"  [{label}] {s.query}")

        # Run knowledge and paper retrieval tasks in parallel.
        web_tasks = [
            run_search(s.query)
            for s in plan.searches if s.source == "web"
        ]
        paper_tasks = [
            run_rag(s.query)
            for s in plan.searches if s.source == "papers"
        ]

        print(
            f"\n[Search] Running {len(web_tasks)} knowledge + "
            f"{len(paper_tasks)} paper searches in parallel..."
        )
        all_results = await asyncio.gather(*web_tasks, *paper_tasks)
        search_results = list(all_results)

        print(f"[Search] Done. Sending to writer...")

        labels = [
            "Knowledge Source" for s in plan.searches if s.source == "web"
        ] + [
            "Paper Source" for s in plan.searches if s.source == "papers"
        ]
        combined = "\n\n===\n\n".join(
            f"{labels[i] if i < len(labels) else 'Source'} {i+1}:\n{r}"
            for i, r in enumerate(search_results)
        )
        report = await write_report(query, combined)

        print("\n" + "="*60)
        print("RESEARCH REPORT")
        print("="*60)
        print(report)

        return ResearchResult(
            query=query,
            plan=plan,
            search_results=search_results,
            report=report,
        )
