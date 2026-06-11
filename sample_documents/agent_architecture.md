# AI Agent Architecture

An AI agent is a system that uses a model to decide actions, call tools, observe results, and continue working toward a goal. A simple agent loop includes a user request, a planning step, tool selection, tool execution, observation, and final response generation.

Agents become more useful when they can use tools. Common tools include web search, file reading, database queries, code execution, calculators, calendar APIs, email APIs, and retrieval systems. Tools reduce the need for the model to guess and let it interact with current or private data.

A research agent can be structured as multiple specialized stages. A planner decomposes the question. A web search component gathers current external sources. A RAG component retrieves local documents. A writer synthesizes the evidence into a report. A verifier can check citations and flag unsupported claims.

Risks in agent systems include infinite loops, unsafe tool calls, prompt injection, leaking secrets, unreliable citations, and excessive API usage. Practical systems should include tool allowlists, path restrictions, rate limits, logging, and clear failure messages.
