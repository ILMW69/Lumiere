import re
from langchain_openai import ChatOpenAI
from config.settings import LLM_MODEL

# Initialize ChatOpenAI client at module load
llm = ChatOpenAI(
    model=LLM_MODEL,
)

CRITIC_PROMPT = """
You are a critic agent evaluating an AI-generated answer.

Your task:
Decide whether the answer is fully supported by the provided context.

Rules:
- If the answer is clearly supported by the context → ACCEPT
- If the answer adds information not present in the context → RETRY
- If the context is insufficient to answer the question → REJECT

Respond with ONLY one word:
ACCEPT, RETRY, or REJECT

Context:
{context}

Question:
{question}

Answer:
{answer}

Decision:
"""

def _extract_memory_signal(text: str) -> dict | None:
    """
    Extract a session-level memory signal from raw user input.
    Rule-based, conservative, but robust.
    """
    if not text:
        return None

    normalized = (
        text.replace("’", "'")
            .replace("‘", "'")
            .lower()
            .strip()
    )

    # Explicit self-declaration patterns
    goal_patterns = [
        r"\bi am\b",
        r"\bi'm\b",
        r"\bi am building\b",
        r"\bi'm building\b",
        r"\bi am working on\b",
        r"\bi'm working on\b",
    ]

    preference_patterns = [
        r"\bi prefer\b",
        r"\bi like\b",
        r"\bi don't like\b",
        r"\bi do not like\b",
    ]

    if any(re.search(p, normalized) for p in goal_patterns):
        return {
            "type": "goal",
            "content": text.strip(),
        }

    if any(re.search(p, normalized) for p in preference_patterns):
        return {
            "type": "preference",
            "content": text.strip(),
        }

    return None

def critic_agent(
        question: str,
        retrieved_docs: list[dict],
        answer: str,
        reasoning_mode: str | None = None,
        user_input: str | None = None,
    ) -> dict:
    result = {
        "decision": None,
        "memory_signal": None,
    }
    # Allow general (non-RAG) answers explicitly
    if reasoning_mode == "general":
        result["decision"] = "ACCEPT"
        return result

    # Grounded mode requires retrieved context
    if not retrieved_docs:
        result["decision"] = "REJECT"
        return result
    
    context_blocks = []
    for d in retrieved_docs:
        source = f"[{d['doc_id']}:{d['chunk_index']}]"
        context_blocks.append(f"{d['text']}\nSource: {source}")

    context = "\n\n".join(context_blocks)
    response = llm.invoke(
        CRITIC_PROMPT.format(
            context=context,
            question=question,
            answer=answer
        )
    )

    decision = response.content.strip().upper()

    if decision not in {"ACCEPT", "RETRY", "REJECT"}:
        result["decision"] = "REJECT"
        return result
    
    result["decision"] = decision

    if decision == "ACCEPT":
        source_text = user_input or question
        memory_signal = _extract_memory_signal(source_text)
        result["memory_signal"] = memory_signal

    return result