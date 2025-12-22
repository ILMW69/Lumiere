# 📚 Lumiere Documentation

This folder contains all documentation for the Lumiere project.

## 📖 Documentation Files

### Getting Started
- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup guide for new users
- **[../README.md](../README.md)** - Main project README (in root directory)

### Technical Documentation
- **[GRAPH_ARCHITECTURE.md](GRAPH_ARCHITECTURE.md)** - Detailed system architecture and workflow

### Contributing & Changelog
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and release notes

### Reference
- **[DOCUMENTATION.md](DOCUMENTATION.md)** - Complete documentation index

## 🎨 Visual Assets

- **[graph_visualization.png](graph_visualization.png)** - System architecture diagram
- **[graph_visualization.mmd](graph_visualization.mmd)** - Mermaid source for diagram

---

## 📋 Quick Navigation

| I want to... | Go to... |
|--------------|----------|
| **Get started quickly** | [QUICKSTART.md](QUICKSTART.md) |
| **Understand the architecture** | [GRAPH_ARCHITECTURE.md](GRAPH_ARCHITECTURE.md) |
| **Learn about semantic memory** | [SEMANTIC_MEMORY.md](SEMANTIC_MEMORY.md) |
| **Contribute** | [CONTRIBUTING.md](CONTRIBUTING.md) |
| **See what's new** | [CHANGELOG.md](CHANGELOG.md) |
| **Find all docs** | [DOCUMENTATION.md](DOCUMENTATION.md) |

## 🔧 Regenerating Documentation

### Update Architecture Diagram

```bash
# From project root
cd docs
python generate_graph_simple.py
```

This will regenerate `graph_visualization.png` with the latest architecture.

### Requirements

- Python 3.11+
- Pillow (for generate_graph_simple.py)
- Graphviz (optional, for generate_graph_image.py)

## 📝 Documentation Standards

When contributing documentation:

1. **Use Markdown** for all documentation files
2. **Include emojis** for visual appeal and quick navigation
3. **Add examples** wherever possible
4. **Keep it updated** with code changes
5. **Use relative links** for cross-references within docs/
6. **Test all code snippets** before documenting

## 🔗 External Links

- [Main Repository](../) - Go back to project root
- [Lumiere README](../README.md) - Main project documentation

---

**Last Updated:** December 22, 2025  
**Version:** 0.2.0
