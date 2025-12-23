"""Test Langfuse connection and event tracking"""
from observability.langfuse_client import langfuse
from langfuse.types import TraceContext
import time

if langfuse:
    print("✅ Langfuse client initialized")
    
    # Test event tracking
    try:
        # Create trace context with user_id and session_id
        trace_context = TraceContext(
            user_id="test_user",
            session_id="test_session"
        )
        print("✅ Trace context created")
        
        # Create input event
        langfuse.create_event(
            trace_context=trace_context,
            name="test_input",
            input={"message": "Hello Langfuse!"},
            metadata={"test": True, "type": "input"}
        )
        print("✅ Input event created")
        
        # Create output event
        langfuse.create_event(
            trace_context=trace_context,
            name="test_output",
            output={"response": "Test successful!"},
            metadata={"test": True, "type": "output"}
        )
        print("✅ Output event created")
        
        # Flush events
        langfuse.flush()
        print("✅ Events flushed to Langfuse")
        
        time.sleep(2)  # Give it time to send
        
        print("\n🎉 Langfuse test successful!")
        print("Check your Langfuse dashboard for test_input and test_output events")
        print("They should be grouped by session: test_session and user: test_user")
        
    except Exception as e:
        print(f"❌ Error testing Langfuse: {e}")
        import traceback
        traceback.print_exc()
else:
    print("❌ Langfuse not initialized - check your .env credentials")
