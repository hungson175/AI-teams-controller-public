# LLM Long-Context Prompt Adherence Research

**Date**: 2025-12-24
**Requested by**: PM (AI Controller Full Team)
**Researcher**: SA (Solution Architect)

---

## Executive Summary

This research investigates techniques for maintaining LLM instruction adherence in very long contexts (100k+ tokens). The core problem: **LLMs drift from their system prompts as context length increases**, with instruction-following degradation documented at 50%+ failure rates beyond 32k tokens.

**Key Finding**: The specific "Planar/Planta" GitHub project was not found, but comprehensive alternatives and techniques were discovered.

---

## Table of Contents

1. [The Problem: Instruction Drift](#the-problem-instruction-drift)
2. [GitHub Projects & Tools](#github-projects--tools)
3. [Techniques for Prompt Adherence](#techniques-for-prompt-adherence)
4. [Best Practices by Provider](#best-practices-by-provider)
5. [Production Patterns](#production-patterns)
6. [Actionable Recommendations](#actionable-recommendations)
7. [Sources](#sources)

---

## The Problem: Instruction Drift

### Quantified Degradation

Research from Databricks shows dramatic instruction-following degradation:

| Context Length | Failure Rate |
|----------------|--------------|
| 8k tokens | 5.2% |
| 16k tokens | 17.6% |
| 32k tokens | **50.4%** |

[Source: Databricks Long-Context RAG Research](https://www.databricks.com/blog/long-context-rag-performance-llms)

### Root Causes

1. **Training Data Gap**: LLMs lack instruction-following training data at longer context lengths
2. **Context Rot**: Token processing reliability degrades - the 10,000th token isn't handled as reliably as the 100th
3. **Attention Dilution**: Critical instructions get "lost" in vast amounts of context
4. **Natural Language Understanding Drift**: Even instruction-tuned models show NLU degradation as context grows

[Source: Context Rot Research - Chroma](https://research.trychroma.com/context-rot)
[Source: Natural Context Drift - arXiv](https://arxiv.org/html/2509.01093v1)

---

## GitHub Projects & Tools

### "Planar/Planta" Project Status

**NOT FOUND**: Extensive searching did not locate a GitHub project specifically named "Planar," "Planta," or similar variations addressing LLM prompt drift. The project may be:
- Very recent (not yet indexed)
- Named differently
- Part of unpublished research
- A private repository

### Closest Alternatives Found

#### 1. LongAlign (THUDM) - EMNLP 2024
- **GitHub**: [github.com/THUDM/LongAlign](https://github.com/THUDM/LongAlign)
- **Problem Solved**: LLMs lose instruction-following in long contexts (10k-100k tokens)
- **Solution**: First full recipe for LLM alignment on long context
- **Dataset**: LongAlign-10k (8k-64k length instructions)
- **Benchmark**: LongBench-Chat for evaluating instruction-following on 10k-100k queries

#### 2. Awesome-LLM-Long-Context-Modeling
- **GitHub**: [github.com/Xnhyacinth/Awesome-LLM-Long-Context-Modeling](https://github.com/Xnhyacinth/Awesome-LLM-Long-Context-Modeling)
- **Purpose**: Curated papers on long context modeling, prompt compression, attention mechanisms
- **Value**: Comprehensive research index

#### 3. Awesome-Context-Engineering
- **GitHub**: [github.com/Meirtz/Awesome-Context-Engineering](https://github.com/Meirtz/Awesome-Context-Engineering)
- **Purpose**: Production-grade context engineering survey
- **Content**: Hundreds of papers, frameworks, implementation guides

#### 4. Context-Engineering Handbook
- **GitHub**: [github.com/davidkimai/Context-Engineering](https://github.com/davidkimai/Context-Engineering)
- **Philosophy**: Based on Andrej Karpathy's principle: "Context engineering is the delicate art and science of filling the context window with just the right information for the next step"

### Prompt Optimization Frameworks

| Project | Maintainer | Key Feature |
|---------|------------|-------------|
| [PromptWizard](https://github.com/microsoft/PromptWizard) | Microsoft | Self-evolving prompt optimization |
| [Promptomatix](https://github.com/SalesforceAIResearch/promptomatix) | Salesforce | AI-driven prompt automation |
| [Promptimizer](https://github.com/hinthornw/promptimizer) | Community | Experimental optimization loop |

### Multi-Agent Frameworks with Memory

| Project | Stars | Key Feature for Adherence |
|---------|-------|---------------------------|
| [AutoGen](https://github.com/microsoft/autogen) | 110k+ | Multi-agent conversation persistence |
| [LangChain](https://github.com/langchain-ai/langchain) | 110k+ | Memory + SummarizationMiddleware |
| [Letta (MemGPT)](https://github.com/letta-ai/letta) | - | Long-term persistent memory |

### Monitoring & Drift Detection

- **[LLMBar](https://github.com/princeton-nlp/LLMBar)** (Princeton): Meta-evaluation benchmark for instruction-following (ICLR 2024)
- **[Scale AI Leaderboard](https://scale.com/leaderboard/instruction_following)**: 1,054 prompts assessing instruction execution
- **[SUPERWISE](https://superwise.ai/llm-monitoring/)**: Production monitoring for prompt drift

---

## Techniques for Prompt Adherence

### 1. Context Recalling Prompting

**The Most Impactful Technique Found**

Research from ∞Bench shows dramatic improvement by explicitly directing the model to repeat relevant information:

| Approach | Accuracy |
|----------|----------|
| Without repetition | 15.74% |
| With explicit recall | **39.59%** |

**Implementation**:
```
Before analyzing this code, first restate the relevant constraints and rules from the system prompt.
```

[Source: ∞Bench Research](https://arxiv.org/html/2402.13718v1)

### 2. Strategic Instruction Placement

#### Anthropic (Claude) Recommendation
> **Place critical instructions at the END of the prompt, after long documents.**

Claude performs significantly better when instructions come last in long contexts.

#### OpenAI (GPT-4.1+) Recommendation
> **Bookend instructions - place at BOTH beginning AND end for optimal performance.**

If only one placement is feasible, placing instructions *above* the context works better.

[Source: Anthropic Long Context Guide](https://www.anthropic.com/news/prompting-long-context)
[Source: OpenAI GPT-4.1 Cookbook](https://cookbook.openai.com/examples/gpt4-1_prompting_guide)

### 3. Reminder Injection Patterns

**Periodic Reinforcement**:
- Inject system reminders at strategic intervals (every N turns or tokens)
- Use explicit reinforcement messages restating critical constraints
- Place high-priority instructions near the end of context (recency bias)

**LangChain Guidance**:
> "Context persistence is about summarization + reinforcement, not just memory. Teach the model to 'remind itself' what's going on each turn."

[Source: LangChain Context Engineering](https://docs.langchain.com/oss/python/langchain/context-engineering)

### 4. Context Compaction (Summarization)

**When approaching context limits**:
1. Summarize earlier conversation parts
2. Keep recent messages intact
3. Prioritize most relevant chunks
4. Preserve: architectural decisions, unresolved bugs, critical implementation details

**Claude Code's Approach**:
- Pass message history to model for self-summarization
- Preserve 5 most recently accessed files + compressed history
- Enables "minimal performance degradation" while continuing long tasks

[Source: Anthropic Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

### 5. Structural Scaffolding

**XML Tags and Semantic Markers**:
```xml
<system_instructions>
  [Core behavioral rules - always enforced]
</system_instructions>

<context>
  [Background information]
</context>

<current_task>
  [What to do now]
</current_task>
```

**Checklists for Multi-Step Tasks**:
- Have model produce Markdown checklists
- Tick off items as it progresses
- Provides explicit state tracking

[Source: Claude 4 Best Practices](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices)

### 6. Plan-Then-Execute Pattern

**Security + Adherence Benefit**:
1. Constrain agent to formulate a fixed plan first
2. Then execute the plan
3. Even if tool calls interact with untrusted data, that data cannot inject instructions deviating from the plan

[Source: Design Patterns for Securing LLM Agents - arXiv](https://arxiv.org/html/2506.08837v2)

### 7. Token Compression

**GemFilter Research**:
- Achieves **1000× compression**
- Reduces input to 100 tokens while maintaining accuracy
- Filters most relevant tokens from early layers
- Significantly reduces running time and GPU memory

[Source: GemFilter Research](https://arxiv.org/html/2409.17422v1)

---

## Best Practices by Provider

### Anthropic (Claude)

1. **Place instructions at the END** of long prompts
2. **Use prompt caching** for stable system instructions (90% cost reduction, 85% latency reduction)
3. **Context will auto-compact** - inform model of this capability so it doesn't prematurely stop
4. **Use scratchpads/thinking blocks** before final instructions
5. **Clear context regularly** with `/clear` between tasks

[Source: Anthropic Prompt Caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)

### OpenAI (GPT-4.1+)

1. **Bookend instructions** - beginning AND end
2. **Be hyper-specific** - GPT-4.1 follows instructions more literally than predecessors
3. **Enforce explicit planning**: "You MUST plan extensively before each function call"
4. **Single sentence clarification** often sufficient when behavior differs from expectations

[Source: OpenAI GPT-4.1 Guide](https://cookbook.openai.com/examples/gpt4-1_prompting_guide)

### General (All Providers)

1. **Reduce ambiguity** through constraints
2. **Order matters** - test different arrangements
3. **Repeat critical requirements** - sometimes you need to double down
4. **Use analogies** and descriptive language to eliminate gray areas

[Source: Azure OpenAI Prompt Engineering](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/prompt-engineering)

---

## Production Patterns

### AI Coding Assistants (Cursor/Continue)

1. **Surgical Context with @ Symbols**:
   - Manually specify relevant context: `@src/components/Button.tsx`
   - Far more precise than letting AI guess

2. **Intent vs State Context**:
   - Intent: What you want (desired outcome)
   - State: Current world (error messages, console logs)
   - Provide both explicitly

3. **Composable Rules**:
   - Keep rule files under 500 lines
   - Apply rules at start of new dialogs (mid-conversation unreliable)
   - Keep code files under 500 lines for indexing

[Source: Cursor Context Management - Steve Kinney](https://stevekinney.com/courses/ai-development/cursor-context)

### Drift Detection (Production)

1. **Activation-Based Monitoring**:
   - Monitor LLM activations to detect off-track behavior
   - No fine-tuning required
   - Catches prompt injections, jailbreaks, malicious instructions

2. **DRIFT Framework** (2025):
   - Reduces Attack Success Rate from 51.7% to 1.5% on GPT-4o
   - System-level defense against prompt injection

[Source: Catching LLM Task Drift - arXiv](https://arxiv.org/html/2406.00799v2)
[Source: DRIFT Framework](https://medium.com/@tahirbalarabe2/how-drift-stops-prompt-injection-attacks-in-llm-agents-9454368f5e4c)

### Real-World Lessons (457 Case Studies)

1. **Input sanitization is critical** - Dropbox discovered prompt injection via control characters
2. **Treat prompt injection as architectural vulnerability**, not patchable bug
3. **Use appropriate models for specific tasks** - context drift minimized with right model for right task

[Source: LLMOps in Production - ZenML](https://www.zenml.io/blog/llmops-in-production-457-case-studies-of-what-actually-works)

---

## Actionable Recommendations

### Priority 1: Immediate Implementation

1. **Place critical instructions at END of long prompts** (Anthropic) or bookend them (OpenAI)
2. **Implement context recalling**: Direct model to restate constraints before acting
3. **Use explicit checklists** for multi-step tasks

### Priority 2: Architecture Changes

4. **Implement context compaction** before hitting limits - summarize while preserving critical details
5. **Apply plan-then-execute pattern** for agentic workflows
6. **Use XML/structural scaffolding** to create clear instruction boundaries

### Priority 3: Monitoring

7. **Monitor for drift proactively** - activation monitoring or output quality metrics
8. **Implement periodic instruction reinforcement** at strategic intervals
9. **Clear context regularly** between logical task boundaries

### For This Team Specifically

Given our multi-agent tmux architecture:

1. **WHITEBOARD as instruction reinforcement**: Already serves as periodic context refresh
2. **tm-send protocol**: Ensures structured message format (reduces ambiguity)
3. **Story branching**: Natural context isolation between stories
4. **Consider**: Adding explicit "restate your role and constraints" at story start

---

## Sources

### Official Documentation
1. [Anthropic - Prompting Long Context](https://www.anthropic.com/news/prompting-long-context)
2. [Anthropic - Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
3. [Anthropic - Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
4. [Anthropic - Prompt Caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)
5. [Claude 4 Best Practices](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices)
6. [OpenAI GPT-4.1 Prompting Guide](https://cookbook.openai.com/examples/gpt4-1_prompting_guide)
7. [Azure OpenAI Prompt Engineering](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/prompt-engineering)
8. [LangChain Context Engineering](https://docs.langchain.com/oss/python/langchain/context-engineering)

### Research Papers
9. [∞Bench - Context Recalling](https://arxiv.org/html/2402.13718v1)
10. [LongGenBench - Long Form Generation](https://arxiv.org/html/2409.02076)
11. [Natural Context Drift](https://arxiv.org/html/2509.01093v1)
12. [GemFilter - Token Compression](https://arxiv.org/html/2409.17422v1)
13. [Catching LLM Task Drift](https://arxiv.org/html/2406.00799v2)
14. [Design Patterns for Securing LLM Agents](https://arxiv.org/html/2506.08837v2)

### GitHub Projects
15. [THUDM/LongAlign](https://github.com/THUDM/LongAlign)
16. [Xnhyacinth/Awesome-LLM-Long-Context-Modeling](https://github.com/Xnhyacinth/Awesome-LLM-Long-Context-Modeling)
17. [Meirtz/Awesome-Context-Engineering](https://github.com/Meirtz/Awesome-Context-Engineering)
18. [davidkimai/Context-Engineering](https://github.com/davidkimai/Context-Engineering)
19. [microsoft/PromptWizard](https://github.com/microsoft/PromptWizard)
20. [SalesforceAIResearch/promptomatix](https://github.com/SalesforceAIResearch/promptomatix)
21. [microsoft/autogen](https://github.com/microsoft/autogen)
22. [langchain-ai/langchain](https://github.com/langchain-ai/langchain)
23. [princeton-nlp/LLMBar](https://github.com/princeton-nlp/LLMBar)
24. [dair-ai/Prompt-Engineering-Guide](https://github.com/dair-ai/Prompt-Engineering-Guide)
25. [jxzhangjhu/Awesome-LLM-Prompt-Optimization](https://github.com/jxzhangjhu/Awesome-LLM-Prompt-Optimization)

### Industry Articles
26. [Databricks - Long-Context RAG Performance](https://www.databricks.com/blog/long-context-rag-performance-llms)
27. [Chroma - Context Rot Research](https://research.trychroma.com/context-rot)
28. [DRIFT Framework - Medium](https://medium.com/@tahirbalarabe2/how-drift-stops-prompt-injection-attacks-in-llm-agents-9454368f5e4c)
29. [ZenML - LLMOps in Production (457 Case Studies)](https://www.zenml.io/blog/llmops-in-production-457-case-studies-of-what-actually-works)
30. [Cursor Context Management - Steve Kinney](https://stevekinney.com/courses/ai-development/cursor-context)
31. [Scale AI Instruction Following Leaderboard](https://scale.com/leaderboard/instruction_following)
32. [Analytics Vidhya - Context Engineering](https://www.analyticsvidhya.com/blog/2025/07/context-engineering/)
33. [Philipp Schmid - Context Engineering](https://www.philschmid.de/context-engineering)

---

## Appendix: Key Metrics

| Metric | Source | Finding |
|--------|--------|---------|
| Instruction failure at 32k | Databricks | 50.4% |
| Context recall improvement | ∞Bench | 15.74% → 39.59% |
| Prompt caching cost reduction | Anthropic | 90% |
| DRIFT attack prevention | Research | 51.7% → 1.5% ASR |
| GemFilter compression | Research | 1000× |
