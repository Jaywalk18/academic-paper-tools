[English](README.md) | [中文](README_CN.md)

# Academic Paper Tools - Cursor Agent Skills

Agent-native tools for academic paper workflows. Designed specifically for Cursor AI to leverage its built-in capabilities.

## Design Philosophy

These skills are designed as **Agent-native** tools:

- **No external LLM calls** - The Cursor Agent itself analyzes content directly
- **Direct file access** - Reads TeX source, figures, and bibliography files natively
- **Minimal dependencies** - Only calls external APIs when necessary (e.g., bibliographic databases)
- **LaTeX-first** - Optimized for TeX projects, reading source files for better analysis

## Available Skills

### 1. Paper Review (`paper-review/`)

AI-powered academic paper review that analyzes LaTeX source files directly.

**Features:**
- Reads `.tex` files to understand paper structure and content
- Analyzes figures for visual quality
- Checks bibliography completeness
- Provides structured review with specific file/line references

**Usage:**
```
"Review my paper in the release/ folder"
"Give me feedback on the experiments section"
"What are the weaknesses of this paper?"
```

### 2. Reference Check (`ref-check/`)

Verifies BibTeX references against academic databases (Crossref, OpenAlex).

**Features:**
- Parses `.bib` files directly
- Queries free academic APIs (no API key required)
- Detects title mismatches, year errors, missing papers
- Suggests corrections

**Usage:**
```
"Check the references in main.bib"
"Verify my citations"
"Are there any suspicious references?"
```

## Installation

### Option 1: Copy to Cursor Skills Directory

**Windows:**
```powershell
Copy-Item -Recurse .\paper-review\ "$env:USERPROFILE\.cursor\skills\paper-review"
Copy-Item -Recurse .\ref-check\ "$env:USERPROFILE\.cursor\skills\ref-check"
```

**macOS/Linux:**
```bash
cp -r ./paper-review ~/.cursor/skills/
cp -r ./ref-check ~/.cursor/skills/
```

### Option 2: Use Directly in Project

Place the skill folders in your project's `.cursor/skills/` directory.

## Why Agent-Native?

Traditional approaches call external LLM APIs from scripts:

```
❌ Old: User → Cursor Agent → Python Script → OpenAI API → Response
```

This is redundant - Cursor Agent already IS a powerful LLM!

```
✅ New: User → Cursor Agent (directly analyzes files) → Response
```

**Benefits:**
- **Faster** - No extra API roundtrips
- **Cheaper** - No additional API costs
- **Better context** - Agent sees full project structure
- **More precise** - Can reference exact file locations

## Why TeX Source Over PDF?

For LaTeX projects, reading source files is superior to PDF:

| Aspect | PDF | TeX Source |
|--------|-----|------------|
| Text quality | May lose formatting | Perfect |
| Math formulas | Often garbled | Original LaTeX |
| Structure | Must infer | Explicit sections |
| Figures | Compressed | Original quality |
| Editability | "Page 5, paragraph 2" | "line 42 in method.tex" |

## Project Structure

```
cursor-skills/
├── paper-review/
│   ├── SKILL.md          # Main skill definition
│   └── prompts.md        # Reference prompts (optional)
├── ref-check/
│   ├── SKILL.md          # Main skill definition
│   └── reference.md      # API documentation (optional)
├── README.md
└── README_CN.md
```

## Requirements

- Cursor IDE with Agent mode
- No additional dependencies for paper-review
- Internet connection for ref-check (API queries)

## License

MIT License

## Acknowledgments

**Inspired by:**
- [PaperDecision](https://github.com/PaperDecision/PaperDecision) - Multi-agent paper review concepts
- [RefCheck.ai](https://github.com/HuaHenry/RefCheck_ai) - Reference verification methodology

**Data Sources:**
- [Crossref](https://www.crossref.org/) - Free scholarly metadata API
- [OpenAlex](https://openalex.org/) - Open catalog of scholarly works
