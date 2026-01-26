---
name: ref-check
description: Verify BibTeX references for academic papers. Checks citation accuracy against Crossref and OpenAlex databases using the RefCheck_ai algorithm. Use when the user wants to check references, verify citations, validate a .bib file, or find potential citation errors.
---

# RefCheck - BibTeX Reference Verification

This skill verifies academic references using the RefCheck_ai algorithm - querying multiple databases and using fuzzy matching to find the best candidates.

## Activation Triggers

Use this skill when the user:
- Asks to "check references" or "verify citations"
- Wants to validate a `.bib` file
- Asks about potential citation errors
- Mentions bibliography verification or reference checking

## Verification Process

### Step 1: Locate the BibTeX File

Find `.bib` files in the project (common names: `main.bib`, `references.bib`, `ref.bib`)

### Step 2: Run the Verification Script

**Preferred method** - Run the Python script for accurate batch verification.

> **⚠️ IMPORTANT: This is a long-running task!**
> - Each reference queries 3 databases with rate limiting (0.3s intervals)
> - 40 references ≈ 120 API calls ≈ **60-90 seconds**
> - **MUST run in background** with output to file, then check results after completion

```bash
# Install dependencies first (if needed)
pip install requests rapidfuzz bibtexparser

# ✅ CORRECT: Run in BACKGROUND with output file
python scripts/check_references.py --bib path/to/references.bib --output report.json &

# ❌ WRONG: Don't run foreground - will timeout/hang
# python scripts/check_references.py --bib path/to/references.bib
```

**Execution steps for Agent:**
1. Run script in **background** with `--output` flag
2. Inform user: "正在后台验证引用，预计需要 X 秒..."
3. Wait ~60-90 seconds (or check if output file exists)
4. Read the output JSON file
5. Generate human-readable report

The script:
1. Parses BibTeX and normalizes entries (strips LaTeX, extracts first author surname)
2. Queries **3 databases** for each reference: Crossref, OpenAlex, Semantic Scholar
3. Uses **fuzzy matching** (rapidfuzz token_sort_ratio) to find best candidate from all results
4. Classifies as `verified`, `uncertain`, or `suspicious` based on RefCheck_ai algorithm

### Step 3: Interpret Results

| Status | Criteria |
|--------|----------|
| **verified** | Title sim ≥90% + author match + year match (±1) |
| **uncertain** | Some inconsistencies but not severe |
| **suspicious** | Title sim <55% OR multiple severe mismatches |

### Step 4: Generate Report

Script output format:

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

## Algorithm Details (RefCheck_ai)

The script uses the RefCheck_ai algorithm:

1. **Multi-source search**: Query Crossref + OpenAlex + Semantic Scholar (if API key set)
2. **Candidate extraction**: Get top 5 candidates from each source (15 total)
3. **Fuzzy matching**: Use `rapidfuzz.fuzz.token_sort_ratio` for title similarity
4. **Best selection**: Score = title_sim × 0.90 + author × 0.05 + year × 0.05
5. **Classification**: Based on best match quality

```python
# Scoring formula
if title_sim >= 0.90 and author_hit and year_match:
    status = "verified"
elif title_sim < 0.55:
    status = "suspicious"  # Very low title match
elif severe_count >= 2:
    status = "suspicious"  # Multiple issues
else:
    status = "uncertain"
```

## Common Issues Detected

| Issue | Description | Severity |
|-------|-------------|----------|
| Title mismatch | BibTeX title differs from official | High |
| Year mismatch | Publication year off by ≥2 years | Medium |
| Author mismatch | First author not in matched paper | Medium |
| No candidates | Paper not found in any database | Critical |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SEMANTIC_SCHOLAR_API_KEY` | No | Enables S2 search for better coverage |

## Dependencies

```bash
pip install requests rapidfuzz bibtexparser
```

## Example Interaction

**User**: Check the references in release/main.bib

**Agent Actions**:

1. **Start background job:**
```bash
python scripts/check_references.py --bib release/main.bib --output refcheck_report.json &
```

2. **Inform user:**
> "正在后台验证 release/main.bib 中的引用，预计需要 60-90 秒。完成后我会生成报告。"

3. **Wait and check output file** (after ~60-90s):
```bash
# Check if file exists and has content
ls -la refcheck_report.json
```

4. **Read results and summarize:**
- Total verified/uncertain/suspicious counts
- List suspicious entries with red flags
- Suggest corrections for problematic references

## Manual Spot-Check (Optional)

For quick spot-checks of individual references, Agent can manually query:

```
WebFetch: https://api.crossref.org/works?query.bibliographic=TITLE&rows=5
```

Then compare the returned candidates with the BibTeX entry. But for batch verification, always prefer the Python script.
