# Web Search Grounding

Web search grounding connects a language model to current external information. Instead of relying only on model knowledge, the system searches the web, extracts titles, snippets, URLs, or page content, and provides those sources to the model.

Web search is useful for current events, product details, weather, release notes, documentation changes, market data, and anything likely to change after a model's training cutoff. It is less necessary for stable concepts such as basic algorithms or historical definitions.

Search snippets are not always enough for high-stakes answers. Snippets may be incomplete, outdated, or misleading. A stronger pipeline fetches the actual page content, extracts relevant passages, and cites the source URL. For lightweight demos, snippets plus URLs can still show the difference between model knowledge and external search.

A good research agent should distinguish source types. Web sources provide current external evidence. Local RAG sources provide private or curated documents. Model knowledge provides background explanation but should not be cited as external evidence.
