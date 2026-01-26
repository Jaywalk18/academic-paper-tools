# Contributing to Academic Paper Tools

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## How to Contribute

### Reporting Issues

- Check existing issues before creating a new one
- Include clear reproduction steps
- Provide your environment details (OS, Python version, AI assistant used)

### Submitting Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Test your changes
5. Commit with clear messages (`git commit -m "Add: description"`)
6. Push to your fork (`git push origin feature/your-feature`)
7. Open a Pull Request

### Commit Message Convention

```
Add: new feature or file
Fix: bug fix
Update: improvement to existing feature
Docs: documentation changes
Refactor: code refactoring without feature changes
```

## Development Guidelines

### Skill Structure

Each skill should follow this structure:

```
skill-name/
├── SKILL.md              # Main skill definition (required)
├── references/           # Supporting documentation (optional)
│   └── *.md
└── scripts/              # Helper scripts (optional)
    └── *.py
```

### SKILL.md Format

Include YAML frontmatter:

```yaml
---
name: skill-name
description: Brief description of what the skill does
version: 1.0.0
author: Your Name
license: MIT
tags: [Tag1, Tag2, Tag3]
dependencies: [package1, package2]
---
```

### Code Style

- Python: Follow PEP 8
- Use type hints where appropriate
- Include docstrings for functions
- Handle errors gracefully

### Testing

Before submitting:

1. Test with at least one AI assistant (Cursor, Claude Code, etc.)
2. Verify scripts work with sample inputs
3. Check for edge cases

## Questions?

Open an issue with the `question` label.
