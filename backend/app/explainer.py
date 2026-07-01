"""
Explanation / conversational layer.

Design choice: this works out of the box with NO API key, using a
template-based explainer built from the analysis JSON. If OPENAI_API_KEY
(or GEMINI_API_KEY) is set in the environment, it upgrades to a real LLM
call that is *grounded* in the same analysis JSON -- i.e. the LLM is given
the circuit's real stats/patterns as context rather than asked to guess
from source code alone, which cuts down on hallucinated gate math.

Swapping in LangChain/LangGraph (as in the original proposal) mainly buys
you: multi-turn memory, tool-calling (e.g. letting the LLM call
`/api/simulate` itself for a modified circuit), and provider-agnostic
routing. None of that changes this module's job -- it would still be the
thing that assembles the grounding context. Kept as plain httpx calls here
so the scaffold has zero required framework dependencies.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import httpx

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def _template_explanation(analysis: Dict[str, Any], question: Optional[str] = None) -> str:
    lines: List[str] = []
    n = analysis["num_qubits"]
    lines.append(f"This circuit uses {n} qubit(s), has depth {analysis['depth']}, "
                 f"and applies {analysis['total_gates']} gate(s): "
                 + ", ".join(f"{v}x {k}" for k, v in analysis["gate_counts"].items() if k not in ("barrier", "measure")) + ".")

    if analysis["entangled"]:
        entangled_qubits = [q for q, e in analysis["entanglement_entropy_per_qubit"].items() if e > 1e-6]
        lines.append(f"Qubit(s) {', '.join(entangled_qubits)} are entangled with the rest of the "
                     "register -- measuring one instantly constrains what you'd measure on the others, "
                     "with no classical local-hidden-variable explanation (Bell's theorem).")
    else:
        lines.append("No entanglement was detected: every qubit's state can be described independently "
                     "of the others (a product state).")

    if analysis["detected_patterns"]:
        for p in analysis["detected_patterns"]:
            lines.append(f"Pattern match: {p['name']} (confidence {p['confidence']:.0%}) -- {p['detail']}")
    else:
        lines.append("No well-known named algorithm pattern was recognized in this circuit.")

    if analysis["optimization_hints"]:
        lines.append("Optimization notes: " + " ".join(analysis["optimization_hints"]))

    if question:
        lines.append(
            f"\n(Note: a template explainer answered this -- no LLM API key is configured, so "
            f"your specific question \"{question}\" couldn't be directly addressed. Set "
            "OPENAI_API_KEY or GEMINI_API_KEY in the backend .env to enable free-form Q&A.)"
        )
    return "\n\n".join(lines)


async def _call_openai(system_prompt: str, user_prompt: str) -> str:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.3,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


async def _call_gemini(system_prompt: str, user_prompt: str) -> str:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}",
            json={
                "contents": [{"parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]}],
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]


SYSTEM_PROMPT = (
    "You are a quantum computing tutor embedded in a circuit-analysis tool. "
    "You are given a JSON summary of a real, already-executed circuit "
    "(gate counts, statevector-derived entanglement, detected algorithm "
    "patterns, optimization hints). Ground every claim in that JSON -- do "
    "not invent gates, qubit counts, or probabilities that aren't in it. "
    "Explain clearly for someone learning quantum computing, include the "
    "relevant math (bra-ket notation is fine) where it helps, and keep the "
    "answer focused and not overly long."
)


async def explain_circuit(analysis: Dict[str, Any], question: Optional[str] = None) -> Dict[str, str]:
    if not (OPENAI_API_KEY or GEMINI_API_KEY):
        return {"explanation": _template_explanation(analysis, question), "source": "template"}

    user_prompt = f"Circuit analysis JSON:\n{analysis}\n\n"
    user_prompt += f"User question: {question}" if question else "Give a general explanation of this circuit."

    try:
        text = await (_call_openai(SYSTEM_PROMPT, user_prompt) if OPENAI_API_KEY
                      else _call_gemini(SYSTEM_PROMPT, user_prompt))
        return {"explanation": text, "source": "llm"}
    except Exception as e:  # noqa: BLE001 - never let a flaky LLM call break the tutor
        fallback = _template_explanation(analysis, question)
        return {"explanation": f"{fallback}\n\n[LLM call failed, showing template explanation: {e}]",
                "source": "template"}


async def chat_reply(messages: List[Dict[str, str]], analysis: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
    last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
    if not (OPENAI_API_KEY or GEMINI_API_KEY):
        context = f" (circuit context: {analysis['detected_patterns']})" if analysis else ""
        return {
            "reply": "I'm running in template mode (no LLM API key configured), so I can't hold a "
                     f"free-form conversation yet{context}. Set OPENAI_API_KEY or GEMINI_API_KEY in "
                     "the backend .env to enable the full conversational tutor.",
            "source": "template",
        }

    context_note = f"\n\nCurrent circuit analysis JSON (ground answers in this if relevant): {analysis}" if analysis else ""
    convo = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in messages)
    try:
        text = await (_call_openai(SYSTEM_PROMPT + context_note, convo) if OPENAI_API_KEY
                      else _call_gemini(SYSTEM_PROMPT + context_note, convo))
        return {"reply": text, "source": "llm"}
    except Exception as e:  # noqa: BLE001
        return {"reply": f"LLM call failed: {e}", "source": "template"}
