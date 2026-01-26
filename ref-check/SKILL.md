---
name: ref-check
description: Verify BibTeX references for academic papers. Checks citation accuracy against Crossref, OpenAlex, and Semantic Scholar databases. Use when the user wants to check references, verify citations, validate a .bib file, or mentions bibliography verification.
---

# RefCheck - BibTeX Reference Verification

This skill verifies the accuracy of BibTeX references by cross-checking against multiple academic databases.

## Quick Start

When the user wants to verify references:

1. **Locate the .bib file** or get the BibTeX content
2. **Run the verification script**:

```bash
python scripts/check_references.py --bib "path/to/references.bib"
```

Or verify inline BibTeX:
```bash
python scripts/check_references.py --content "@article{key, title={...}, ...}"
```

## Environment Setup

Optional environment variables:
- `SEMANTIC_SCHOLAR_API_KEY` - For enhanced S2 search (optional, free tier available)

Note: Crossref and OpenAlex are completely free and require no API keys.

## Verification Process

The system performs these steps for each BibTeX entry:

1. **Parse** - Extract entries from BibTeX
2. **Normalize** - Clean LaTeX, extract first author, normalize DOI
3. **Search** - Query multiple academic databases:
   - Crossref (bibliographic search)
   - OpenAlex (works search)
   - Semantic Scholar (optional, if API key provided)
4. **Score** - Find best matching candidate and compute similarity
5. **Classify** - Determine verification status

## Output Status

Each reference gets one of three statuses:

| Status | Criteria | Score |
|--------|----------|-------|
| **verified** | Title sim ≥ 0.90 + author match + year match (±1) | 90 |
| **uncertain** | Some inconsistencies but not severe | 60 |
| **suspicious** | Title sim < 0.55 OR multiple severe mismatches | 20 |

## Output Format

The script outputs a JSON report:

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
      "key": "smith2023deep",
      "status": "verified",
      "score": 90,
      "input": {
        "title": "Deep Learning for NLP",
        "year": 2023,
        "venue": "ACL"
      },
      "best_match": {
        "title": "Deep Learning for Natural Language Processing",
        "year": 2023,
        "authors": ["John Smith", "Jane Doe"],
        "sim_title": 0.95
      },
      "diff_fields": [],
      "red_flags": []
    }
  ]
}
```

## Usage Examples

**Check a .bib file:**
> "Check the references in paper.bib"

**Check specific entries:**
> "Verify this citation: @article{key, title={...}}"

**Save report:**
```bash
python scripts/check_references.py --bib refs.bib --output report.json
```

## Common Issues Detected

- **Title mismatch** - Citation title differs significantly from database
- **Author mismatch** - First author not found in reference authors
- **Year mismatch** - Publication year differs by more than 1 year
- **No candidates found** - Reference not found in any database (may be fabricated)

## Dependencies

Install required packages:
```bash
pip install requests rapidfuzz bibtexparser
```

## API Reference

For detailed information about the verification process and scoring algorithm, see [reference.md](reference.md).
