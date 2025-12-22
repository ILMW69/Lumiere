from memory.session_memory import get_session_memory
from observability.langfuse_client import langfuse
from langchain_openai import ChatOpenAI
from config.settings import LLM_MODEL

llm = ChatOpenAI(
    model=LLM_MODEL,
    temperature=0,
)

REASONING_PROMPT = """
You are a reasoning agent in an AI knowledge workspace.

CRITICAL INSTRUCTION: Read the conversation history carefully. If the user uses words like "that", "it", "this", or "the topic", they are referring to something mentioned in the conversation history above.

For example:
- If conversation shows "User: What is RAG?" and then "User: simplify that"
- "that" means RAG
- You should simplify the explanation of RAG using ONLY the provided context

If the user asks to "simplify that" or "explain it more simply":
1. Look at the conversation history
2. Find what topic was just discussed
3. Answer about THAT topic in a simpler way using the retrieved context

Do NOT ask the user to clarify what they mean if it's obvious from the conversation history.

You MUST answer the question using ONLY the provided context below.
If the context does not contain enough information, say:
"I do not have enough information in the provided documents."

Rules:
- Do not use external knowledge
- Do not guess
- Cite sources using [doc_id:chunk_index]
- Use conversation history to understand what the user is referring to

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONVERSATION HISTORY (what has been discussed so far):
{conversation_history}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Session Memory (facts, goals, preferences):
{session_memory}

Retrieved Context (use this to answer):
{context}

Current Question from User:
{question}

Your Answer (cite sources with [doc_id:chunk_index]):
"""

def reasoning_agent(question: str, retrieved_docs: list[dict], session_id: str) -> str:
    if not retrieved_docs:
        return "I do not have enough information in the provided documents."
    
    memory_items = get_session_memory(session_id)
    
    # Separate conversation history from other memory types
    conversation_items = [m for m in memory_items if m["type"] == "conversation"]
    other_memory_items = [m for m in memory_items if m["type"] != "conversation"]
    
    memory_read_span = langfuse.start_span(
        name="memory.read",
        input={
            "session_id": session_id,
            "memory_count": len(memory_items),
            "conversation_count": len(conversation_items),
            "memory_types": list({m["type"] for m in memory_items}) if memory_items else [],
        },
    )
    
    # Format conversation history (last 10 items = 5 exchanges)
    if conversation_items:
        recent_conversation = conversation_items[-10:]  # Last 10 items (5 exchanges)
        conversation_history = "\n".join([m["content"] for m in recent_conversation])
    else:
        conversation_history = "No previous conversation."
    
    # Format session memory (goals, preferences, facts)
    if other_memory_items:
        memory_lines = [
            f"- ({m['type']}) {m['content']}"
            for m in other_memory_items
        ]
        session_memory = "\n".join(memory_lines)
    else:
        session_memory = "No relevant session memory."

    context_blocks = []
    for d in retrieved_docs:
        source = f"[{d['doc_id']}:{d['chunk_index']}]"
        context_blocks.append(f"{d['text']}\nSource: {source}")

    context = "\n\n".join(context_blocks)

    memory_read_span.update(output={
        "conversation_history_length": len(conversation_history),
        "has_conversation": bool(conversation_items),
    })
    memory_read_span.end()
    
    response = llm.invoke(
        REASONING_PROMPT.format(
            conversation_history=conversation_history,
            session_memory=session_memory,
            context=context,
            question=question
        )
    )
    return response.content.strip()