"""Test LangSmith tracing configuration"""
import os
from observability.langsmith_client import langsmith_enabled

print("\n🔍 LangSmith Configuration Check")
print("=" * 50)

# Check environment variables
print(f"\n📋 Environment Variables:")
print(f"LANGCHAIN_TRACING_V2: {os.getenv('LANGCHAIN_TRACING_V2')}")
print(f"LANGCHAIN_PROJECT: {os.getenv('LANGCHAIN_PROJECT')}")
print(f"LANGCHAIN_ENDPOINT: {os.getenv('LANGCHAIN_ENDPOINT')}")
print(f"LANGCHAIN_API_KEY: {'*' * 20 if os.getenv('LANGCHAIN_API_KEY') else 'Not set'}")

print(f"\n✨ LangSmith Status: {'✅ ENABLED' if langsmith_enabled else '❌ DISABLED'}")

if langsmith_enabled:
    print("\n🎉 LangSmith is properly configured!")
    print("\n📖 Next steps:")
    print("1. Run: streamlit run app.py")
    print("2. Send some messages in the chat")
    print("3. Check your LangSmith dashboard at https://smith.langchain.com")
    print(f"4. Look for traces in project: {os.getenv('LANGCHAIN_PROJECT')}")
    print("\n💡 LangSmith automatically traces all LangChain/LangGraph operations")
    print("   No manual instrumentation needed!")
else:
    print("\n⚠️  LangSmith is not configured")
    print("\n📝 To enable LangSmith, add to your .env file:")
    print("LANGSMITH_API_KEY=your_api_key_here")
    print("LANGSMITH_PROJECT=lumiere  # Optional, defaults to 'lumiere'")
    print("\nOr use the alternative names:")
    print("LANGCHAIN_API_KEY=your_api_key_here")
    print("LANGCHAIN_PROJECT=lumiere")
