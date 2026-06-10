import asyncio
import argparse
import os
import sys
import warnings
from pathlib import Path

warnings.filterwarnings(
    "ignore",
    message="urllib3 .* doesn't match a supported version.*",
    category=Warning,
)

from manager import ResearchManager
from src_agents.env_loader import load_dotenv
from src_agents.runtime_config import (
    format_status,
    set_fallback,
    set_model,
    set_provider,
    set_web,
)


load_dotenv()


def configure_stdio() -> None:
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name)
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def run_doctor() -> int:
    api_key = os.getenv("GEMINI_API_KEY", "")
    provider = os.getenv("LLM_PROVIDER", "gemini")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    hf_model = os.getenv("HF_MODEL", "HuggingFaceTB/SmolLM2-1.7B-Instruct")
    env_path = Path(__file__).resolve().parent / ".env"
    placeholder = api_key.strip() in {"", "your_gemini_api_key_here", "your_key_here"}

    print("Research Agent RAG doctor")
    print(f"- main file: {Path(__file__).resolve()}")
    print(f"- cwd: {Path.cwd().resolve()}")
    print(f"- .env: {env_path} ({'found' if env_path.exists() else 'missing'})")
    print(f"- LLM_PROVIDER: {provider}")
    print(f"- GEMINI_MODEL: {model}")
    print(f"- HF_MODEL: {hf_model}")
    print(f"- HF_API_TOKEN: {'present' if os.getenv('HF_API_TOKEN', '').strip() else 'missing'}")
    print(f"- DISABLE_OLLAMA: {os.getenv('DISABLE_OLLAMA', '')}")
    print(f"- ALLOW_LOCAL_FALLBACK: {os.getenv('ALLOW_LOCAL_FALLBACK', '0')}")
    print(f"- ENABLE_WEB_SEARCH: {os.getenv('ENABLE_WEB_SEARCH', '1')}")
    print(f"- WEB_SEARCH_PROVIDER: {os.getenv('WEB_SEARCH_PROVIDER', 'duckduckgo')}")
    print(f"- WEB_SEARCH_LIMIT: {os.getenv('WEB_SEARCH_LIMIT', '5')}")
    print(f"- GEMINI_API_KEY: {'missing/placeholder' if placeholder else 'present'}")

    if placeholder:
        print("  ERROR replace GEMINI_API_KEY in .env with your real Google AI Studio key.")
        return 1
    return 0
    

def print_banner() -> None:
    print("=== Research Agent RAG ===")
    provider = os.getenv("LLM_PROVIDER", "gemini")
    if provider.strip().lower() == "gemini":
        print("Provider pipeline: Web Search + Local RAG + Gemini 2.5 Flash -> Writer")
    elif provider.strip().lower() == "auto":
        print("Provider pipeline: Web Search + Local RAG + Gemini/Ollama -> Writer")
    else:
        print("Provider pipeline: Web Search + Local RAG + Ollama -> Writer")
    print(f"Configured LLM_PROVIDER={provider}. Use gemini for Gemini 2.5 Flash.\n")

    if not os.getenv("GEMINI_API_KEY"):
        if provider.strip().lower() == "auto":
            print("[Config] GEMINI_API_KEY not found. Ollama or local fallback will be used.")
        else:
            print("[Config] GEMINI_API_KEY not found. Local fallback will be used.")


async def run_once(manager: ResearchManager, query: str) -> None:
    if not query:
        query = "Recent advances in LLM reasoning and chain-of-thought prompting"
    try:
        await manager.run(query)
    except RuntimeError as exc:
        print("\n[Error] The configured LLM provider failed.")
        print(str(exc))
        print(
            "\nFix: check your Gemini API key/project, or set "
            "ALLOW_LOCAL_FALLBACK=1 in .env if you want offline demo answers."
        )


async def main(query_arg: str | None = None, chat: bool = False) -> None:
    print_banner()
    manager = ResearchManager()

    if chat:
        print("Chat mode. Type a research question, /help, or 'exit' to quit.\n")
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
            if query.startswith("/"):
                print(handle_command(query))
                print()
                continue

            await run_once(manager, query)
            print()
        return

    query = query_arg or input("What would you like to research? ").strip()
    await run_once(manager, query)


def handle_command(command: str) -> str:
    parts = command.strip().split(maxsplit=1)
    name = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""

    if name == "/help":
        return (
            "Commands:\n"
            "- /status\n"
            "- /provider gemini|ollama|auto\n"
            "- /provider huggingface\n"
            "- /model <model-name>\n"
            "- /fallback on|off\n"
            "- /web on|off\n"
            "- /help\n"
            "- exit"
        )
    if name == "/status":
        return format_status()
    if name == "/provider":
        return set_provider(arg)
    if name == "/model":
        return set_model(arg)
    if name == "/fallback":
        return set_fallback(arg)
    if name == "/web":
        return set_web(arg)
    return "Unknown command. Type /help."


if __name__ == "__main__":
    configure_stdio()
    parser = argparse.ArgumentParser(description="Run the Research Agent RAG pipeline")
    parser.add_argument("--query", "-q", help="Research question to run non-interactively")
    parser.add_argument("--chat", action="store_true", help="Run multiple questions in one session")
    parser.add_argument("--doctor", action="store_true", help="Show provider/key configuration and exit")
    args = parser.parse_args()
    if args.doctor:
        raise SystemExit(run_doctor())
    asyncio.run(main(args.query, args.chat))
