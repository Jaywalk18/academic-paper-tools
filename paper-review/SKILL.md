---
name: paper-review
description: Review academic papers using multi-agent AI simulation. Predicts paper acceptance decisions (Oral/Spotlight/Poster/Reject) by analyzing PDF content, reviewer comments, and rebuttals. Use when the user asks to review a paper, evaluate a submission, predict acceptance, or mentions ICLR/NeurIPS/ICML paper review.
---

# Paper Review - AI-Powered Academic Paper Evaluation

This skill simulates the academic paper review process using a multi-agent system to predict paper acceptance decisions.

## Quick Start

When the user wants to review a paper:

1. **Locate the paper file** - Find the PDF file path
2. **Check for review data** - Look for accompanying JSON with reviewer comments (optional)
3. **Run the review script**:

```bash
python scripts/review_paper.py --pdf "path/to/paper.pdf"
```

With reviewer data:
```bash
python scripts/review_paper.py --pdf "path/to/paper.pdf" --reviews "path/to/reviews.json"
```

## Environment Setup

Required environment variable:
- `PAPER_REVIEW_API_KEY` - OpenAI-compatible API key (required)
- `PAPER_REVIEW_API_BASE` - API base URL (optional, defaults to OpenAI)
- `PAPER_REVIEW_MODEL` - Model name (optional, defaults to gpt-4o)

## Review Process

The system uses 4 AI agents in sequence:

### Agent 1: Visual Content Evaluator
Analyzes PDF pages to extract:
- Core technical claims
- Novelty level (Groundbreaking/Significant/Incremental)
- Award potential
- Visual quality assessment

### Agent 2: Review Synthesizer
Analyzes reviewer comments to determine:
- Reviewer credibility (Expert/Competent/Shallow)
- Fatal flaw allegations
- Consensus type
- Risk level

### Agent 3: Rebuttal Analyzer
Evaluates author responses:
- Rebuttal effectiveness
- Success rate of addressing concerns
- Reviewer final states

### Agent 4: Decision Coordinator
Makes final prediction:
- Decision: Oral / Spotlight / Poster / Reject
- Confidence level
- Key deciding factors

## Output Format

The script outputs a JSON report:

```json
{
  "title": "Paper Title",
  "prediction": "Poster",
  "final_score": 7.5,
  "decision": {
    "final_decision": "Poster",
    "decision_archetype": "Uncontested_Success",
    "key_factor": "Strong empirical results",
    "confidence": "High"
  },
  "reasoning": "Detailed explanation..."
}
```

## Input Formats

### PDF Only Mode
Just provide the PDF - the system will analyze visual content and provide a preliminary assessment.

### Full Review Mode
Provide PDF + JSON with review data in this format:

```json
{
  "title": "Paper Title",
  "abstract": "Paper abstract...",
  "peer_discussion": [
    {
      "review": {
        "rating": 6,
        "confidence": 4,
        "summary": "...",
        "strengths": "...",
        "weaknesses": "..."
      },
      "comments_tree": []
    }
  ],
  "official_comment": []
}
```

## Usage Examples

**Simple review:**
> "Review this paper: paper.pdf"

**With specific questions:**
> "What are the chances this paper gets accepted to ICLR?"

**Batch review:**
> "Review all PDFs in the submissions/ folder"

## Dependencies

Install required packages:
```bash
pip install openai pdf2image Pillow
```

Note: `pdf2image` requires Poppler. Install via:
- Windows: Download from https://github.com/osber/poppler-for-windows/releases
- macOS: `brew install poppler`
- Linux: `apt-get install poppler-utils`

## Prompts Reference

For detailed agent prompts, see [prompts.md](prompts.md).
