# Lumiere Test Suite

Comprehensive test coverage for the Lumiere AI knowledge workspace.

## 📋 Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Shared fixtures and configuration
├── test_semantic_memory.py  # Semantic memory system tests
├── test_intent_agent.py     # Intent classification tests
├── test_graph.py            # LangGraph workflow tests
└── test_rag.py              # RAG components tests
```

## 🚀 Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_semantic_memory.py
```

### Run Specific Test Class
```bash
pytest tests/test_semantic_memory.py::TestSemanticMemory
```

### Run Specific Test
```bash
pytest tests/test_semantic_memory.py::TestSemanticMemory::test_store_conversation_memory
```

### Run with Coverage
```bash
pytest --cov=. --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`.

### Run with Output
```bash
pytest -s
```

Shows print statements and other output during tests.

### Run Verbose
```bash
pytest -v
```

Shows detailed test execution information.

## 🏷️ Test Markers

Tests are organized with markers for selective execution:

### Run Only Unit Tests
```bash
pytest -m unit
```

### Run Only Integration Tests
```bash
pytest -m integration
```

### Skip Slow Tests
```bash
pytest -m "not slow"
```

### Skip Tests Requiring API
```bash
pytest -m "not requires_api"
```

## 📝 Test Coverage

### Current Test Coverage

| Component | File | Tests | Coverage |
|-----------|------|-------|----------|
| Semantic Memory | `test_semantic_memory.py` | 9 tests | Core functionality |
| Intent Agent | `test_intent_agent.py` | 6 tests | Classification logic |
| Graph Workflow | `test_graph.py` | 10 tests | State & routing |
| RAG Components | `test_rag.py` | 10 tests | Retrieval pipeline |

### What's Tested

✅ **Semantic Memory**
- Memory storage and retrieval
- Collection creation
- Metadata handling
- User filtering
- Memory formatting

✅ **Intent Agent**
- SQL query detection
- RAG query detection
- General query handling
- Memory context integration
- Error handling

✅ **Graph Workflow**
- State initialization
- Routing logic (ACCEPT/RETRY)
- Memory write operations
- Field name handling
- Mode detection

✅ **RAG Components**
- Text embedding
- Document chunking
- Document ingestion
- Document retrieval
- Collection management

## 🔧 Writing New Tests

### Test Structure

```python
import pytest
from unittest.mock import Mock, patch

class TestYourComponent:
    """Test suite for your component."""
    
    def test_basic_functionality(self, sample_state):
        """Test description."""
        # Setup
        # ...
        
        # Execute
        result = your_function()
        
        # Verify
        assert result == expected
```

### Using Fixtures

Shared fixtures are available in `conftest.py`:

- `mock_env_vars` - Mock environment variables
- `sample_session_id` - Test session ID
- `sample_user_id` - Test user ID
- `sample_state` - Complete AgentState
- `sample_conversation` - Test conversation data
- `mock_qdrant_client` - Mocked Qdrant client
- `mock_openai_embeddings` - Mocked embeddings
- `mock_llm_response` - Mocked LLM response

### Mocking External Dependencies

```python
@patch('module.external_dependency')
def test_with_mock(mock_dependency):
    """Test with mocked dependency."""
    # Configure mock
    mock_dependency.return_value = "test_value"
    
    # Test your code
    result = function_using_dependency()
    
    # Verify mock was called
    mock_dependency.assert_called_once()
```

## 🎯 Best Practices

### 1. Test Naming
- Use descriptive names: `test_store_memory_with_metadata`
- Follow pattern: `test_<what>_<condition>_<expected>`

### 2. Test Organization
- One test class per component
- Group related tests together
- Use clear docstrings

### 3. Assertions
- Be specific with assertions
- Test one thing per test
- Use descriptive failure messages

### 4. Mocking
- Mock external APIs (OpenAI, Qdrant)
- Don't mock the code you're testing
- Verify mock interactions

### 5. Fixtures
- Use fixtures for common setup
- Keep fixtures simple and focused
- Name fixtures clearly

## 🐛 Troubleshooting

### Import Errors

If you see `ModuleNotFoundError`:

```bash
# Make sure you're in the project root
cd /path/to/Lumiere

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest
```

### API Key Errors

Tests mock external APIs, but if you see API key errors:

```bash
# Set test environment variables
export OPENAI_API_KEY="test-key"
export LANGFUSE_PUBLIC_KEY="test-key"
```

Or use the `mock_env_vars` fixture.

### Database Connection Errors

Tests mock database connections, but if you encounter issues:

1. Check that `mock_qdrant_client` fixture is being used
2. Verify `@patch` decorators are correct
3. Ensure test functions accept mock parameters

## 📊 Continuous Integration

### GitHub Actions (Future)

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest --cov=. --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## 🎓 Learning Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [unittest.mock Guide](https://docs.python.org/3/library/unittest.mock.html)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)

## 📈 Future Improvements

- [ ] Add integration tests with real API calls (marked with `@pytest.mark.requires_api`)
- [ ] Add performance benchmarks
- [ ] Add end-to-end tests for Streamlit UI
- [ ] Increase coverage to 90%+
- [ ] Add property-based testing with Hypothesis
- [ ] Add mutation testing with mutmut

## 🤝 Contributing

When adding new features:

1. Write tests first (TDD)
2. Ensure all tests pass
3. Maintain > 80% coverage
4. Update this README if adding new test files

## 📞 Support

If you encounter issues with tests:

1. Check this README
2. Look at similar tests for examples
3. Review test output carefully
4. Open an issue with test failure details
