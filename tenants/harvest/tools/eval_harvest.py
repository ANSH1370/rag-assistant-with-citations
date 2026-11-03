"""Tenant-local evaluation helpers for the Harvest demo (no shared code changed).

    myenv/bin/python tenants/harvest/tools/eval_harvest.py retrieval   # hit-rate@4 + retrieved URLs on every miss (local, in-memory)
    myenv/bin/python tenants/harvest/tools/eval_harvest.py count       # Qdrant collection count vs expected chunk count
    myenv/bin/python tenants/harvest/tools/eval_harvest.py pipeline    # guard → rewrite → retrieve → generate on golden + off-topic

`retrieval` mirrors evals/tenant_eval.py (same embedder, same K, same gate) but
prints URLs instead of title::section so a miss can be diagnosed. `pipeline`
needs the tenant ingested (QDRANT_URL in .env) and GROQ_API_KEY.
"""

import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

SLUG = "harvest"
TENANT = ROOT / "tenants" / SLUG
K, GATE = 4, 0.85
PACE_S, BACKOFF_S = 20, 30

FR = {"le", "la", "les", "des", "une", "est", "et", "pour", "dans", "vous", "nous", "avec", "sur", "pas", "que", "qui", "aux", "votre", "vos", "plus", "un", "du", "de"}
EN = {"the", "and", "for", "with", "that", "this", "you", "your", "are", "our", "from", "which", "have", "will", "can", "not", "more", "all", "about", "it", "is", "of"}


def lang_of(text: str) -> str:
    words = re.findall(r"[a-zàâçéèêëîïôûùüÿœ']+", text.lower())
    fr, en = sum(w in FR for w in words), sum(w in EN for w in words)
    return "fr" if fr > en else "en" if en > fr else "?"


def load(name: str) -> list[dict]:
    p = TENANT / name
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []


def retrieval() -> None:
    from fastembed import TextEmbedding
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, PointStruct, VectorParams

    from app.config import settings
    from app.tenants import get_tenant
    from ingest.ingest import load_chunks

    golden = load("golden.jsonl")
    t = get_tenant(SLUG)
    chunks = load_chunks(t.corpus_dir)
    emb = TextEmbedding(settings.embed_model, cache_dir=settings.embed_cache_dir)
    vecs = list(emb.embed([c.text for c in chunks]))
    cl = QdrantClient(":memory:")
    cl.create_collection("eval", vectors_config=VectorParams(size=len(vecs[0]), distance=Distance.COSINE))
    cl.upsert("eval", points=[PointStruct(id=i, vector=v.tolist(), payload={"url": c.url, "title": c.title, "section": c.section})
                              for i, (c, v) in enumerate(zip(chunks, vecs))])
    hits, rows = 0, []
    for g in golden:
        qv = list(emb.query_embed(g["q"]))[0]
        res = cl.query_points("eval", query=qv.tolist(), limit=K, with_payload=True).points
        urls = [p.payload["url"] for p in res]
        rank = next((i + 1 for i, u in enumerate(urls) if g["expect_url_contains"] in u), None)
        hits += rank is not None
        rows.append((g, rank, [(p.payload["url"], p.payload["section"], round(p.score, 3)) for p in res]))
    rate = hits / len(golden)
    print(f"\n{SLUG}: retrieval hit-rate@{K} = {rate:.0%} ({hits}/{len(golden)})  gate {GATE:.0%} → {'PASS' if rate >= GATE else 'FAIL'}\n")
    print("| # | lang | question | expected | rank |")
    print("|---|---|---|---|---|")
    for i, (g, rank, _) in enumerate(rows, 1):
        print(f"| {i} | {g.get('lang', '?')} | {g['q']} | …{g['expect_url_contains']} | {rank or 'MISS'} |")
    for i, (g, rank, got) in enumerate(rows, 1):
        if rank is None:
            print(f"\nMISS #{i}: {g['q']!r}  (expected …{g['expect_url_contains']})")
            for u, s, sc in got:
                print(f"    {sc}  {u}  [{s[:50]}]")
    sys.exit(0 if rate >= GATE else 1)


def count() -> None:
    from app.tenants import get_tenant
    from ingest.ingest import get_client, load_chunks

    t = get_tenant(SLUG)
    expected = len(load_chunks(t.corpus_dir))
    cl = get_client()
    try:
        exists = cl.collection_exists(t.collection)
        n = cl.count(t.collection, exact=True).count if exists else None
        print(f"collection {t.collection!r}: exists={exists} count={n} expected={expected} → {'OK' if n == expected else 'MISMATCH'}")
        print("all collections:", sorted(c.name for c in cl.get_collections().collections))
    finally:
        cl.close()


def pipeline_run() -> None:
    from app.graph import pipeline

    items = [dict(g, kind="on-topic") for g in load("golden.jsonl")] + [dict(g, kind="off-topic") for g in load("offtopic.jsonl")]
    results = []
    for i, g in enumerate(items, 1):
        # Groq free tier: 8k tokens/min on the 120b model → pace the questions and back off on 429.
        if i > 1:
            time.sleep(PACE_S)
        for attempt in range(5):
            try:
                st = pipeline.invoke({"tenant": SLUG, "question": g["q"], "history": []})
                break
            except RuntimeError as exc:
                if "429" not in str(exc) or attempt == 4:
                    raise
                print(f"[rate-limited, waiting {BACKOFF_S}s]")
                time.sleep(BACKOFF_S)
        ans, cits = st["answer"], st.get("citations", [])
        refused = not st.get("on_topic", True)
        alang = lang_of(ans)
        ok = (refused and not cits) if g["kind"] == "off-topic" else (bool(cits) and alang == g.get("lang", alang))
        results.append({"n": i, "kind": g["kind"], "lang": g.get("lang"), "q": g["q"], "answer": ans, "answer_lang": alang,
                        "refused": refused, "citations": cits, "ok": ok})
        print(f"\n### {i}. [{g['kind']} / {g.get('lang', '-')}] {g['q']}")
        print(f"**guard:** {'REFUSED' if refused else 'on-topic'}   **answer language:** {alang}   **check:** {'✓' if ok else '✗'}")
        print(f"\n{ans}\n")
        for c in cits:
            print(f"- {c['title']} — {c['url']}")
    (TENANT / "pipeline_results.json").write_text(json.dumps(results, indent=1, ensure_ascii=False), encoding="utf-8")
    passed = sum(r["ok"] for r in results)
    print(f"\n{passed}/{len(results)} checks passed → {TENANT / 'pipeline_results.json'}")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "retrieval"
    {"retrieval": retrieval, "count": count, "pipeline": pipeline_run}[mode]()
