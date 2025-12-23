# LangSmith Observability Guide

## Setup Complete! ✅

LangSmith tracing is now enabled for Lumiere.

## What Gets Traced Automatically

LangSmith automatically captures:
- **All LangGraph workflow executions**
- **LangChain model calls** (OpenAI, embeddings)
- **Agent decisions and reasoning**
- **Tool calls** (retrieval, SQL execution)
- **Input/output for each step**
- **Latency and performance metrics**
- **Errors and exceptions**

## No Manual Instrumentation Needed!

Unlike Langfuse, LangSmith works automatically with LangChain/LangGraph.
Just set the environment variables and it traces everything.

## Environment Variables

Your `.env` should have:
```env
# LangSmith (required)
LANGSMITH_API_KEY=your_api_key
LANGSMITH_PROJECT=Lumiere

# Alternative names (also supported)
# LANGCHAIN_API_KEY=your_api_key
# LANGCHAIN_PROJECT=Lumiere
```

## Testing

Test configuration:
```bash
python test_langsmith.py
```

## Viewing Traces

1. Visit: https://smith.langchain.com
2. Select project: **Lumiere**
3. View traces in real-time as users interact with the app

## Trace Organization

LangSmith automatically groups traces by:
- **Run ID**: Each graph execution
- **Session**: Each conversation session
- **Tags**: Lumiere mode, user operations
- **Metadata**: User inputs, outputs, errors

## What You'll See

Each chat message creates a trace showing:
1. **Intent Classification** - Which mode/agent to use
2. **Retrieval** (if RAG) - Documents fetched and reranked
3. **SQL Generation** (if data) - Query created and executed
4. **Reasoning** - Agent thinking and response generation
5. **Critic Evaluation** - Answer quality check
6. **Memory Storage** - What gets remembered

## Benefits Over Langfuse

- ✅ Zero manual instrumentation
- ✅ Automatic trace grouping
- ✅ Native LangGraph support
- ✅ Detailed agent step visibility
- ✅ Performance metrics built-in
- ✅ Error tracking automatic
- ✅ Easier to maintain

## Troubleshooting

If traces aren't appearing:
1. Check `LANGCHAIN_TRACING_V2=true` is set
2. Verify API key is valid
3. Ensure project name matches
4. Wait 5-10 seconds for traces to appear

## Additional Features

LangSmith also provides:
- **Dataset creation** from traces
- **Evaluation runs** for testing
- **A/B testing** different prompts
- **Feedback collection** from users
- **Cost tracking** for API calls
