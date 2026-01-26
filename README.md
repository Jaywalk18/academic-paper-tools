[English](README.md) | [中文](README_CN.md)

# Academic Paper Tools

AI-powered tools for academic paper workflows. Works with Cursor, CLI, and other AI editors.

This repository contains two tools:

1. **paper-review** - AI-powered paper review simulation using multi-agent system
2. **ref-check** - BibTeX reference verification against academic databases

## Features

### Paper Review Skill

- **Multi-Agent Pipeline**: Uses 4 AI agents to simulate the academic review process
- **Visual Analysis**: Analyzes PDF pages to extract technical contributions
- **Review Synthesis**: Evaluates reviewer comments and identifies credibility
- **Rebuttal Analysis**: Assesses author responses to reviewer concerns
- **Decision Prediction**: Predicts acceptance (Oral/Spotlight/Poster/Reject)

### RefCheck Skill

- **Multi-Source Verification**: Checks references against Crossref, OpenAlex, and Semantic Scholar
- **Accuracy Scoring**: Computes title similarity, author match, and year match
- **Status Classification**: Classifies each reference as verified/uncertain/suspicious
- **Detailed Reports**: Provides diff details and suggested corrections

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/Jaywalk18/academic-paper-tools.git
cd academic-paper-tools
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

**For Paper Review** (required):
```bash
# Windows PowerShell
$env:PAPER_REVIEW_API_KEY = "your-openai-api-key"

# macOS/Linux
export PAPER_REVIEW_API_KEY="your-openai-api-key"
```

**For RefCheck** (optional, enhances search):
```bash
# Windows PowerShell
$env:SEMANTIC_SCHOLAR_API_KEY = "your-s2-api-key"

# macOS/Linux
export SEMANTIC_SCHOLAR_API_KEY="your-s2-api-key"
```

## Usage

### Command Line

### Paper Review

```bash
# Basic review (PDF only)
python paper-review/scripts/review_paper.py --pdf paper.pdf

# With reviewer comments
python paper-review/scripts/review_paper.py --pdf paper.pdf --reviews reviews.json

# Save output
python paper-review/scripts/review_paper.py --pdf paper.pdf -o result.json
```

### RefCheck

```bash
# Check a .bib file
python ref-check/scripts/check_references.py --bib references.bib

# Check inline BibTeX
python ref-check/scripts/check_references.py --content "@article{key, title={...}}"

# Save report
python ref-check/scripts/check_references.py --bib refs.bib -o report.json
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `PAPER_REVIEW_API_KEY` | Yes (paper-review) | OpenAI-compatible API key |
| `PAPER_REVIEW_API_BASE` | No | Custom API base URL (default: OpenAI) |
| `PAPER_REVIEW_MODEL` | No | Model name (default: gpt-4o) |
| `SEMANTIC_SCHOLAR_API_KEY` | No | Semantic Scholar API key for enhanced search |

## Output Examples

### Paper Review Output

```json
{
  "title": "Deep Learning for NLP",
  "prediction": "Poster",
  "final_score": 7.5,
  "decision": {
    "final_decision": "Poster",
    "decision_archetype": "Uncontested_Success",
    "key_factor": "Strong empirical results",
    "confidence": "High"
  }
}
```

### RefCheck Output

```json
{
  "summary": {
    "total": 10,
    "counts": {
      "verified": 7,
      "uncertain": 2,
      "suspicious": 1
    }
  },
  "items": [
    {
      "key": "smith2023",
      "status": "verified",
      "score": 90,
      "best_match": {
        "title": "...",
        "sim_title": 0.95
      }
    }
  ]
}
```

## System Requirements

- Python 3.8+
- Internet connection for API calls

### Additional Requirements for Paper Review

- Poppler (for PDF processing)
  - **Windows**: Download from [poppler-for-windows](https://github.com/osber/poppler-for-windows/releases)
  - **macOS**: `brew install poppler`
  - **Linux**: `apt-get install poppler-utils`

## AI Editor Integration (Optional)

These tools can be used as Agent Skills in AI-powered editors like Cursor:

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

Then you can use natural language commands like:
- "Review this paper: paper.pdf"
- "Check the references in paper.bib"

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

**Based on:**
- [PaperDecision](https://github.com/PaperDecision/PaperDecision) - Multi-agent paper review prediction system
- [RefCheck.ai](https://github.com/HuaHenry/RefCheck_ai) - BibTeX reference verification tool

**Data Sources:**
- [Crossref](https://www.crossref.org/) - Scholarly metadata API
- [OpenAlex](https://openalex.org/) - Open catalog of scholarly works
- [Semantic Scholar](https://www.semanticscholar.org/) - AI-powered research tool
