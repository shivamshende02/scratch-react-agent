# Scratch-Built ReAct (Reasoning + Acting) Agent

This repository contains a first-principles implementation of the **ReAct (Reasoning and Acting)** paradigm for large language models, based on the paper *ReAct: Synergizing Reasoning and Acting in Language Models (Yao et al., ICLR 2023)*.

Unlike complex orchestration frameworks like LangChain, this project is built completely from scratch in pure Python using the official Mistral AI SDK. This minimal implementation is designed for educational purposes to demonstrate how autonomous LLM loops, state management, and tool-use mechanics work "under the hood."

## 🧩 Overview

The ReAct paradigm enables a Large Language Model (LLM) to solve multi-step problems by interleaving verbal reasoning ("Thoughts") with actions ("Actions")[cite: 3].

1.  **Reason:** The model analyzes the current situation to create a plan[cite: 3].
2.  **Act:** The model interacts with external tools to gather facts[cite: 3].
3.  **Observe:** The model receives grounded feedback from the real world[cite: 3, 4].

This process repeats until the model has enough information to arrive at a final grounded answer.

## 🧱 Project Structure

*   `src/agent.py`: The core execution engine. Handles the LLM interaction loop, stops generation to intercept tool calls, and orchestrates the state flow[cite: 3].
*   `src/tools.py`: The environment interface. Contains the live Wikipedia API wrapper and dispatcher logic.
*   `src/prompt.py`: The few-shot ReAct prompt template that teaches the model the required input/output syntax[cite: 3].
*   `.env`: (Hidden) File containing your API keys.

## 🏗️ Creative Architecture

The diagram below visualizes the **closed-loop feedback system** implemented in this repository. It shows how internal cognitive strategy is married to external factual grounding through a rigid `Thought` $\rightarrow$ `Action` $\rightarrow$ `Observation` pipeline.

### 🎨 The Dual-Space ReAct Engine

```text
 ┌────────────────────────────────────────────────────────────────────────┐
 |                        🧠 INTERNAL COGNITIVE SPACE                     |
 |                                                                        |
 |   [ User Prompt & Few-Shot Demonstrations ]                            |
 |                        │                                               |
 |                        ▼                                               |
 |   ┌───────────────────────────────────────────────────────────────┐    |
 |   │                      Mistral LLM Engine                       │    |
 |   │                                                               │    |
 |   │   1. Context Absorption    ► Reads accumulated history        │    |
 |   │   2. Verbal Reasoning      ► Generates `Thought: ...`         │    |
 |   │   3. Tool Selection        ► Generates `Action: tool[...]`    │    |
 |   └──────────────────────────────┬────────────────────────────────┘    |
 |                                  │                                     |
 |                        [ Stop Token Intercept ]                        |
 |                        (Halt generation at "Observation:")             |
 └──────────────────────────────────┼─────────────────────────────────────┘
                                    │
                                    ▼ (Extracted Payload)
 ┌──────────────────────────────────┼─────────────────────────────────────┐
 |                       🌍 EXTERNAL ACTION SPACE                         |
 |                                  │                                     |
 |                                  ▼                                     |
 |   ┌───────────────────────────────────────────────────────────────┐    |
 |   │                   Python Execution Dispatch                   │    |
 |   │                                                               │    |
 |   │   • Regex Parser           ► Splits Tool Name & Argument      │    |
 |   │   • Tool Router            ► Directs to `search` or `lookup`  │    |
 |   └──────────────────────────────┬────────────────────────────────┘    |
 |                                  │                                     |
 |                    ┌─────────────┴─────────────┐                       |
 |                    ▼                           ▼                       |
 |         [ wikipedia_search() ]      [ wikipedia_lookup() ]             |
 |                    │                           │                       |
 |                    └─────────────<─────────────┘                       |
 |                                  │                                     |
 |                                  ▼                                     |
 |         ┌────────────────────────────────────────────────┐             |
 |         │           Live MediaWiki API Gateway           │             |
 |         │  • Fetches Article Summaries                   │             |
 |         │  • Fallback Entity Suggestions                 │             |