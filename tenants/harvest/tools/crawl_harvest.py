"""Tenant-local crawl runner for the Harvest demo.

Runs the stock crawler (ingest.crawl) UNCHANGED and adds, around it, what the
brief asks for and DEMOS.md does not provide:

  * raw HTML of every fetched page       -> tenants/harvest/raw/*.html   (not committed)
  * a fetch log (status, type, bytes, ms) -> tenants/harvest/crawl_log.jsonl
  * per-page language (html lang attr, stopword fallback), publish date
    (trafilatura metadata), word count and a content hash, written as extra
    frontmatter keys — ingest.ingest reads only title/type/url and ignores the rest
  * de-duplication by content hash (duplicates moved to tenants/harvest/dropped/)
  * junk flags for the corpus review (thin, menu-like, repeated boilerplate)
  * CRAWL_REPORT.md: fetched / kept / dropped (+why) / duplicates / tokens

No shared code is modified: `crawl.fetch` is swapped at runtime inside this
process only. Timeout is 15 s here (the stock crawler uses 20 s).

    myenv/bin/python tenants/harvest/tools/crawl_harvest.py
"""

import hashlib
import io
import json
import re
import sys
import time
import urllib.robotparser
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import httpx  # noqa: E402

from ingest import crawl  # noqa: E402

SLUG = "harvest"
SITE = "https://www.harvest.fr"
MAX_PAGES = 300
MAX_DEPTH = 4
DELAY = 1.0
TIMEOUT = 15
TENANT = ROOT / "tenants" / SLUG
RAW, CORPUS, DROPPED = TENANT / "raw", TENANT / "corpus", TENANT / "dropped"
LOG = TENANT / "crawl_log.jsonl"
REPORT = TENANT / "CRAWL_REPORT.md"

# login / account / legal / privacy / cookies / careers (fr + en) + depth > MAX_DEPTH
EXTRA_EXCLUDE = (
    r"/(login|connexion|mon-compte|account|espace-client|espace-clients|"
    r"mentions-legales|legal|cgu|cgv|confidentialite|politique-de-confidentialite|"
    r"donnees-personnelles|rgpd|cookies?|politique-cookies|"
    r"carrieres?|careers?|recrutement|jobs?|nous-rejoindre|offres-d-emploi|offre-d-emploi)(/|$)"
    rf"|^https?://[^/]+(/[^/]+){{{MAX_DEPTH + 1},}}"
)

FR_WORDS = {"le", "la", "les", "des", "une", "est", "et", "pour", "dans", "vous", "nous", "avec", "sur", "pas", "que", "qui", "aux", "votre", "vos", "plus"}
EN_WORDS = {"the", "and", "for", "with", "that", "this", "you", "your", "are", "our", "from", "which", "have", "will", "can", "not", "more", "all", "about", "into"}

fetch_log: list[dict] = []
candidates: dict[str, list[str]] = {}


# ── wrapped fetch: same contract as crawl.fetch, plus raw save + log ─────

def fetch(client: httpx.Client, url: str) -> tuple[int, str, str]:
    t0 = time.time()
    try:
        r = client.get(url, follow_redirects=True, timeout=TIMEOUT)
        ctype = r.headers.get("content-type", "")
        rec = {"url": url, "final_url": str(r.url), "status": r.status_code, "content_type": ctype,
               "bytes": len(r.content), "ms": int((time.time() - t0) * 1000)}
        if r.status_code == 200 and "html" in ctype:
            fname = hashlib.sha1(url.encode()).hexdigest()[:10] + "-" + crawl.slugify(url) + ".html"
            (RAW / fname).write_bytes(r.content)
            rec["raw"] = fname
        fetch_log.append(rec)
        return r.status_code, ctype, r.text
    except Exception as exc:
        fetch_log.append({"url": url, "status": 0, "error": str(exc)[:200], "ms": int((time.time() - t0) * 1000)})
        return 0, "", str(exc)


PRIORITY = ["page-sitemap.xml", "produit-sitemap.xml", "solutions-sitemap.xml",
            "groupe-sitemap.xml", "homepage-sitemap.xml"]  # then post-sitemap by lastmod desc
SKIP_SITEMAPS = re.compile(r"(category|tag|author|attachment|product_cat|taxonom)", re.I)  # same as ingest.crawl


def discover(client: httpx.Client) -> list[dict]:
    """Sitemap index -> [{url, lastmod, sitemap}] for every child sitemap (taxonomies skipped)."""
    status, _, xml = fetch(client, urljoin(SITE, "/sitemap_index.xml"))
    if status != 200:
        sys.exit("sitemap_index.xml not reachable")
    out = []
    for child in re.findall(r"<loc>(.*?)</loc>", xml):
        name = child.rsplit("/", 1)[-1]
        if SKIP_SITEMAPS.search(name):
            continue
        time.sleep(DELAY)
        status, _, body = fetch(client, child)
        if status != 200:
            continue
        for m in re.finditer(r"<url>(.*?)</url>", body, re.S):
            loc = re.search(r"<loc>(.*?)</loc>", m.group(1))
            lm = re.search(r"<lastmod>(.*?)</lastmod>", m.group(1))
            if loc:
                out.append({"url": crawl.normalize(loc.group(1)), "lastmod": lm.group(1)[:10] if lm else "", "sitemap": name})
    return out


def prioritise(cands: list[dict], exclude: re.Pattern, rp) -> list[str]:
    """Site/product/solution/group pages first, then posts newest-first; cap at MAX_PAGES."""
    def ok(c):
        u = c["url"]
        return crawl.same_host(u, SITE) and not exclude.search(u) and (rp is None or rp.can_fetch(crawl.UA, u))
    seen, ordered = set(), []
    for name in PRIORITY:
        for c in cands:
            if c["sitemap"] == name and ok(c) and c["url"] not in seen:
                seen.add(c["url"]); ordered.append(c["url"])
    posts = sorted((c for c in cands if c["sitemap"] not in PRIORITY and ok(c)), key=lambda c: c["lastmod"], reverse=True)
    for c in posts:
        if c["url"] not in seen:
            seen.add(c["url"]); ordered.append(c["url"])
    return ordered[:MAX_PAGES]


class Tee(io.TextIOBase):
    def __init__(self, *streams):
        self.streams = streams

    def write(self, s):
        for st in self.streams:
            st.write(s)
        return len(s)

    def flush(self):
        for st in self.streams:
            st.flush()


# ── post-processing helpers ──────────────────────────────────────────────

def split_frontmatter(text: str) -> tuple[list[str], str]:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return m.group(1).splitlines(), text[m.end():]


def detect_lang(html: str | None, md: str) -> tuple[str, str]:
    if html:
        m = re.search(r"<html[^>]*\blang=[\"']?([a-zA-Z]{2})", html)
        if m:
            return m.group(1).lower(), "html-lang"
    words = re.findall(r"[a-zàâçéèêëîïôûùüÿœ']+", md.lower())
    fr = sum(w in FR_WORDS for w in words)
    en = sum(w in EN_WORDS for w in words)
    if fr == en == 0:
        return "unknown", "stopwords"
    return ("fr" if fr >= en else "en"), "stopwords"


def publish_date(html: str | None, url: str) -> str:
    if not html:
        return ""
    try:
        import trafilatura

        meta = trafilatura.extract_metadata(html, default_url=url)
        return (meta.date or "") if meta else ""
    except Exception:
        return ""


def content_hash(md: str) -> str:
    norm = re.sub(r"\s+", " ", md).strip().lower()
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()[:16]


def main() -> None:
    for d in (RAW, CORPUS, DROPPED):
        d.mkdir(parents=True, exist_ok=True)
    crawl.fetch = fetch
    exclude = re.compile(crawl.DEFAULT_EXCLUDE + "|" + EXTRA_EXCLUDE, re.I)
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(urljoin(SITE, "/robots.txt"))
    try:
        rp.read()
    except Exception:
        rp = None

    t_start = time.time()
    with httpx.Client(headers={"User-Agent": crawl.UA, "Accept": "text/html,application/xhtml+xml"}) as client:
        cands = discover(client)
    candidates["sitemap"] = cands
    ordered = prioritise(cands, exclude, rp)
    urls_file = TENANT / "urls.txt"
    urls_file.write_text("\n".join(ordered) + "\n", encoding="utf-8")
    print(f"{len(cands)} sitemap URLs -> {len(ordered)} to fetch (cap {MAX_PAGES}); list in {urls_file}")

    buf = io.StringIO()
    real_stdout = sys.stdout
    sys.stdout = Tee(real_stdout, buf)
    try:
        crawl.main([
            "--slug", SLUG, "--url", SITE, "--urls", str(urls_file),
            "--max-pages", str(MAX_PAGES), "--delay", str(DELAY),
            "--exclude", EXTRA_EXCLUDE,
        ])
    finally:
        sys.stdout = real_stdout
    elapsed = time.time() - t_start
    crawler_out = buf.getvalue()
    (TENANT / "crawl_stdout.log").write_text(crawler_out, encoding="utf-8")
    LOG.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in fetch_log) + "\n", encoding="utf-8")

    # ── classify every candidate URL ────────────────────────────────────
    raw_by_url = {r["url"]: r for r in fetch_log if r.get("raw")}
    fetched_pages = {r["url"]: r for r in fetch_log if "sitemap" not in r["url"] and "robots" not in r["url"]}
    lastmod = {c["url"]: c["lastmod"] for c in cands}
    in_list = set(ordered)

    written: dict[str, Path] = {}
    for f in sorted(CORPUS.glob("*.md")):
        m = re.search(r"^url: (.+)$", f.read_text(encoding="utf-8"), re.M)
        if m:
            written[m.group(1).strip()] = f

    reasons: dict[str, str] = {}
    cand = list(dict.fromkeys(c["url"] for c in cands))
    other_hosts = []
    for u in cand:
        if not crawl.same_host(u, SITE):
            other_hosts.append(u)
            reasons[u] = "other subdomain (crawler follows the main host only)"
        elif exclude.search(u):
            why = "default exclude" if re.compile(crawl.DEFAULT_EXCLUDE, re.I).search(u) else "brief exclude (login/legal/privacy/cookies/careers/depth>4)"
            if re.search(r"\.pdf$", u, re.I):
                why = "PDF (not supported by the extractor)"
            reasons[u] = why
        elif rp and not rp.can_fetch(crawl.UA, u):
            reasons[u] = "robots.txt disallow"
        elif u in written:
            reasons[u] = "kept"
        elif u in fetched_pages:
            r = fetched_pages[u]
            if r["status"] != 200:
                reasons[u] = f"http {r['status']}" if r["status"] else f"error: {r.get('error', '')[:60]}"
            elif "html" not in r.get("content_type", ""):
                reasons[u] = f"non-HTML ({r.get('content_type', '')[:30]})"
            else:
                reasons[u] = "thin page (< 200 chars of main content)"
        else:
            reasons[u] = f"beyond max-pages cap (older post, lastmod {lastmod.get(u, '?')})" if u not in in_list else "not fetched (unexpected)"

    # ── enrich frontmatter, dedupe, flag ────────────────────────────────
    pages: list[dict] = []
    seen_hash: dict[str, str] = {}
    para_counts: Counter = Counter()
    bodies: dict[Path, tuple[list[str], str]] = {}
    for f in sorted(CORPUS.glob("*.md")):
        fm, body = split_frontmatter(f.read_text(encoding="utf-8"))
        bodies[f] = (fm, body)
        for p in body.split("\n\n"):
            p = p.strip()
            if len(p) > 80:
                para_counts[hashlib.sha1(p.encode()).hexdigest()] += 1

    for f, (fm, body) in bodies.items():
        url = next(l.split(": ", 1)[1].strip() for l in fm if l.startswith("url: "))
        title = json.loads(next(l.split(": ", 1)[1] for l in fm if l.startswith("title: ")))
        rec = raw_by_url.get(url)
        html = (RAW / rec["raw"]).read_text(encoding="utf-8", errors="ignore") if rec else None
        lang, lang_src = detect_lang(html, body)
        pub = publish_date(html, url)
        h = content_hash(body)
        words = len(re.findall(r"\S+", body))
        lines = [l for l in body.splitlines() if l.strip()]
        short_ratio = (sum(len(l.split()) <= 4 for l in lines) / len(lines)) if lines else 1.0
        paras = [p.strip() for p in body.split("\n\n") if len(p.strip()) > 80]
        repeated = sum(para_counts[hashlib.sha1(p.encode()).hexdigest()] >= 3 for p in paras)
        flags = []
        if words < 120:
            flags.append("thin")
        if short_ratio > 0.6:
            flags.append("menu-like")
        if paras and repeated / len(paras) > 0.5:
            flags.append("repeated-boilerplate")
        if h in seen_hash:
            dup_of = seen_hash[h]
            f.rename(DROPPED / f.name)
            reasons[url] = f"duplicate content of {dup_of}"
            pages.append({"file": f.name, "url": url, "title": title, "lang": lang, "words": words, "dup_of": dup_of})
            continue
        seen_hash[h] = url
        extra = [f"lang: {lang}", f"lang_source: {lang_src}", f"content_hash: {h}", f"words: {words}"]
        if pub:
            extra.append(f"published: {pub}")
        f.write_text("---\n" + "\n".join(fm + extra) + "\n---\n" + body, encoding="utf-8")
        pages.append({"file": f.name, "url": url, "title": title, "lang": lang, "lang_src": lang_src,
                      "published": pub, "words": words, "hash": h, "flags": flags})

    kept = [p for p in pages if "dup_of" not in p]
    dups = [p for p in pages if "dup_of" in p]
    total_words = sum(p["words"] for p in kept)
    est_tokens = int(total_words * 1.4)  # rough: French text tokenises ~1.4 tok/word on bge/llama vocabularies

    # PDFs linked from the pages (not crawled)
    pdfs: set[str] = set()
    for rec in raw_by_url.values():
        html = (RAW / rec["raw"]).read_text(encoding="utf-8", errors="ignore")
        for href in re.findall(r"""href=["']([^"']+\.pdf)["']""", html, re.I):
            pdfs.add(urljoin(rec["url"], href))

    # ── report ──────────────────────────────────────────────────────────
    drop_rows = [(u, w) for u, w in reasons.items() if w != "kept"]
    why_counts = Counter(w.split(" of ")[0] if w.startswith("duplicate") else w for _, w in drop_rows)
    lang_counts = Counter(p["lang"] for p in kept)
    lines_out = [
        f"# Crawl report — {SITE} (tenant `{SLUG}`)",
        "",
        f"Crawled on {date.today().isoformat()} with `ingest.crawl` (sitemap discovery, robots.txt respected, "
        f"UA `{crawl.UA}`), delay {DELAY}s, timeout {TIMEOUT}s, max {MAX_PAGES} pages, max depth {MAX_DEPTH}. "
        f"Wall time {elapsed / 60:.1f} min.",
        "",
        "| Metric | Count |", "|---|---|",
        f"| Sitemap candidate URLs | {len(cand)} |",
        f"| Pages fetched (HTTP requests to pages) | {len(fetched_pages)} |",
        f"| Pages kept in corpus | {len(kept)} |",
        f"| Duplicates removed (content hash) | {len(dups)} |",
        f"| Dropped / not fetched (all reasons) | {len(drop_rows)} |",
        f"| Words in kept corpus | {total_words:,} |",
        f"| Estimated tokens (words × 1.4) | {est_tokens:,} |",
        f"| Languages (kept) | {', '.join(f'{k}: {v}' for k, v in lang_counts.most_common())} |",
        "",
        "## Dropped — by reason", "",
        "| Reason | Count |", "|---|---|",
        *[f"| {w} | {n} |" for w, n in why_counts.most_common()],
        "",
        "## Dropped — every URL", "",
        "| URL | Reason |", "|---|---|",
        *[f"| {u} | {w} |" for u, w in sorted(drop_rows, key=lambda x: (x[1], x[0]))],
        "",
        "## PDFs linked from crawled pages (not crawled — unsupported by the extractor)", "",
        *([f"- {p}" for p in sorted(pdfs)] or ["- none found"]),
        "",
        "## Other-host URLs seen in the sitemap", "",
        *([f"- {u}" for u in other_hosts] or ["- none"]),
        "",
        "## Kept pages", "",
        "| # | URL | Title | Lang | Words | Published | Flags |", "|---|---|---|---|---|---|---|",
        *[f"| {i} | {p['url']} | {p['title'][:70]} | {p['lang']} | {p['words']} | {p.get('published') or ''} | {', '.join(p['flags'])} |"
          for i, p in enumerate(kept, 1)],
        "",
    ]
    REPORT.write_text("\n".join(lines_out), encoding="utf-8")
    (TENANT / "pages.json").write_text(json.dumps(pages, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\nreport → {REPORT}\nkept {len(kept)}  dups {len(dups)}  dropped {len(drop_rows)}  ~{est_tokens:,} tokens")


if __name__ == "__main__":
    main()
