# Evaluation Metrics for Research Agents

Research agents should be evaluated on more than whether the answer sounds good. Important metrics include answer correctness, source relevance, citation accuracy, retrieval recall, latency, cost, and failure transparency.

Retrieval recall measures whether the system retrieved the documents needed to answer the question. Citation accuracy checks whether cited sources actually support the claims. Faithfulness measures whether the final report stays within the provided evidence.

Latency matters because research pipelines often make multiple calls: planning, web search, RAG retrieval, reranking, writing, and verification. Cost matters when using paid model APIs or search services. A system that calls a cloud model three times per question can exhaust a small free quota quickly.

A useful evaluation set includes easy factual questions, ambiguous questions, questions with no answer in the local data, and questions requiring multiple sources. The expected behavior for missing evidence should be explicit: the agent should say it does not know instead of inventing an answer.
