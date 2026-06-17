import asyncio
import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from src_agents.env_loader import load_dotenv


load_dotenv()

DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
DEFAULT_OLLAMA_MODEL = "llama3.2:1b"
DEFAULT_HF_MODEL = "HuggingFaceTB/SmolLM2-1.7B-Instruct"
DEFAULT_LLM_PROVIDER = "gemini"
DEFAULT_ALLOW_LOCAL_FALLBACK = "0"
_warned_fallback = False
_provider_name = None


def _extract_after(prompt: str, marker: str) -> str:
    if marker not in prompt:
        return ""
    return prompt.split(marker, 1)[1].strip().splitlines()[0].strip()


def _topic_summary(query: str) -> str:
    q = query.lower()
    if "llma" in q or "llama" in q or "large language model" in q or re.search(r"\bllm\b", q):
        return (
            "If you meant LLM, it stands for Large Language Model: a neural network trained "
            "on large text/code corpora to predict and generate language. LLMs can summarize, "
            "answer questions, write code, classify text, and follow instructions, but they can "
            "also hallucinate or miss recent facts without tools or retrieval.\n\n"
            "If you meant LLaMA, it is Meta's family of open-weight large language models. "
            "LLaMA-style models can be run locally through tools such as Ollama, while Gemini "
            "is Google's hosted cloud model. Local models improve privacy and avoid cloud quotas; "
            "hosted models usually offer stronger quality and convenience. [Knowledge: local fallback]"
        )
    if (
        "speech recognition" in q
        or "speech regconition" in q
        or "automatic speech recognition" in q
        or " asr" in q
    ):
        return (
            "Speech recognition, also called Automatic Speech Recognition (ASR), is the "
            "process of converting spoken audio into written text. An ASR system takes an "
            "audio waveform, extracts acoustic features, predicts likely phonetic or token "
            "sequences, and decodes them into words.\n\n"
            "Modern speech recognition systems often use deep learning models such as CNNs, "
            "RNNs, transformers, conformers, or encoder-decoder architectures. They are used "
            "in voice assistants, transcription tools, call-center analytics, captions, dictation, "
            "and accessibility products. Key challenges include background noise, accents, speaker "
            "variation, domain-specific vocabulary, latency, and privacy. [Knowledge: local fallback]"
        )
    if "rag" in q or "retrieval" in q:
        return (
            "Retrieval-Augmented Generation (RAG) is a pattern for improving LLM answers by "
            "retrieving relevant external documents before generation. Instead of relying only "
            "on model parameters, the system embeds a user query, searches a vector database for "
            "similar chunks, and passes those chunks into the model as context.\n\n"
            "A typical RAG pipeline has four steps: ingest documents, split them into chunks, "
            "store embeddings in a vector database, then retrieve the most relevant chunks at "
            "question time. This helps reduce hallucination, keeps answers grounded in local or "
            "private data, and makes citations possible. The main tradeoffs are retrieval quality, "
            "chunking strategy, embedding model choice, latency, and how much context the generator "
            "can use effectively. [Knowledge: local fallback]"
        )
    if "chain-of-thought" in q or "cot" in q or "reasoning" in q:
        return (
            "Chain-of-thought prompting asks a language model to solve a problem through "
            "intermediate reasoning steps instead of jumping directly to the answer. It is useful "
            "for math, logic, planning, and multi-step analysis because it encourages decomposition "
            "and consistency checks.\n\n"
            "In production systems, developers often avoid exposing full hidden reasoning and "
            "instead ask for concise explanations, structured steps, or verifiable outputs. The "
            "benefit is better task performance; the risk is that generated reasoning can still be "
            "wrong, verbose, or misleading if not grounded by tools or retrieval. [Knowledge: local fallback]"
        )
    if "attention" in q or "transformer" in q:
        return (
            "Attention is the mechanism that lets a transformer decide which tokens are most "
            "relevant to each other. In self-attention, each token creates query, key, and value "
            "vectors; attention scores compare queries with keys, then use those scores to combine "
            "values into contextual representations.\n\n"
            "Multi-head attention runs this process several times in parallel so the model can "
            "capture different relationships, such as syntax, long-range dependencies, and semantic "
            "similarity. This is a core reason transformers work well for language modeling, retrieval, "
            "translation, and code tasks. [Knowledge: local fallback]"
        )
    if "rlhf" in q or "alignment" in q:
        return (
            "Reinforcement Learning from Human Feedback (RLHF) is a training process used to align "
            "language models with human preferences. A common setup trains a reward model from human "
            "rankings, then optimizes the language model to produce outputs that score well under that "
            "reward model.\n\n"
            "RLHF can make models more helpful and safer, but it can also introduce issues such as "
            "over-optimization, style bias, refusal mistakes, and dependence on the quality of human "
            "preference data. Modern systems often combine RLHF with supervised fine-tuning, safety "
            "data, evaluations, and tool grounding. [Knowledge: local fallback]"
        )
    return (
        f"{query} can be answered by identifying the core concept, explaining how it works, "
        "then discussing practical uses, limitations, and tradeoffs.\n\n"
        "In a research assistant pipeline, the planner decomposes the question, retrieval provides "
        "grounding from local documents, and the writer synthesizes the available context into a "
        "structured answer with citations. [Knowledge: local fallback]"
    )


def _topic_findings(query: str) -> list[str]:
    q = query.lower()
    if "llma" in q or "llama" in q or "large language model" in q or re.search(r"\bllm\b", q):
        return [
            "LLM means Large Language Model, a model trained to generate and transform text.",
            "LLaMA is Meta's open-weight LLM family; Ollama is a local runtime that can run models like LLaMA.",
            "Gemini is a hosted Google model, while local LLaMA-style models run on your machine with lower privacy risk but weaker hardware-dependent performance.",
        ]
    if (
        "speech recognition" in q
        or "speech regconition" in q
        or "automatic speech recognition" in q
        or " asr" in q
    ):
        return [
            "Speech recognition converts audio signals into text by modeling acoustic patterns and language structure.",
            "Modern ASR systems typically use neural encoders and decoders trained on large paired audio-text datasets.",
            "Accuracy depends on audio quality, accents, background noise, vocabulary coverage, and the target domain.",
        ]
    if "rag" in q or "retrieval" in q:
        return [
            "RAG combines retrieval and generation: retrieval finds relevant context, and generation turns that context into a natural-language answer.",
            "Vector databases such as ChromaDB are commonly used to store and search document embeddings for semantic similarity.",
            "RAG quality depends heavily on chunking, embedding quality, retrieval ranking, prompt construction, and citation handling.",
        ]
    if "chain-of-thought" in q or "cot" in q or "reasoning" in q:
        return [
            "Chain-of-thought improves multi-step task performance by encouraging decomposition before final answers.",
            "Reasoning traces are not automatically reliable, so production systems should pair them with evaluation, retrieval, or tools.",
            "Concise, structured reasoning is usually more useful for applications than exposing long hidden chains of thought.",
        ]
    if "attention" in q or "transformer" in q:
        return [
            "Self-attention lets each token condition on other tokens in the same sequence.",
            "Query-key similarity scores decide which value vectors contribute most to each token representation.",
            "Multi-head attention captures multiple relationship types in parallel, improving transformer expressiveness.",
        ]
    if "rlhf" in q or "alignment" in q:
        return [
            "RLHF uses human preference data to train reward models and improve model behavior.",
            "It can improve helpfulness and safety, but quality depends on the preference data and optimization process.",
            "Modern alignment pipelines usually combine RLHF with supervised tuning, evaluations, safety data, and policy constraints.",
        ]
    return [
        "The topic should be decomposed into definitions, mechanisms, applications, and limitations.",
        "A retrieval step can ground the answer in local documents instead of relying only on model knowledge.",
        "A synthesis step should make uncertainty and citation coverage explicit.",
    ]


def _topic_conclusion(query: str) -> str:
    q = query.lower()
    if "llma" in q or "llama" in q or "large language model" in q or re.search(r"\bllm\b", q):
        return (
            "For your project, Gemini is the cloud LLM provider, while Ollama can run local "
            "LLaMA-style models. Use Gemini for better answers; use local models when you want "
            "offline/private execution."
        )
    if (
        "speech recognition" in q
        or "speech regconition" in q
        or "automatic speech recognition" in q
        or " asr" in q
    ):
        return (
            "Speech recognition is a core speech AI technology for turning spoken language into "
            "usable text. Strong systems combine robust acoustic modeling, language modeling, "
            "domain adaptation, and careful evaluation on real audio conditions."
        )
    if "rag" in q or "retrieval" in q:
        return (
            "RAG is useful when an LLM must answer from private, changing, or source-grounded data. "
            "It does not guarantee correctness by itself, but it gives the model better evidence and "
            "makes the system easier to evaluate."
        )
    if "chain-of-thought" in q or "cot" in q or "reasoning" in q:
        return (
            "Reasoning prompts are most useful when paired with clear task structure and verification. "
            "They can improve answer quality, but they should not be treated as proof of correctness."
        )
    if "attention" in q or "transformer" in q:
        return (
            "Attention is central to transformers because it gives models a flexible way to build "
            "context-aware token representations across a sequence."
        )
    if "rlhf" in q or "alignment" in q:
        return (
            "RLHF is an important alignment technique, but it is best treated as one part of a broader "
            "model-quality and safety pipeline."
        )
    return (
        "The pipeline gives a structured answer from the available context and keeps citation coverage "
        "visible for review."
    )


_STOP_WORDS = {
    "about",
    "after",
    "again",
    "also",
    "from",
    "into",
    "local",
    "paper",
    "papers",
    "question",
    "research",
    "say",
    "says",
    "source",
    "that",
    "the",
    "this",
    "what",
    "when",
    "where",
    "which",
    "with",
}


def _query_terms(query: str) -> set[str]:
    return {
        word
        for word in re.findall(r"[a-z0-9]+", query.lower())
        if len(word) >= 3 and word not in _STOP_WORDS
    }


def _clean_source_text(text: str) -> str:
    text = re.sub(r"\[(?:Source|Paper|Web|Knowledge): [^\]]+\]", " ", text)
    text = re.sub(r"^(?:Web|Knowledge|Paper) Source \d+:\s*", " ", text, flags=re.MULTILINE)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _sentences(text: str) -> list[str]:
    cleaned = _clean_source_text(text)
    parts = re.split(r"(?<=[.!?])\s+", cleaned)
    return [
        part.strip()
        for part in parts
        if 35 <= len(part.strip()) <= 320
        and not part.strip().startswith("---")
    ]


def _select_source_sentences(query: str, text: str, limit: int = 4) -> list[str]:
    terms = _query_terms(query)
    scored = []
    for index, sentence in enumerate(_sentences(text)):
        words = set(re.findall(r"[a-z0-9]+", sentence.lower()))
        score = len(terms & words)
        if "hugging face" in query.lower() and "hugging face" in sentence.lower():
            score += 3
        if "provider" in query.lower() and "provider" in sentence.lower():
            score += 2
        scored.append((score, -index, sentence))

    relevant = [item for item in scored if item[0] > 0]
    if not relevant:
        relevant = scored[:limit]
    relevant.sort(reverse=True)

    selected = []
    seen = set()
    for _, _, sentence in relevant:
        key = sentence.lower()
        if key in seen:
            continue
        selected.append(sentence)
        seen.add(key)
        if len(selected) >= limit:
            break
    return selected


def _source_titles(sources: str) -> list[str]:
    titles = re.findall(r"\[Paper: ([^\]]+)\]", sources)
    titles += re.findall(r"\[Source: ([^\]]+)\]", sources)
    return list(dict.fromkeys(titles))


def _web_titles(sources: str) -> list[str]:
    return list(dict.fromkeys(re.findall(r"\[Web: ([^\]]+)\]", sources)))


def _section_text(sources: str, label: str) -> str:
    pattern = rf"{re.escape(label)} Source \d+:\s*(.*?)(?=\n\n===\n\n|$)"
    parts = re.findall(pattern, sources, flags=re.DOTALL)
    return "\n\n".join(part.strip() for part in parts if part.strip())


def _source_grounded_report(query: str, sources: str) -> str | None:
    paper_titles = _source_titles(sources)
    web_titles = _web_titles(sources)
    if not paper_titles and not web_titles:
        return None

    paper_text = _section_text(sources, "Paper")
    web_text = _section_text(sources, "Web")
    paper_selected = _select_source_sentences(query, paper_text or sources, limit=4)
    web_selected = _select_source_sentences(query, web_text, limit=3) if web_text else []
    if not paper_selected and not web_selected:
        return None

    paper_citation = f"[Paper: {paper_titles[0]}]" if paper_titles else ""
    web_citation = f"[Web: {web_titles[0]}]" if web_titles else ""
    overview_parts = []
    if paper_selected:
        overview_parts.append(f"Local RAG found: {' '.join(paper_selected[:2])} {paper_citation}")
    if web_selected:
        overview_parts.append(f"Web search found: {web_selected[0]} {web_citation}")

    findings = []
    for sentence in paper_selected[:3]:
        findings.append(f"- Local document: {sentence} {paper_citation}")
    for sentence in web_selected[:2]:
        findings.append(f"- Web result: {sentence} {web_citation}")

    technical_parts = []
    if paper_titles:
        technical_parts.append(
            f"Local ChromaDB returned '{paper_titles[0]}' as a matching document. {paper_citation}"
        )
    if web_titles:
        technical_parts.append(
            f"Web search returned live DuckDuckGo snippets, led by '{web_titles[0]}'. {web_citation}"
        )
    technical_parts.append(
        "The fallback writer used retrieved source text directly because the configured LLM provider was unavailable."
    )
    conclusion = (
        "So web search is part of the pipeline when enabled, but local-document questions should still be judged mainly from RAG sources."
    )

    return (
        "Overview\n"
        f"{' '.join(overview_parts)}\n\n"
        "Key Findings\n"
        f"{chr(10).join(findings)}\n\n"
        "Technical Details\n"
        f"{' '.join(technical_parts)}\n\n"
        "Conclusion\n"
        f"{conclusion}"
    )


def _report_for_query(query: str, sources: str) -> str:
    grounded = _source_grounded_report(query, sources)
    if grounded:
        return grounded

    summary = _topic_summary(query).replace(" [Knowledge: local fallback]", "")
    source_titles = _source_titles(sources)
    paper_citation = source_titles[0] if source_titles else "local ChromaDB"
    has_relevant_paper = (
        "No papers indexed yet" not in sources
        and "No relevant papers found" not in sources
        and bool(source_titles)
    )
    paper_note = (
        "No relevant local papers were available for this run, so the answer relies on the "
        "knowledge summary rather than document citations."
        if not has_relevant_paper
        else f"The local ChromaDB retrieval results were included from {paper_citation}."
    )
    technical_detail = (
        f"{paper_note} [Paper: {paper_citation}]"
        if has_relevant_paper
        else paper_note
    )
    findings = "\n".join(f"- {item}" for item in _topic_findings(query))
    return (
        "Overview\n"
        f"{summary}\n\n"
        "Key Findings\n"
        f"{findings} [Knowledge: local fallback]\n\n"
        "Technical Details\n"
        f"{technical_detail}\n\n"
        "Conclusion\n"
        f"{_topic_conclusion(query)}"
    )


def _offline_response(prompt: str, error: Exception | None = None) -> str:
    if "Return only valid JSON" in prompt:
        query = _extract_after(prompt, "User query:") or "the research question"
        return json.dumps(
            {
                "searches": [
                    {
                        "reason": "Build a high-level understanding of the topic.",
                        "query": query,
                        "source": "web",
                    },
                    {
                        "reason": "Check the local paper database for grounded excerpts.",
                        "query": query,
                        "source": "papers",
                    },
                ]
            }
        )

    if "Search term:" in prompt:
        query = _extract_after(prompt, "Search term:") or "the topic"
        return _topic_summary(query)

    if "Local paper excerpts:" in prompt:
        query = _extract_after(prompt, "Search query:") or "the topic"
        excerpts = prompt.split("Local paper excerpts:", 1)[1].strip()
        titles = _source_titles(excerpts)
        title = titles[0] if titles else "local document"
        selected = _select_source_sentences(query, excerpts, limit=4)
        if not selected:
            summary = _topic_summary(query).replace(" [Knowledge: local fallback]", "")
            return (
                f"{summary}\n\n"
                f"The retrieved local document '{title}' provides grounding for this answer. "
                f"[Paper: {title}]"
            )
        summary = " ".join(selected[:2])
        bullets = "\n".join(f"- {sentence} [Paper: {title}]" for sentence in selected)
        return (
            f"{summary} [Paper: {title}]\n\n"
            "Relevant local excerpts\n"
            f"{bullets}\n\n"
            "These excerpts came from the local ChromaDB retrieval step, not from model-only "
            "general knowledge. "
            f"[Paper: {title}]"
        )

    if "Sources:" in prompt:
        query_match = re.search(r"Research query:\s*(.+)", prompt)
        query = query_match.group(1).strip() if query_match else "the query"
        sources = prompt.split("Sources:", 1)[1].strip()
        return _report_for_query(query, sources)

    return (
        "Local fallback response: the external model provider was unavailable, but the "
        "pipeline continued in offline demo mode. [Knowledge: local fallback]"
    )


def _generate_ollama_sync(prompt: str) -> str:
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    model = os.getenv("OLLAMA_MODEL") or _detect_ollama_model(base_url)
    payload = json.dumps(
        {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2},
        }
    ).encode("utf-8")
    request = Request(
        f"{base_url}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=120) as response:
        data = json.loads(response.read().decode("utf-8"))
    text = data.get("response", "")
    if not text:
        raise RuntimeError("Ollama returned an empty response.")
    return text.strip()


def _detect_ollama_model(base_url: str) -> str:
    request = Request(f"{base_url}/api/tags", method="GET")
    with urlopen(request, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))
    models = data.get("models", [])
    if not models:
        return DEFAULT_OLLAMA_MODEL
    names = [item.get("name", "") for item in models]
    for preferred in (DEFAULT_OLLAMA_MODEL, "llama3.2:3b", "qwen2.5:7b"):
        if preferred in names:
            return preferred
    return names[0]


def _generate_gemini_sync(prompt: str) -> str:
    try:
        from google import genai
    except ImportError as exc:
        raise RuntimeError(
            "Missing google-genai. Install it with: "
            ".venv\\Scripts\\python.exe -m pip install google-genai"
        ) from exc

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY. Set it before running the agent.")

    client = genai.Client(api_key=api_key)
    model = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)
    response = client.models.generate_content(model=model, contents=prompt)
    text = getattr(response, "text", None)
    if not text:
        return ""
    return text.strip()


def _generate_huggingface_sync(prompt: str) -> str:
    model = os.getenv("HF_MODEL", DEFAULT_HF_MODEL).strip() or DEFAULT_HF_MODEL
    token = os.getenv("HF_API_TOKEN", "").strip()
    max_new_tokens = int(os.getenv("HF_MAX_NEW_TOKENS", "700"))
    temperature = float(os.getenv("HF_TEMPERATURE", "0.2"))

    payload = json.dumps(
        {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_new_tokens,
                "temperature": temperature,
                "return_full_text": False,
            },
            "options": {"wait_for_model": True},
        }
    ).encode("utf-8")

    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(
        f"https://api-inference.huggingface.co/models/{model}",
        data=payload,
        headers=headers,
        method="POST",
    )

    try:
        with urlopen(request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Hugging Face API error {exc.code}: {body}") from exc

    if isinstance(data, dict) and data.get("error"):
        raise RuntimeError(f"Hugging Face API error: {data['error']}")

    text = ""
    if isinstance(data, list) and data:
        first = data[0]
        if isinstance(first, dict):
            text = str(first.get("generated_text", ""))
    elif isinstance(data, dict):
        text = str(data.get("generated_text", ""))

    if not text.strip():
        raise RuntimeError(f"Hugging Face returned no generated text: {data!r}")
    return text.strip()


def _generate_sync(prompt: str) -> tuple[str, str]:
    errors = []
    provider = os.getenv("LLM_PROVIDER", DEFAULT_LLM_PROVIDER).strip().lower()

    if provider in {"gemini", "google"}:
        try:
            return "gemini", _generate_gemini_sync(prompt)
        except Exception as exc:
            errors.append(f"Gemini: {type(exc).__name__}: {exc}")

    elif provider == "ollama":
        try:
            return "ollama", _generate_ollama_sync(prompt)
        except Exception as exc:
            errors.append(f"Ollama: {type(exc).__name__}: {exc}")

    elif provider in {"huggingface", "hf"}:
        try:
            return "huggingface", _generate_huggingface_sync(prompt)
        except Exception as exc:
            errors.append(f"HuggingFace: {type(exc).__name__}: {exc}")

    elif provider == "auto":
        try:
            return "gemini", _generate_gemini_sync(prompt)
        except Exception as exc:
            errors.append(f"Gemini: {type(exc).__name__}: {exc}")

        try:
            return "huggingface", _generate_huggingface_sync(prompt)
        except Exception as exc:
            errors.append(f"HuggingFace: {type(exc).__name__}: {exc}")

        if os.getenv("DISABLE_OLLAMA") != "1":
            try:
                return "ollama", _generate_ollama_sync(prompt)
            except Exception as exc:
                errors.append(f"Ollama: {type(exc).__name__}: {exc}")

    else:
        errors.append(
            "Config: LLM_PROVIDER must be one of gemini, huggingface, ollama, or auto "
            f"(got {provider!r})"
        )

    raise RuntimeError("; ".join(errors))


async def generate_text(prompt: str) -> str:
    global _provider_name, _warned_fallback
    try:
        provider, text = await asyncio.to_thread(_generate_sync, prompt)
        if provider != _provider_name:
            print(f"[Provider] Using {provider}.")
            _provider_name = provider
        return text
    except Exception as exc:
        allow_fallback = os.getenv("ALLOW_LOCAL_FALLBACK", DEFAULT_ALLOW_LOCAL_FALLBACK).strip()
        if allow_fallback != "1":
            raise RuntimeError(
                "Configured LLM provider failed and ALLOW_LOCAL_FALLBACK is disabled. "
                f"Original error: {type(exc).__name__}: {exc}"
            ) from exc
        if not _warned_fallback:
            print(
                "[Provider] Configured LLM provider unavailable; using local fallback mode "
                f"({type(exc).__name__}: {exc})"
            )
            _warned_fallback = True
        return _offline_response(prompt, exc)
