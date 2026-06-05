"""
Simple eval suite — chạy 10 test queries, đo citation rate và relevance.
Usage: python -m research_agent_rag.eval
"""
import asyncio
import json
import time
from .manager import ResearchManager

TEST_QUERIES = [
    "What is chain-of-thought prompting and how does it improve LLM reasoning?",
    "How does RAG (Retrieval Augmented Generation) work?",
    "What are the main differences between GPT-4 and open-source LLMs?",
    "Explain attention mechanism in transformers",
    "What is RLHF and how is it used to align language models?",
]

async def run_eval():
    manager = ResearchManager()
    results = []

    for i, query in enumerate(TEST_QUERIES):
        print(f"\n[Eval {i+1}/{len(TEST_QUERIES)}] {query[:60]}...")
        start = time.time()
        try:
            result = await manager.run(query)
            latency = time.time() - start
            has_citation = "[Web:" in result.report or "[Paper:" in result.report
            results.append({
                "query": query,
                "latency_s": round(latency, 2),
                "has_citation": has_citation,
                "report_len": len(result.report),
                "num_sources": len(result.search_results),
                "status": "ok",
            })
            print(f"  -> {latency:.1f}s | citation={'YES' if has_citation else 'NO'} | {len(result.report)} chars")
        except Exception as e:
            results.append({"query": query, "status": "error", "error": str(e)})
            print(f"  -> ERROR: {e}")

    # Summary
    ok = [r for r in results if r["status"] == "ok"]
    citation_rate = sum(r["has_citation"] for r in ok) / len(ok) if ok else 0
    avg_latency = sum(r["latency_s"] for r in ok) / len(ok) if ok else 0

    print("\n" + "="*50)
    print("EVAL RESULTS")
    print("="*50)
    print(f"Queries run:    {len(results)}")
    print(f"Success rate:   {len(ok)}/{len(results)}")
    print(f"Citation rate:  {citation_rate*100:.0f}%")
    print(f"Avg latency:    {avg_latency:.1f}s")

    with open("eval_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed results saved to eval_results.json")

    return results


if __name__ == "__main__":
    asyncio.run(run_eval())
