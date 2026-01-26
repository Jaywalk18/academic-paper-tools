# RefCheck - API Reference

This document provides technical details for the reference verification skill.

## Academic Database APIs

### Crossref API

**Endpoint:** `https://api.crossref.org/works`

**Query Parameters:**
| Parameter | Description | Example |
|-----------|-------------|---------|
| `query.bibliographic` | Search by title/author | `Deep Learning for NLP` |
| `query.author` | Filter by author | `Smith` |
| `rows` | Number of results | `5` |
| `filter` | Date filter | `from-pub-date:2023-01-01` |

**Example Request:**
```
https://api.crossref.org/works?query.bibliographic=Attention+Is+All+You+Need&rows=3
```

**Response Structure:**
```json
{
  "status": "ok",
  "message": {
    "items": [
      {
        "DOI": "10.xxxxx",
        "title": ["Attention Is All You Need"],
        "author": [
          {"given": "Ashish", "family": "Vaswani"},
          {"given": "Noam", "family": "Shazeer"}
        ],
        "issued": {"date-parts": [[2017]]},
        "container-title": ["Advances in Neural Information Processing Systems"]
      }
    ]
  }
}
```

**Rate Limits:** ~50 requests/second for polite users (include email in User-Agent)

---

### OpenAlex API

**Endpoint:** `https://api.openalex.org/works`

**Query Parameters:**
| Parameter | Description | Example |
|-----------|-------------|---------|
| `search` | Full-text search | `transformer attention mechanism` |
| `filter` | Field filters | `publication_year:2023` |
| `per-page` | Results per page | `5` |

**Example Request:**
```
https://api.openalex.org/works?search=BERT+pre-training&per-page=3
```

**Response Structure:**
```json
{
  "results": [
    {
      "id": "https://openalex.org/W2963403868",
      "title": "BERT: Pre-training of Deep Bidirectional Transformers",
      "publication_year": 2019,
      "authorships": [
        {
          "author": {
            "display_name": "Jacob Devlin"
          }
        }
      ],
      "host_venue": {
        "display_name": "NAACL"
      }
    }
  ]
}
```

**Rate Limits:** 100,000 requests/day without API key

---

## Verification Algorithm

### Title Similarity

Use fuzzy string matching (token sort ratio):

```
similarity = token_sort_ratio(normalize(bib_title), normalize(ref_title))
```

**Normalization:**
1. Convert to lowercase
2. Remove LaTeX commands (`\textbf{}`, etc.)
3. Remove special characters
4. Collapse whitespace

**Thresholds:**
- ≥ 0.90: Verified
- 0.70-0.89: Uncertain
- < 0.70: Suspicious
- < 0.55: Very suspicious (likely wrong paper)

### Author Matching

Extract first author's last name from BibTeX:
```
"Smith, John and Doe, Jane" → "smith"
"John Smith and Jane Doe" → "smith"
```

Check if first author appears in reference's author list (case-insensitive).

### Year Matching

```
if abs(bib_year - ref_year) <= 1:
    match = True  # Allow 1 year tolerance for publication delays
elif abs(bib_year - ref_year) >= 2:
    match = False  # Likely error
```

### Final Status

```python
def classify(title_sim, author_match, year_match):
    if title_sim >= 0.90 and author_match and year_match:
        return "verified"
    
    # Very severe issues
    if title_sim < 0.55:
        return "suspicious"
    
    # Count severe issues
    severe = 0
    if title_sim < 0.70:
        severe += 1
    if author_match == False:  # Not None
        severe += 1
    if year_match == False and year_diff >= 2:
        severe += 1
    
    if severe >= 2:
        return "suspicious"
    
    return "uncertain"
```

---

## Common BibTeX Issues

### 1. Title Errors

**Truncated titles:**
```bibtex
% Wrong
title = {Deep Learning}
% Correct
title = {Deep Learning for Natural Language Processing}
```

**Extra words:**
```bibtex
% Wrong (includes subtitle)
title = {BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding}
% Correct (conference version)
title = {BERT: Pre-training of Deep Bidirectional Transformers}
```

### 2. Author Errors

**Name order:**
```bibtex
% Wrong (family name not first)
author = {John Smith and Jane Doe}
% Better (standard format)
author = {Smith, John and Doe, Jane}
```

**Missing authors:**
```bibtex
% Wrong (only first author)
author = {Vaswani, Ashish}
% Correct
author = {Vaswani, Ashish and Shazeer, Noam and Parmar, Niki and ...}
```

### 3. Year Errors

Common causes:
- arXiv year vs. publication year
- Conference vs. journal version
- Typos

### 4. Venue Errors

```bibtex
% Inconsistent
booktitle = {NeurIPS}
booktitle = {Advances in Neural Information Processing Systems}
booktitle = {NeurIPS 2023}
```

---

## URL Encoding

When constructing API URLs, encode special characters:

| Character | Encoded |
|-----------|---------|
| Space | `%20` or `+` |
| `&` | `%26` |
| `=` | `%3D` |
| `?` | `%3F` |
| `:` | `%3A` |

**Example:**
```
Title: "What is BERT?"
Encoded: What%20is%20BERT%3F
```

---

## Error Handling

### API Errors

| Status | Meaning | Action |
|--------|---------|--------|
| 200 | Success | Process results |
| 404 | Not found | Mark as "no results" |
| 429 | Rate limited | Wait and retry |
| 500+ | Server error | Try alternative API |

### No Results

If no results from any API:
1. Check if title is very unusual or contains special characters
2. Paper may be preprint-only (not indexed)
3. Paper may be very recent
4. Paper may not exist (fabricated reference)

---

## Batch Processing

For large `.bib` files:

1. **Parse all entries first**
2. **Process in batches of 5-10**
3. **Add delays between batches** (0.5-1 second)
4. **Report progress** to user
5. **Handle failures gracefully** (continue with next entry)

```
Processing references...
[=====>                    ] 12/45 (27%)
```
