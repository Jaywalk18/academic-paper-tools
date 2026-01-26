---
name: ref-check
description: Verify BibTeX references for academic papers. Checks citation accuracy against Crossref and OpenAlex databases. Use when the user wants to check references, verify citations, validate a .bib file, or find potential citation errors.
---

# RefCheck - BibTeX Reference Verification

This skill verifies academic references by querying real bibliographic databases and analyzing the results.

## Activation Triggers

Use this skill when the user:
- Asks to "check references" or "verify citations"
- Wants to validate a `.bib` file
- Asks about potential citation errors
- Mentions bibliography verification or reference checking

## Verification Process

### Step 1: Locate and Read BibTeX File

1. Find `.bib` files in the project (common names: `main.bib`, `references.bib`, `ref.bib`)
2. Read the BibTeX content using `Read` tool

### Step 2: Parse BibTeX Entries

Extract key information from each entry:
- **Citation key**: The identifier (e.g., `smith2023deep`)
- **Title**: The paper/book title
- **Authors**: Author names (focus on first author's last name)
- **Year**: Publication year
- **Venue**: Journal, conference, or publisher

### Step 3: Query Academic Databases

For each reference, query **Crossref** (free, no API key needed):

```bash
# Using curl to query Crossref
curl "https://api.crossref.org/works?query.bibliographic=TITLE&rows=3"
```

Or use `WebFetch` tool with URL:
```
https://api.crossref.org/works?query.bibliographic=ENCODED_TITLE&rows=3
```

**Alternative: OpenAlex** (also free):
```
https://api.openalex.org/works?search=ENCODED_TITLE&per-page=3
```

### Step 4: Compare and Score

For each reference, compare BibTeX entry with database results:

| Check | Verified | Uncertain | Suspicious |
|-------|----------|-----------|------------|
| Title similarity | ≥90% | 70-89% | <70% |
| First author match | Found | Missing info | Not found |
| Year match | ±1 year | Missing | ≥2 years off |

### Step 5: Generate Report

Produce a verification report:

```markdown
## Reference Verification Report

### Summary
- **Total references**: 45
- ✅ **Verified**: 38 (84%)
- ⚠️ **Uncertain**: 5 (11%)
- ❌ **Suspicious**: 2 (5%)

### Suspicious References (Need Attention)

#### 1. `fabricated2023`
- **BibTeX title**: "A Novel Approach to Everything"
- **Issue**: No matching papers found in any database
- **Action**: Verify this reference exists; may be fabricated

#### 2. `smith2020deep`
- **BibTeX title**: "Deep Learning Methods"
- **Best match**: "Deep Learning Methods for Computer Vision" (sim: 0.72)
- **Issue**: Title significantly different; year mismatch (2020 vs 2019)
- **Action**: Verify correct paper; update title and year if needed

### Uncertain References (Review Recommended)

#### 1. `jones2022neural`
- **Issue**: Author name not found in matched paper's author list
- **Suggestion**: Check if author order or name spelling is correct

### Verified References
[List of verified references - can be collapsed]

### Suggested Corrections

\`\`\`bibtex
% smith2020deep - suggested correction:
@article{smith2020deep,
  title = {Deep Learning Methods for Computer Vision},
  author = {Smith, John and Doe, Jane},
  year = {2019},  % Changed from 2020
  journal = {IEEE TPAMI}
}
\`\`\`
```

## API Response Parsing

### Crossref Response Structure
```json
{
  "message": {
    "items": [
      {
        "title": ["Paper Title"],
        "author": [{"given": "John", "family": "Smith"}],
        "issued": {"date-parts": [[2023]]},
        "container-title": ["Journal Name"]
      }
    ]
  }
}
```

### OpenAlex Response Structure
```json
{
  "results": [
    {
      "title": "Paper Title",
      "publication_year": 2023,
      "authorships": [{"author": {"display_name": "John Smith"}}],
      "host_venue": {"display_name": "Journal Name"}
    }
  ]
}
```

## Scoring Algorithm

```
title_sim = fuzzy_match(bib_title, ref_title)  # 0-1 scale
author_match = first_author_in_ref_authors     # true/false/null
year_match = abs(bib_year - ref_year) <= 1     # true/false/null

if title_sim >= 0.90 and author_match and year_match:
    status = "verified"
elif title_sim < 0.55 or (multiple severe mismatches):
    status = "suspicious"
else:
    status = "uncertain"
```

## Batch Processing Strategy

For large `.bib` files (>20 entries):
1. Process in batches of 5-10 to avoid rate limits
2. Add 0.5s delay between API calls
3. Report progress: "Checking references 1-10 of 45..."

## Common Issues Detected

| Issue | Description | Severity |
|-------|-------------|----------|
| Title mismatch | BibTeX title differs from official title | High |
| Year mismatch | Publication year incorrect | Medium |
| Author mismatch | First author not found | Medium |
| Venue mismatch | Journal/conference name differs | Low |
| No results | Reference not found in any database | Critical |
| Duplicate entry | Same paper cited with different keys | Low |

## Important Notes

1. **Rate Limiting**: Crossref allows ~50 requests/second for polite users; add delays for large batches
2. **Title Encoding**: URL-encode special characters in titles
3. **False Positives**: Some legitimate papers may not be in databases (preprints, very recent, etc.)
4. **Manual Verification**: Always recommend manual check for suspicious entries

## Example Interaction

**User**: Check the references in release/main.bib

**Agent Actions**:
1. `Read release/main.bib` → Parse BibTeX entries
2. For each entry (or sample if many):
   - Extract title, author, year
   - `WebFetch https://api.crossref.org/works?query.bibliographic=...`
   - Compare results with BibTeX entry
3. Compile verification report with issues found
4. Suggest corrections for problematic entries
