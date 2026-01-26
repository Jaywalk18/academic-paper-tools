# RefCheck Technical Reference

## Verification Algorithm

### 1. BibTeX Parsing

The system uses `bibtexparser` library with fallback to a custom regex-based parser.

**Extracted fields:**
- `title` - Paper title
- `author` - Author list (BibTeX format: "Last1, First1 and Last2, First2")
- `year` - Publication year
- `doi` - Digital Object Identifier (if available)
- `journal` / `booktitle` - Venue

### 2. Normalization

**Title normalization:**
- Remove LaTeX commands (`\textbf{}`, `\emph{}`, etc.)
- Remove braces
- Lowercase
- Collapse whitespace
- Unicode NFKC normalization

**Author normalization:**
- Split by " and "
- Extract first author's last name
- Normalize text

**DOI normalization:**
- Remove URL prefix (`https://doi.org/`)
- Lowercase
- Remove trailing punctuation

### 3. Database Queries

#### Crossref
- **Endpoint:** `https://api.crossref.org/works`
- **Parameters:** `query.bibliographic`, `query.author`, `filter` (year)
- **Rate limit:** Polite pool (no key required)

#### OpenAlex
- **Endpoint:** `https://api.openalex.org/works`
- **Parameters:** `search`, `per-page`
- **Rate limit:** 100,000/day (no key required)

#### Semantic Scholar
- **Endpoint:** `https://api.semanticscholar.org/graph/v1/paper/search`
- **Parameters:** `query`, `limit`, `fields`
- **Rate limit:** 100/5min without key, higher with API key

### 4. Scoring Algorithm

#### Title Similarity
Uses `rapidfuzz.fuzz.token_sort_ratio`:
- Tokenizes both strings
- Sorts tokens alphabetically
- Computes ratio (0-100, divided by 100)

#### Author Hit
Checks if normalized first author appears in any candidate author name (substring match within first 5 authors).

#### Year Match
Checks if years are within tolerance (default: ±1 year).

### 5. Status Classification

```
IF title_sim >= 0.90 AND author_hit AND year_match:
    status = "verified"
ELIF title_sim < 0.55:
    status = "suspicious"
ELIF severe_count >= 2:
    status = "suspicious"
ELSE:
    status = "uncertain"
```

**Severe criteria:**
- `title_severe`: title_sim < 0.70
- `author_severe`: author_hit == False AND both have author info
- `year_severe`: year difference >= 2

## Error Handling

### No Candidates Found
If all sources return no matching candidates:
- If sources were reachable → `suspicious` (reference may be fabricated)
- If all sources failed → `uncertain` (network issue)

### API Errors
- Rate limiting (429): Automatic retry with exponential backoff
- Timeout: Returns partial results
- Server errors: Skips source, continues with others

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `timeout_sec` | 12 | HTTP request timeout |
| `max_candidates` | 5 | Max candidates per source |
| `per_source_min_interval_sec` | 0.25 | Rate limit between requests |

## Output Fields

### Per-Entry Result

| Field | Type | Description |
|-------|------|-------------|
| `key` | string | BibTeX citation key |
| `status` | string | verified/uncertain/suspicious |
| `score` | int | Display score (90/60/20) |
| `input` | object | Original BibTeX data |
| `best_match` | object | Best matching candidate |
| `diff_fields` | array | Fields with mismatches |
| `diff_detail` | object | Detailed mismatch info |
| `suggested` | object | Suggested corrections |
| `red_flags` | array | Warning messages |

### Best Match Object

| Field | Type | Description |
|-------|------|-------------|
| `source` | string | crossref_search/openalex/semanticscholar |
| `title` | string | Reference title |
| `year` | int | Publication year |
| `venue` | string | Journal/conference name |
| `authors` | array | Author names |
| `sim_title` | float | Title similarity score |
| `author_hit` | bool/null | Author match result |
| `year_match` | bool/null | Year match result |
