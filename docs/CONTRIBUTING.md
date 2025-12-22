# Contributing to Lumiere

Thank you for your interest in contributing to Lumiere! This document provides guidelines and instructions for contributing.

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
   ```bash
   git clone https://github.com/kikomatchi/lumiere.git
   cd lumiere
   ```
3. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## 🌿 Branching Strategy

- `main` - Stable production branch
- `develop` - Development branch
- `feature/*` - New features
- `fix/*` - Bug fixes
- `docs/*` - Documentation updates

**Create a feature branch:**
```bash
git checkout -b feature/your-feature-name
```

## 📝 Commit Messages

Follow conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(memory): add memory consolidation feature
fix(rag): resolve chunking overlap issue
docs(readme): update installation instructions
```

## 🧪 Testing

Before submitting a PR:

1. **Test your changes locally**
   ```bash
   streamlit run app.py
   ```

2. **Run semantic memory tests**
   ```bash
   python scripts/retrieval_test.py
   ```

3. **Check for errors**
   - Look for exceptions in terminal
   - Test all affected features
   - Verify memory storage/retrieval

## 📋 Code Style

### Python Style Guide

- Follow **PEP 8** guidelines
- Use **type hints** for function parameters and returns
- Add **docstrings** to all functions and classes
- Keep functions **small and focused**
- Use **meaningful variable names**

**Example:**
```python
def retrieve_memories(
    query: str,
    top_k: int = 3,
    user_id: Optional[str] = None,
    min_score: float = 0.7
) -> List[Dict[str, Any]]:
    """
    Retrieve relevant memories from vector database.
    
    Args:
        query: Search query text
        top_k: Number of memories to retrieve
        user_id: Optional user identifier for filtering
        min_score: Minimum similarity score threshold
        
    Returns:
        List of memory dictionaries with content and metadata
    """
    # Implementation...
```

### Import Organization

```python
# Standard library
import os
from typing import List, Dict, Optional

# Third-party
from langchain.chat_models import ChatOpenAI
import streamlit as st

# Local
from config.settings import OPENAI_API_KEY
from rag.retriever import retrieve_documents
```

## 🎯 Areas for Contribution

### High Priority

- [ ] **Multi-user support**: User isolation and permissions
- [ ] **Memory management**: Pruning and consolidation
- [ ] **Testing**: Unit tests for core components
- [ ] **Documentation**: API documentation, tutorials
- [ ] **Performance**: Query optimization, caching

### Medium Priority

- [ ] **UI improvements**: Better visualizations, responsive design
- [ ] **Agent enhancements**: New reasoning strategies
- [ ] **Data sources**: Support for more file types
- [ ] **Export features**: Memory export, conversation history
- [ ] **Configuration**: More customization options

### Nice to Have

- [ ] **Plugins**: Plugin system for extensibility
- [ ] **Integrations**: Slack, Discord, etc.
- [ ] **Analytics**: Usage statistics, insights
- [ ] **Internationalization**: Multi-language support

## 📤 Submitting a Pull Request

1. **Update your branch** with latest main
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-branch
   git rebase main
   ```

2. **Push your changes**
   ```bash
   git push origin your-branch
   ```

3. **Create a Pull Request** on GitHub

4. **PR Description** should include:
   - What changes were made
   - Why the changes are needed
   - How to test the changes
   - Screenshots (if UI changes)
   - Related issues (if applicable)

**PR Template:**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
How to test the changes

## Screenshots (if applicable)

## Checklist
- [ ] Code follows style guidelines
- [ ] Added/updated documentation
- [ ] Tested locally
- [ ] No breaking changes
```

## 🐛 Reporting Bugs

### Before Reporting

1. **Search existing issues** to avoid duplicates
2. **Try the latest version** from main branch
3. **Gather information**:
   - Python version
   - OS and version
   - Error messages/stack traces
   - Steps to reproduce

### Bug Report Template

```markdown
**Describe the bug**
Clear description of the issue

**To Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What should happen

**Screenshots**
If applicable

**Environment**
- OS: [e.g., macOS 14.0]
- Python: [e.g., 3.11.5]
- Lumiere version: [e.g., commit hash]

**Additional context**
Any other relevant information
```

## 💡 Feature Requests

We welcome feature suggestions! Please:

1. **Check roadmap** in README.md
2. **Search existing issues** for similar requests
3. **Provide context**:
   - Use case
   - Expected behavior
   - Potential implementation approach
   - Benefits to users

## 📚 Documentation

Good documentation is crucial! Contributions needed:

- **Code comments**: Explain complex logic
- **Docstrings**: All public functions/classes
- **README updates**: Keep installation/usage current
- **Tutorials**: Step-by-step guides
- **Architecture docs**: System design explanations

## 🔍 Code Review Process

All PRs require review before merging:

1. **Automated checks** must pass
2. **Code review** by maintainer
3. **Testing** verification
4. **Documentation** review

**Review criteria:**
- Code quality and style
- Test coverage
- Documentation completeness
- Performance impact
- Breaking changes

## 🎨 Design Philosophy

When contributing, keep these principles in mind:

1. **Simplicity**: Favor simple solutions over complex ones
2. **Modularity**: Keep components loosely coupled
3. **Extensibility**: Design for future enhancements
4. **User-first**: Prioritize user experience
5. **Performance**: Be mindful of latency and costs

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and ideas
- **Documentation**: Check existing docs first

## 🏆 Recognition

Contributors will be:
- Listed in README.md
- Credited in release notes
- Acknowledged in documentation

Thank you for contributing to Lumiere! 🌟
