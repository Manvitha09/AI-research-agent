# import os
# import json
# import time
# from groq import Groq
# from dotenv import load_dotenv
# from tools import search_web
# from rich.console import Console

# load_dotenv()
# console = Console()


# def init_model():
#     api_key = os.getenv("GROQ_API_KEY")
#     if not api_key:
#         raise ValueError("GROQ_API_KEY not set in .env file")
#     return Groq(api_key=api_key)


# def call_model(client, prompt: str) -> str:
#     """Send a prompt to Groq and return the response text."""
#     response = client.chat.completions.create(
#         model="llama-3.3-70b-versatile",
#         messages=[{"role": "user", "content": prompt}],
#         max_tokens=1000,
#     )
#     return response.choices[0].message.content.strip()


# def generate_sub_questions(client, topic: str) -> list[str]:
#     """Break the topic into focused research sub-questions."""
#     prompt = f"""You are a research planner. A user wants to research: "{topic}"

# Break this into 3-4 specific sub-questions that together would give a comprehensive understanding of the topic.

# Respond ONLY with a JSON array of strings. Example:
# ["What is X?", "How does Y work?", "What are the latest trends in Z?"]"""

#     console.print(f"\n[bold cyan]🧠 Planning research for:[/bold cyan] {topic}")
#     text = call_model(client, prompt)

#     # Strip markdown code fences if present
#     if text.startswith("```"):
#         text = text.split("```")[1]
#         if text.startswith("json"):
#             text = text[4:]
#     text = text.strip()

#     questions = json.loads(text)
#     return questions


# def research_question(client, question: str) -> dict:
#     """Search the web for a question, then summarize findings."""
#     console.print(f"\n[bold yellow]🔍 Researching:[/bold yellow] {question}")

#     # Step 1: Web search
#     results = search_web(question, max_results=4)
#     if not results:
#         return {"question": question, "summary": "No results found.", "sources": []}

#     # Format search results for the model
#     search_context = ""
#     for i, r in enumerate(results, 1):
#         search_context += f"\n[Source {i}] {r['title']}\nURL: {r['url']}\n{r['content']}\n"

#     console.print(f"  [green]✓ Found {len(results)} sources[/green]")

#     # Step 2: Summarize with Groq
#     prompt = f"""You are a research assistant. Based on the web search results below, write a concise, factual summary (3-5 sentences) answering this question:

# Question: {question}

# Search Results:
# {search_context}

# Write only the summary. Be factual and cite which sources support key claims using [Source N] notation."""

#     summary = call_model(client, prompt)

#     return {
#         "question": question,
#         "summary": summary,
#         "sources": [{"title": r["title"], "url": r["url"]} for r in results],
#     }


# def synthesize_report(client, topic: str, findings: list[dict]) -> str:
#     """Combine all findings into a final structured report."""
#     console.print(f"\n[bold magenta]📝 Synthesizing final report...[/bold magenta]")

#     findings_text = ""
#     for f in findings:
#         findings_text += f"\n## Sub-question: {f['question']}\n{f['summary']}\n"

#     prompt = f"""You are a professional research writer. Synthesize the following research findings into a well-structured report on: "{topic}"

# Research Findings:
# {findings_text}

# Write a report with these sections:
# 1. **Executive Summary** (2-3 sentences overview)
# 2. **Key Findings** (bullet points of the most important insights)
# 3. **Detailed Analysis** (a few paragraphs expanding on the findings)
# 4. **Conclusion** (what this all means / what to watch for)

# Use markdown formatting."""

#     return call_model(client, prompt)


# def run_agent(topic: str) -> str:
#     """Main agent loop: plan → search → synthesize → report."""
#     client = init_model()

#     # Phase 1: Plan
#     # In agent.py, inside run_agent()
#     # if " vs " in topic.lower() or "compare" in topic.lower():
#     #     questions = generate_comparison_questions(client, topic)
#     questions = generate_sub_questions(client, topic)
#     console.print(f"[dim]Sub-questions: {questions}[/dim]")

#     # Phase 2: Research each question (with delay to avoid rate limits)
#     findings = []
#     for q in questions:
#         result = research_question(client, q)
#         findings.append(result)
#         time.sleep(2)

#     # Phase 3: Synthesize
#     report = synthesize_report(client, topic, findings)

#     return report

import os
import re
import json
import time
from groq import Groq
from dotenv import load_dotenv
from tools import search_web
from rich.console import Console

load_dotenv()
console = Console()


def init_model():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set in .env file")
    return Groq(api_key=api_key)


def call_model(client, prompt: str) -> str:
    """Send a prompt to Groq and return the response text."""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
    )
    return response.choices[0].message.content.strip()


def parse_json_array(text: str) -> list[str]:
    """
    Robustly extract a JSON array from model output.
    Handles markdown fences, extra text, and smart quotes.
    Falls back to regex extraction if JSON parsing fails.
    """
    # Remove markdown code fences
    if "```" in text:
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.startswith("json"):
            text = text[4:]

    # Replace smart/curly quotes with straight quotes
    text = (text
        .replace("\u201c", '"').replace("\u201d", '"')
        .replace("\u2018", "'").replace("\u2019", "'"))

    # Extract just the JSON array, ignoring surrounding text
    start = text.find("[")
    end = text.rfind("]") + 1
    if start != -1 and end > start:
        text = text[start:end]

    text = text.strip()

    try:
        result = json.loads(text)
        if isinstance(result, list):
            return result
    except json.JSONDecodeError:
        pass

    # Last resort: extract quoted strings with regex
    matches = re.findall(r'"([^"]{10,})"', text)
    if matches:
        return matches

    raise ValueError(f"Could not parse JSON array from model output:\n{text}")


def generate_sub_questions(client, topic: str) -> list[str]:
    """Break the topic into focused research sub-questions."""
    prompt = f"""You are a research planner. A user wants to research: "{topic}"

Break this into 3-4 specific sub-questions. Each question must:
- Be answerable with concrete facts, numbers, or examples
- Target a DIFFERENT aspect of the topic (no overlap between questions)
- Avoid vague questions like "what are their values" — ask for specific evidence instead

Respond ONLY with a JSON array of strings, nothing else. No explanation, no markdown."""

    console.print(f"\n[bold cyan]🧠 Planning research for:[/bold cyan] {topic}")
    text = call_model(client, prompt)
    return parse_json_array(text)


def generate_comparison_questions(client, topic: str) -> list[str]:
    """Generate structured comparison-focused sub-questions."""
    prompt = f"""You are a research planner. A developer wants to compare: "{topic}"

Generate 4 specific sub-questions that together give a thorough technical comparison.
Focus on: performance, use cases, community/ecosystem, and tradeoffs.

Respond ONLY with a JSON array of strings, nothing else. No explanation, no markdown.
Example: ["What are the performance benchmarks of X vs Y?", "What are the ideal use cases for X vs Y?"]"""

    console.print(f"\n[bold cyan]⚖️  Planning comparison for:[/bold cyan] {topic}")
    text = call_model(client, prompt)
    return parse_json_array(text)


def research_question(client, question: str) -> dict:
    """Search the web for a question, then summarize findings."""
    console.print(f"\n[bold yellow]🔍 Researching:[/bold yellow] {question}")

    results = search_web(question, max_results=4)
    if not results:
        return {"question": question, "summary": "No results found.", "sources": []}

    search_context = ""
    for i, r in enumerate(results, 1):
        search_context += f"\n[Source {i}] {r['title']}\nURL: {r['url']}\n{r['content']}\n"

    console.print(f"  [green]✓ Found {len(results)} sources[/green]")

    prompt = f"""You are a research assistant. Based on the web search results below, write a concise, factual summary (3-5 sentences) answering this question:

Question: {question}

Search Results:
{search_context}

Write only the summary. Be factual and cite which sources support key claims using [Source N] notation."""

    summary = call_model(client, prompt)

    return {
        "question": question,
        "summary": summary,
        "sources": [{"title": r["title"], "url": r["url"]} for r in results],
    }


def synthesize_report(client, topic: str, findings: list[dict], is_comparison: bool = False) -> str:
    """Combine all findings into a final structured report."""
    console.print(f"\n[bold magenta]📝 Synthesizing final report...[/bold magenta]")

    # Build findings text first
    findings_text = ""
    for f in findings:
        findings_text += f"\n## Sub-question: {f['question']}\n{f['summary']}\n"

    # Choose format based on mode
    if is_comparison:
        format_instruction = """Write a comparison report with these sections:
## Overview
## Head-to-Head Comparison
(include a markdown table with rows like Performance, Use Case, Learning Curve, Community, Cost)
## When to Choose X
## When to Choose Y
## Verdict"""
    else:
        format_instruction = """Write a report with these sections:
## Executive Summary
## Key Findings
## Detailed Analysis
## Conclusion"""

    prompt = f"""You are a senior technical writer specializing in software engineering.
Synthesize the following research findings on: "{topic}"

Research Findings:
{findings_text}

{format_instruction}

Rules:
- You MUST use ## markdown headings for every section exactly as shown above
- NEVER repeat the same fact, sentence, or idea across sections — each section must add NEW information
- Executive Summary: high-level overview only, no details
- Key Findings: bullet points of specific facts, numbers, and data points not mentioned in summary
- Detailed Analysis: deeper context and explanation, no restatement of findings
- Conclusion: forward-looking only — implications, predictions, what to watch — not a recap
- Always include specific numbers, benchmarks, or data points where available
- Minimum 300 words total but NO filler or padding"""

    return call_model(client, prompt)


def run_agent(topic: str) -> str:
    """Main agent loop: plan → search → synthesize → report."""
    client = init_model()

    # Phase 1: Plan
    is_comparison = " vs " in topic.lower() or "compare" in topic.lower()
    if is_comparison:
        questions = generate_comparison_questions(client, topic)
    else:
        questions = generate_sub_questions(client, topic)
    console.print(f"[dim]Sub-questions: {questions}[/dim]")

    # Phase 2: Research each question
    findings = []
    for q in questions:
        result = research_question(client, q)
        findings.append(result)
        time.sleep(2)

    # Phase 3: Synthesize (small pause to avoid token rate limits)
    time.sleep(10)
    report = synthesize_report(client, topic, findings, is_comparison=is_comparison)

    return report