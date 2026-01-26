#!/usr/bin/env python3
"""
RefCheck - BibTeX Reference Verification Script

Verifies academic references against Crossref, OpenAlex, and Semantic Scholar.

Usage:
    python check_references.py --bib references.bib
    python check_references.py --content "@article{key, title={...}}"
    python check_references.py --bib refs.bib --output report.json

Environment Variables:
    SEMANTIC_SCHOLAR_API_KEY - Optional, for enhanced S2 search
"""

import argparse
import json
import os
import re
import sys
import time
import unicodedata
from typing import Any, Dict, List, Optional, Tuple

try:
    import requests
except ImportError:
    print("Error: requests package not installed. Run: pip install requests")
    sys.exit(1)

try:
    from rapidfuzz import fuzz
except ImportError:
    print("Error: rapidfuzz package not installed. Run: pip install rapidfuzz")
    sys.exit(1)


# =============================================================================
# CONFIGURATION
# =============================================================================

TIMEOUT_SEC = 12
MAX_CANDIDATES = 5
MIN_INTERVAL_SEC = 0.25
S2_API_KEY = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")


# =============================================================================
# RATE LIMITER
# =============================================================================

class RateLimiter:
    def __init__(self, min_interval: float = 0.25):
        self.min_interval = min_interval
        self._last = 0.0

    def wait(self):
        now = time.time()
        dt = now - self._last
        if dt < self.min_interval:
            time.sleep(self.min_interval - dt)
        self._last = time.time()


limiter = RateLimiter(MIN_INTERVAL_SEC)


# =============================================================================
# BIBTEX PARSING
# =============================================================================

def parse_bibtex(content: str) -> List[Dict[str, Any]]:
    """Parse BibTeX content into a list of entries."""
    content = content.strip()
    if not content:
        return []

    # Try bibtexparser first
    try:
        import bibtexparser
        from bibtexparser.bparser import BibTexParser
        parser = BibTexParser(common_strings=True)
        db = bibtexparser.loads(content, parser=parser)
        entries = []
        for e in db.entries:
            e2 = {str(k).lower(): v for k, v in e.items()}
            if "id" not in e2 and "ID" in e:
                e2["id"] = e["ID"]
            entries.append(e2)
        return entries
    except Exception:
        pass

    # Fallback parser
    return _fallback_parse(content)


_ENTRY_RE = re.compile(r"@(?P<type>\w+)\s*[{(]\s*(?P<key>[^,]+)\s*,", re.MULTILINE)


def _fallback_parse(content: str) -> List[Dict[str, Any]]:
    """Simple fallback BibTeX parser."""
    entries = []
    i = 0
    n = len(content)
    
    while i < n:
        m = _ENTRY_RE.search(content, i)
        if not m:
            break
        
        entry_type = m.group("type").strip().lower()
        key = m.group("key").strip()
        start = m.end()
        
        open_ch = "{" if "{" in content[m.start():m.end()] else "("
        close_ch = "}" if open_ch == "{" else ")"
        nest = 1
        j = start
        
        while j < n and nest > 0:
            if content[j] == open_ch:
                nest += 1
            elif content[j] == close_ch:
                nest -= 1
            j += 1
        
        body = content[start:j-1].strip()
        fields = _parse_fields(body)
        fields["entrytype"] = entry_type
        fields["id"] = key
        entries.append({k.lower(): v for k, v in fields.items()})
        i = j
    
    return entries


def _parse_fields(body: str) -> Dict[str, Any]:
    """Parse BibTeX fields from entry body."""
    out = {}
    i = 0
    n = len(body)

    def skip_ws():
        nonlocal i
        while i < n and body[i].isspace():
            i += 1

    def parse_name() -> str:
        nonlocal i
        start = i
        while i < n and (body[i].isalnum() or body[i] in "_-:"):
            i += 1
        return body[start:i].strip()

    def parse_value() -> str:
        nonlocal i
        skip_ws()
        if i >= n:
            return ""
        if body[i] == "{":
            i += 1
            nest = 1
            start = i
            while i < n and nest > 0:
                if body[i] == "{":
                    nest += 1
                elif body[i] == "}":
                    nest -= 1
                i += 1
            return body[start:i-1].strip()
        if body[i] == '"':
            i += 1
            start = i
            while i < n and body[i] != '"':
                i += 1
            val = body[start:i].strip()
            i += 1
            return val
        start = i
        while i < n and body[i] not in ",\n\r":
            i += 1
        return body[start:i].strip()

    while i < n:
        skip_ws()
        if i >= n:
            break
        name = parse_name().lower()
        skip_ws()
        if not name:
            break
        if i < n and body[i] == "=":
            i += 1
        skip_ws()
        val = parse_value()
        out[name] = val
        while i < n and body[i] != ",":
            i += 1
        if i < n and body[i] == ",":
            i += 1
    
    return out


# =============================================================================
# NORMALIZATION
# =============================================================================

_LATEX_CMD_RE = re.compile(r"\\[a-zA-Z]+(\*?)")
_BRACES_RE = re.compile(r"[{}]")
_WS_RE = re.compile(r"\s+")
_DOI_PREFIX_RE = re.compile(r"^(https?://(dx\.)?doi\.org/)", re.IGNORECASE)


def safe_str(x: Any) -> str:
    if x is None:
        return ""
    return str(x).strip()


def strip_latex(s: str) -> str:
    s = safe_str(s)
    if not s:
        return ""
    s = s.replace("~", " ")
    s = s.replace("\\&", "&")
    s = s.replace("\\%", "%")
    s = s.replace("\\_", "_")
    s = _LATEX_CMD_RE.sub("", s)
    s = _BRACES_RE.sub("", s)
    s = _WS_RE.sub(" ", s).strip()
    return s


def normalize_text(s: str) -> str:
    s = strip_latex(s)
    s = unicodedata.normalize("NFKC", s)
    s = s.lower().strip()
    s = _WS_RE.sub(" ", s)
    return s


def normalize_doi(doi: str) -> str:
    doi = safe_str(doi)
    doi = _DOI_PREFIX_RE.sub("", doi).strip()
    doi = doi.lower()
    doi = doi.rstrip(" .;,")
    return doi


def first_author_norm(author_field: str) -> str:
    author_field = safe_str(author_field)
    if not author_field:
        return ""
    parts = [p.strip() for p in author_field.split(" and ") if p.strip()]
    if not parts:
        return ""
    a0 = strip_latex(parts[0])
    if "," in a0:
        last = a0.split(",")[0].strip()
    else:
        toks = a0.split()
        last = toks[-1] if toks else a0
    return normalize_text(last)


def year_int(entry: Dict[str, Any]) -> Optional[int]:
    y = safe_str(entry.get("year") or entry.get("date") or "")
    m = re.search(r"(19|20)\d{2}", y)
    if not m:
        return None
    try:
        return int(m.group(0))
    except Exception:
        return None


def normalize_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    e = dict(entry)
    title = safe_str(e.get("title"))
    author = safe_str(e.get("author"))
    doi = safe_str(e.get("doi"))

    e["title_norm"] = normalize_text(title)
    e["first_author_norm"] = first_author_norm(author)
    e["doi_norm"] = normalize_doi(doi) if doi else ""
    e["year_int"] = year_int(e)
    e["venue_raw"] = safe_str(e.get("journal") or e.get("booktitle") or e.get("publisher") or "")

    if "id" not in e:
        e["id"] = safe_str(e.get("citation_key") or e.get("key") or "")
    
    return e


# =============================================================================
# API CLIENTS
# =============================================================================

def api_get(url: str, params: Optional[dict] = None, headers: Optional[dict] = None) -> Dict[str, Any]:
    """Make a GET request with rate limiting."""
    limiter.wait()
    t0 = time.time()
    
    try:
        r = requests.get(url, params=params, headers=headers, timeout=TIMEOUT_SEC)
        elapsed_ms = int((time.time() - t0) * 1000)
        
        if r.status_code == 429:
            return {"ok": False, "status": 429, "error": "Rate limited", "data": None, "elapsed_ms": elapsed_ms}
        
        ok = 200 <= r.status_code < 300
        data = None
        if ok:
            try:
                data = r.json()
            except Exception:
                data = {"text": r.text}
        
        return {"ok": ok, "status": r.status_code, "data": data, "elapsed_ms": elapsed_ms}
    
    except Exception as e:
        elapsed_ms = int((time.time() - t0) * 1000)
        return {"ok": False, "error": f"{type(e).__name__}: {e}", "data": None, "elapsed_ms": elapsed_ms}


def search_crossref(title: str, author: str = "", year: Optional[int] = None) -> Dict[str, Any]:
    """Search Crossref for bibliographic data."""
    url = "https://api.crossref.org/works"
    params = {"query.bibliographic": title, "rows": MAX_CANDIDATES}
    if author:
        params["query.author"] = author
    if year:
        params["filter"] = f"from-pub-date:{year}-01-01,until-pub-date:{year}-12-31"
    return api_get(url, params=params)


def search_openalex(title: str) -> Dict[str, Any]:
    """Search OpenAlex for works."""
    url = "https://api.openalex.org/works"
    params = {"search": title, "per-page": MAX_CANDIDATES}
    return api_get(url, params=params)


def search_semantic_scholar(title: str) -> Dict[str, Any]:
    """Search Semantic Scholar for papers."""
    if not S2_API_KEY:
        return {"ok": False, "disabled": True, "data": None}
    
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": title,
        "limit": MAX_CANDIDATES,
        "fields": "title,year,venue,authors,externalIds,url"
    }
    headers = {"x-api-key": S2_API_KEY, "Accept": "application/json"}
    return api_get(url, params=params, headers=headers)


# =============================================================================
# SCORING
# =============================================================================

def sim_title(a: str, b: str) -> float:
    """Compute title similarity using token sort ratio."""
    a = normalize_text(a)
    b = normalize_text(b)
    if not a or not b:
        return 0.0
    return fuzz.token_sort_ratio(a, b) / 100.0


def author_hit(first_author: str, cand_authors: List[str]) -> Optional[bool]:
    """Check if first author appears in candidate authors."""
    fa = safe_str(first_author)
    if not fa:
        return None
    if not cand_authors:
        return None
    for a in cand_authors[:5]:
        if fa and fa in normalize_text(a):
            return True
    return False


def year_match(bib_year: Optional[int], ref_year: Optional[int], tol: int = 1) -> Optional[bool]:
    """Check if years match within tolerance."""
    if bib_year is None or ref_year is None:
        return None
    return abs(int(bib_year) - int(ref_year)) <= tol


def extract_crossref_fields(item: Dict) -> Tuple[str, Optional[int], str, List[str]]:
    """Extract fields from Crossref result."""
    title = (item.get("title") or [""])[0] if isinstance(item.get("title"), list) else safe_str(item.get("title"))
    year = None
    if "issued" in item and "date-parts" in item["issued"]:
        try:
            year = int(item["issued"]["date-parts"][0][0])
        except Exception:
            pass
    venue = safe_str(item.get("container-title") or "")
    authors = []
    for a in item.get("author", []) or []:
        given = safe_str(a.get("given"))
        family = safe_str(a.get("family"))
        full = (given + " " + family).strip()
        if full:
            authors.append(full)
    return title, year, venue, authors


def extract_openalex_fields(item: Dict) -> Tuple[str, Optional[int], str, List[str]]:
    """Extract fields from OpenAlex result."""
    title = safe_str(item.get("title"))
    year = item.get("publication_year")
    try:
        year = int(year) if year is not None else None
    except Exception:
        year = None
    venue = safe_str((item.get("host_venue") or {}).get("display_name") or "")
    authors = []
    for a in (item.get("authorships") or [])[:8]:
        nm = safe_str((a.get("author") or {}).get("display_name") or "")
        if nm:
            authors.append(nm)
    return title, year, venue, authors


def extract_s2_fields(item: Dict) -> Tuple[str, Optional[int], str, List[str]]:
    """Extract fields from Semantic Scholar result."""
    title = safe_str(item.get("title"))
    year = item.get("year")
    try:
        year = int(year) if year is not None else None
    except Exception:
        year = None
    venue = safe_str(item.get("venue") or "")
    authors = [safe_str(a.get("name")) for a in (item.get("authors") or [])[:8] if safe_str(a.get("name"))]
    return title, year, venue, authors


def score_entry(entry: Dict[str, Any], evidence: Dict[str, Any]) -> Dict[str, Any]:
    """Score a single entry against gathered evidence."""
    key = safe_str(entry.get("id"))
    title = safe_str(entry.get("title") or "")
    fa = safe_str(entry.get("first_author_norm") or "")
    year = entry.get("year_int")
    venue = safe_str(entry.get("venue_raw") or "")
    raw_author = safe_str(entry.get("author") or "")

    best = None
    best_score = -1.0
    best_fields = None

    def consider(source: str, ref_title: str, ref_year: Optional[int], ref_venue: str, ref_authors: List[str]):
        nonlocal best, best_score, best_fields

        st = sim_title(title, ref_title)
        ah = author_hit(fa, ref_authors)
        ym = year_match(year, ref_year, tol=1)

        ah_val = 0.5 if ah is None else (1.0 if ah else 0.0)
        ym_val = 0.5 if ym is None else (1.0 if ym else 0.0)

        if st < 0.60:
            ah_val = 0.5

        s = st * 0.90 + ah_val * 0.05 + ym_val * 0.05

        if s > best_score:
            best_score = s
            best = {
                "source": source,
                "title": ref_title,
                "year": ref_year,
                "venue": ref_venue,
                "authors": ref_authors[:8],
                "sim_title": st,
                "author_hit": ah,
                "year_match": ym,
            }
            best_fields = (ref_title, ref_year, ref_venue, ref_authors, st, ah, ym)

    # Gather candidates from Crossref
    cr = evidence.get("crossref", {})
    if cr.get("ok") and cr.get("data"):
        items = cr["data"].get("message", {}).get("items", []) or []
        for it in items:
            rt, ry, rv, ra = extract_crossref_fields(it)
            if rt:
                consider("crossref", rt, ry, rv, ra)

    # Gather candidates from OpenAlex
    oa = evidence.get("openalex", {})
    if oa.get("ok") and oa.get("data"):
        items = oa["data"].get("results", []) or []
        for it in items:
            rt, ry, rv, ra = extract_openalex_fields(it)
            if rt:
                consider("openalex", rt, ry, rv, ra)

    # Gather candidates from Semantic Scholar
    s2 = evidence.get("semanticscholar", {})
    if s2.get("ok") and s2.get("data"):
        data = s2["data"]
        items = data.get("data", []) if isinstance(data, dict) else []
        for it in items:
            rt, ry, rv, ra = extract_s2_fields(it)
            if rt:
                consider("semanticscholar", rt, ry, rv, ra)

    diff_fields = []
    diff_detail = {}
    suggested = {}

    # No candidates found
    if best is None:
        diff_fields.append("title")
        diff_detail["title"] = {"input": title, "ref": None, "sim": 0.0}

        cr_ok = bool(cr.get("ok", False))
        oa_ok = bool(oa.get("ok", False))
        s2_ok = bool(s2.get("ok", False))

        if cr_ok or oa_ok or s2_ok:
            status = "suspicious"
            red_flags = ["No candidates found (sources reachable)"]
            score_show = 20
        else:
            status = "uncertain"
            red_flags = ["No candidates (all sources unavailable)"]
            score_show = 60

        return {
            "key": key,
            "status": status,
            "score": score_show,
            "input": {"title": title, "year": year, "venue": venue},
            "best_match": None,
            "diff_fields": diff_fields,
            "diff_detail": diff_detail,
            "suggested": suggested,
            "red_flags": red_flags,
        }

    ref_title, ref_year, ref_venue, ref_authors, st, ah, ym = best_fields

    # Check conditions
    title_ok = st >= 0.90
    author_ok = (ah is True)
    year_ok = (ym is True)

    if not title_ok:
        diff_fields.append("title")
        diff_detail["title"] = {"input": title, "ref": ref_title, "sim": round(float(st), 3)}
        suggested["title"] = ref_title

    if ah is False:
        diff_fields.append("author")
        diff_detail["author"] = {"input": raw_author or fa, "ref": ", ".join(ref_authors[:6])}
        suggested["author"] = ", ".join(ref_authors[:6])
    elif ah is None:
        diff_fields.append("author")
        diff_detail["author"] = {"input": raw_author or fa, "ref": ", ".join(ref_authors[:6]), "note": "missing info"}

    if ym is False:
        diff_fields.append("year")
        diff_detail["year"] = {"input": year, "ref": ref_year}
        suggested["year"] = ref_year
    elif ym is None:
        diff_fields.append("year")
        diff_detail["year"] = {"input": year, "ref": ref_year, "note": "missing info"}

    # Determine severity
    title_very_severe = st < 0.55
    title_severe = st < 0.70
    author_severe = (ah is False) and bool(raw_author) and bool(ref_authors)
    year_severe = False
    if year is not None and ref_year is not None:
        try:
            year_severe = abs(int(year) - int(ref_year)) >= 2
        except Exception:
            pass

    severe_cnt = int(title_severe) + int(author_severe) + int(year_severe)

    if title_ok and author_ok and year_ok:
        status = "verified"
    elif title_very_severe:
        status = "suspicious"
    elif severe_cnt >= 2:
        status = "suspicious"
    else:
        status = "uncertain"

    score_show = 90 if status == "verified" else (60 if status == "uncertain" else 20)

    red_flags = []
    if status != "verified":
        if title_severe:
            red_flags.append(f"Title inconsistent (sim={st:.2f})")
        if author_severe:
            red_flags.append("Author mismatch")
        if year_severe:
            red_flags.append(f"Year mismatch (bib={year}, ref={ref_year})")

    return {
        "key": key,
        "status": status,
        "score": score_show,
        "input": {"title": title, "year": year, "venue": venue},
        "best_match": best,
        "diff_fields": diff_fields,
        "diff_detail": diff_detail,
        "suggested": suggested,
        "red_flags": red_flags,
    }


# =============================================================================
# MAIN PIPELINE
# =============================================================================

def verify_references(bib_content: str, verbose: bool = True) -> Dict[str, Any]:
    """Verify all references in BibTeX content."""
    # Parse
    if verbose:
        print("[1/3] Parsing BibTeX...")
    entries = parse_bibtex(bib_content)
    if verbose:
        print(f"      Found {len(entries)} entries")

    # Normalize
    if verbose:
        print("[2/3] Normalizing entries...")
    norm_entries = [normalize_entry(e) for e in entries]

    # Verify
    if verbose:
        print("[3/3] Verifying against databases...")
    results = []

    for idx, entry in enumerate(norm_entries, start=1):
        key = safe_str(entry.get("id"))
        title = safe_str(entry.get("title") or entry.get("title_norm") or "")
        author = safe_str(entry.get("first_author_norm") or "")
        year = entry.get("year_int")

        if verbose:
            print(f"      [{idx}/{len(norm_entries)}] {key[:40]}...")

        # Search databases
        evidence = {
            "crossref": search_crossref(title, author, year),
            "openalex": search_openalex(title),
            "semanticscholar": search_semantic_scholar(title),
        }

        # Score
        scored = score_entry(entry, evidence)
        results.append(scored)

    # Summary
    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    return {
        "summary": {
            "total": len(results),
            "counts": counts,
        },
        "items": results,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Verify BibTeX references against academic databases",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python check_references.py --bib references.bib
  python check_references.py --content "@article{key, title={...}}"
  python check_references.py --bib refs.bib --output report.json

Environment Variables:
  SEMANTIC_SCHOLAR_API_KEY - Optional, for enhanced S2 search
        """
    )
    parser.add_argument("--bib", help="Path to .bib file")
    parser.add_argument("--content", help="Inline BibTeX content")
    parser.add_argument("--output", "-o", help="Output JSON file path")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress progress output")

    args = parser.parse_args()

    if not args.bib and not args.content:
        parser.error("Either --bib or --content is required")

    # Load content
    if args.bib:
        if not os.path.exists(args.bib):
            print(f"Error: File not found: {args.bib}")
            sys.exit(1)
        with open(args.bib, 'r', encoding='utf-8') as f:
            bib_content = f.read()
    else:
        bib_content = args.content

    # Verify
    result = verify_references(bib_content, verbose=not args.quiet)

    # Output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\nResult saved to: {args.output}")
    else:
        print("\n" + "=" * 60)
        print("VERIFICATION RESULT")
        print("=" * 60)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    # Summary
    print("\n" + "=" * 60)
    print(f"Total: {result['summary']['total']}")
    for status, count in result['summary']['counts'].items():
        print(f"  {status}: {count}")
    print("=" * 60)


if __name__ == "__main__":
    main()
