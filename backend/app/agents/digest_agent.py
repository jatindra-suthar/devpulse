"""
DevPulse LangGraph Agent
------------------------
Graph:  prepare_context → analyse_activity → score_importance → generate_digest → done

Each node refines the understanding of what happened in the repo.
The importance scorer separates signal from noise before the final summary is written.
"""

import json
from typing import TypedDict, Annotated
import operator

from langgraph.graph import StateGraph, END
from langchain_ibm import WatsonxLLM
from langchain_core.prompts import PromptTemplate

from app.core.config import settings
from app.services.github_service import RepoActivity


# ── State ────────────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    activity: dict                          # serialised RepoActivity
    context_summary: str                    # human-readable activity context
    important_events: Annotated[list, operator.add]  # scored highlights
    digest: dict                            # final structured digest output


# ── LLM setup ────────────────────────────────────────────────────────────────

def get_llm() -> WatsonxLLM:
    return WatsonxLLM(
        model_id=settings.watsonx_model_id,
        url=settings.watsonx_url,
        project_id=settings.watsonx_project_id,
        apikey=settings.watsonx_api_key,
        params={
            "decoding_method": "greedy",
            "max_new_tokens": 1024,
            "temperature": 0.3,
            "repetition_penalty": 1.1,
        },
    )


# ── Node 1: prepare_context ───────────────────────────────────────────────────

def prepare_context(state: AgentState) -> AgentState:
    """Convert raw GitHub activity dict into a readable text block for the LLM."""
    a = state["activity"]

    lines = [
        f"Repository: {a['repo_full_name']}",
        f"Period: last {a['period_days']} days",
        f"",
        f"STATS",
        f"  Commits      : {a['total_commits']}",
        f"  PRs opened   : {a['total_prs_opened']}",
        f"  PRs merged   : {a['total_prs_merged']}",
        f"  Issues opened: {a['total_issues_opened']}",
        f"  Issues closed: {a['total_issues_closed']}",
        f"  Contributors : {', '.join(a['contributors']) or 'none'}",
        f"",
        f"RECENT COMMITS (latest 20)",
    ]
    for c in a["commits"][:20]:
        lines.append(f"  [{c['sha']}] {c['author']}: {c['message']}")

    lines.append("")
    lines.append("PULL REQUESTS")
    for pr in a["pull_requests"][:15]:
        merged = "merged" if pr["merged_at"] else pr["state"]
        lines.append(f"  #{pr['number']} [{merged}] {pr['title']} — @{pr['author']}")

    lines.append("")
    lines.append("ISSUES")
    for issue in a["issues"][:15]:
        lines.append(f"  #{issue['number']} [{issue['state']}] {issue['title']} — @{issue['author']}")

    state["context_summary"] = "\n".join(lines)
    return state


# ── Node 2: analyse_activity ──────────────────────────────────────────────────

ANALYSE_PROMPT = PromptTemplate.from_template("""
You are a senior engineering lead reviewing a week of activity on a software repository.

Below is the raw activity data:

{context}

Your task: identify the 3-5 most significant things that happened. Focus on:
- Major features or fixes merged
- PRs that have been open too long (stale)
- Sudden spikes or drops in activity
- Any blockers or repeated failure patterns

Write your analysis as a plain numbered list. Be specific — mention PR numbers, commit authors, or issue titles where relevant. Do not invent anything not in the data.

Analysis:
""")

def analyse_activity(state: AgentState) -> AgentState:
    llm = get_llm()
    chain = ANALYSE_PROMPT | llm
    result = chain.invoke({"context": state["context_summary"]})
    state["important_events"] = [result.strip()]
    return state


# ── Node 3: score_importance ──────────────────────────────────────────────────

SCORE_PROMPT = PromptTemplate.from_template("""
You are evaluating engineering activity for a team digest email.

Raw stats and events:
{context}

Initial analysis:
{analysis}

Now produce a JSON object with these exact keys:
{{
  "overall_health": "green | yellow | red",
  "health_reason": "one sentence explaining the health score",
  "highlights": ["bullet 1", "bullet 2", "bullet 3"],
  "stale_items": ["any PR or issue open > 5 days with no activity, or empty list"],
  "top_contributor": "username or null",
  "action_items": ["concrete next steps for the team, or empty list"]
}}

Rules:
- green = active, healthy progress
- yellow = some stale work or low activity  
- red = blocked, no merges, or many open issues piling up
- highlights must be specific (mention names/numbers)
- Return ONLY the JSON object, no other text.

JSON:
""")

def score_importance(state: AgentState) -> AgentState:
    llm = get_llm()
    chain = SCORE_PROMPT | llm
    result = chain.invoke({
        "context": state["context_summary"],
        "analysis": state["important_events"][0],
    })

    # Parse JSON safely
    try:
        raw = result.strip()
        # Strip any markdown code fences if model adds them
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        scored = json.loads(raw.strip())
    except (json.JSONDecodeError, IndexError):
        scored = {
            "overall_health": "yellow",
            "health_reason": "Could not parse scoring response.",
            "highlights": [state["important_events"][0]],
            "stale_items": [],
            "top_contributor": None,
            "action_items": [],
        }

    state["important_events"] = state["important_events"] + [json.dumps(scored)]
    return state


# ── Node 4: generate_digest ───────────────────────────────────────────────────

DIGEST_PROMPT = PromptTemplate.from_template("""
You are writing a concise engineering digest email for a software team.

Repository: {repo}
Period: last {period} days

Activity context:
{context}

Scored analysis (JSON):
{scored}

Write a short, friendly digest in plain English. Structure:
1. One opening sentence summarising the week's vibe (use the health score).
2. "What happened" — 3-4 bullet points of the most important events.
3. "Watch out" — stale items or blockers (skip this section if none).
4. "Up next" — action items for the team (skip if none).

Use plain text only. No markdown headers. No emoji. Keep the whole digest under 250 words.

Digest:
""")

def generate_digest(state: AgentState) -> AgentState:
    llm = get_llm()
    chain = DIGEST_PROMPT | llm

    scored_raw = state["important_events"][-1]
    try:
        scored = json.loads(scored_raw)
    except json.JSONDecodeError:
        scored = {}

    a = state["activity"]
    result = chain.invoke({
        "repo": a["repo_full_name"],
        "period": a["period_days"],
        "context": state["context_summary"],
        "scored": scored_raw,
    })

    state["digest"] = {
        "summary": result.strip(),
        "highlights": scored.get("highlights", []),
        "stale_items": scored.get("stale_items", []),
        "action_items": scored.get("action_items", []),
        "overall_health": scored.get("overall_health", "yellow"),
        "health_reason": scored.get("health_reason", ""),
        "top_contributor": scored.get("top_contributor"),
    }
    return state


# ── Build the graph ───────────────────────────────────────────────────────────

def build_digest_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("prepare_context", prepare_context)
    graph.add_node("analyse_activity", analyse_activity)
    graph.add_node("score_importance", score_importance)
    graph.add_node("generate_digest", generate_digest)

    graph.set_entry_point("prepare_context")
    graph.add_edge("prepare_context", "analyse_activity")
    graph.add_edge("analyse_activity", "score_importance")
    graph.add_edge("score_importance", "generate_digest")
    graph.add_edge("generate_digest", END)

    return graph.compile()


# ── Public interface ──────────────────────────────────────────────────────────

def run_digest_agent(activity: RepoActivity) -> dict:
    """Run the full LangGraph pipeline and return the digest dict."""
    import dataclasses

    def to_dict(obj):
        if dataclasses.is_dataclass(obj):
            return dataclasses.asdict(obj)
        return obj

    activity_dict = dataclasses.asdict(activity)

    graph = build_digest_graph()
    final_state = graph.invoke({
        "activity": activity_dict,
        "context_summary": "",
        "important_events": [],
        "digest": {},
    })

    return final_state["digest"]
