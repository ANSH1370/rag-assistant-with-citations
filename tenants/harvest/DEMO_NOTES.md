# Harvest — demo notes

**Prospect:** Harvest Groupe (harvest.fr), French wealth-management software (O2S, Big, Fidnet, MoneyPitch, Quantalys, Plateforme Wealth, KYC, Data, API).
**Audience:** Head of IT / AI leadership. **Demo URL:** https://anshmangukiya.in/demo/harvest
**Content crawled:** 2026-11-03 (www.harvest.fr only; sitemap-driven, robots.txt respected, 1 req/s).

## What is indexed

| | |
|---|---|
| Sitemap URLs considered | 582 (taxonomy sitemaps skipped) |
| Pages fetched / kept after review | 300 / 211 |
| Dropped in review | 59 (events, awards, HR, internal/junk, thin pages) — see CORPUS_REVIEW.md |
| Chunks in Qdrant `demo_harvest` | 832 (bge-small-en-v1.5, header-aware chunking, same as production) |
| Languages of sources | French only (the EN site is www.harvest.eu — out of scope) |
| Oldest / newest page | 2019-11 / 2026-11 (posts newest-first; 281 older posts fell outside the 300-page cap) |

## Quality

- Retrieval hit-rate@4 on the 10-question golden set (5 FR / 5 EN): **90%** (gate 85%).
- Full pipeline: 12/12 — French asked → French answer, English → English, every on-topic answer cited, both off-topic questions (weather, Salesforce) refused.
- Details and every answer: EVAL_RESULTS.md.

## Three best questions to show

1. **FR** — *Comment fonctionne la recherche avec IA dans Fidnet ?* → precise, two sources (Fidnet AI search page + "L'IA arrive dans Fidnet"). Lands well with an AI lead: a RAG assistant describing their own RAG feature.
2. **FR** — *Quelles données financières et ESG propose l'offre Data de Harvest ?* → rich, structured answer (1 600 producers, 250 000 products, DICI/PRIIPS/MIFID II, SFDR, Quantalys ESG Indicator) with two sources.
3. **EN** — *What is the Plateforme Wealth and who is it designed for?* → shows cross-language answering from French sources, cites the product page; good follow-up: *"Is it ISO 27001 certified?"* (cites the certification news page).

Also strong: *Qu'est-ce que l'authentification à deux facteurs sur Harvest Connect ?* (FR, 2FA FAQ) and *Does Harvest provide APIs, and how is access secured?* (EN, OAuth2 from the API page).

## Known gaps (say them before the prospect finds them)

- **Hosting / security question** (*Où sont hébergées les données ?*): now cites the security page but the answer stays generic ("infrastructures sécurisées") and misses the "EU-only, no Cloud Act" fact. A third corpus tweak (variant E in the session log) fixes it offline but was not applied. Prefer the ISO 27001 question for the security angle.
- **Off-topic refusals are English-only**, even for French questions — the refusal text is a shared template (app/prompts.py).
- **All sources are French.** English answers are translations of French pages; the EN site www.harvest.eu and the subdomains formations.harvest.fr / analytics.harvest.fr were not crawled.
- **No contact page on the site** — contact details come from tenant.json (contact@harvest.fr, +33 1 53 30 28 00).
- **Retrieval harness miss:** the French "Qu'est-ce que O2S ?" returns O2S articles rather than the product page (the live pipeline, which rewrites to English, gets it right).
- **PDFs not indexed** (none on harvest.fr itself). Old tax-law posts before late 2019 are not indexed.
- **Infra:** Qdrant free cluster suspends after inactivity (keep the pinger running); the single-request ingest upload timed out twice against the cloud before succeeding — re-run `python -m ingest.ingest --tenant harvest` and check the count if a push fails.

## Re-crawl / update

```bash
myenv/bin/python tenants/harvest/tools/crawl_harvest.py      # re-crawl (report + raw + language/hash frontmatter)
myenv/bin/python -m evals.tenant_eval --tenant harvest       # gate
myenv/bin/python -m ingest.ingest --tenant harvest           # push demo_harvest only
myenv/bin/python tenants/harvest/tools/eval_harvest.py count # verify
```
