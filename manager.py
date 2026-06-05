import asyncio
from dataclasses import dataclass, field
from agents import Runner, trace

from .agents.planner_agent import planner_agent, ResearchPlan
from .agents.search_agent import search_agent
from .agents.rag_agent import rag_agent
from .agents.writer_agent import writer_agent


@dataclass
class ResearchResult:
    query: str
    plan: ResearchPlan
    search_results: list[str] = field(default_factory=list)
    report: str = ""


class ResearchManager:
    async def run(self, query: str) -> ResearchResult:
        print(f"\n[Planner] Breaking down query: '{query}'")
        plan_result = await Runner.run(planner_agent, query)
        plan: ResearchPlan = plan_result.final_output

        print(f"[Planner] Created {len(plan.searches)} search tasks:")
        for s in plan.searches:
            print(f"  [{s.source.upper()}] {s.query}")

        # Run web + paper searches in parallel
        web_tasks = [
            Runner.run(search_agent, s.query)
            for s in plan.searches if s.source == "web"
        ]
        paper_tasks = [
            Runner.run(rag_agent, s.query)
            for s in plan.searches if s.source == "papers"
        ]

        print(f"\n[Search] Running {len(web_tasks)} web + {len(paper_tasks)} paper searches in parallel...")
        all_results = await asyncio.gather(*web_tasks, *paper_tasks)
        search_results = [r.final_output for r in all_results]

        print(f"[Search] Done. Sending to writer...")

        combined = "\n\n===\n\n".join(
            f"Source {i+1}:\n{r}" for i, r in enumerate(search_results)
        )
        synthesis_prompt = f"Research query: {query}\n\nSources:\n{combined}"

        report_result = await Runner.run(writer_agent, synthesis_prompt)
        report = report_result.final_output

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
