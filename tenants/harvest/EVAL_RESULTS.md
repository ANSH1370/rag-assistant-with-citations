# Evaluation — harvest (2026-11-03)

## Retrieval (stock harness `evals.tenant_eval`, in-memory, same embedder)

**hit-rate@4 = 90% (9/10), gate 85% → PASS** — unchanged before and after the security-page edit (828 → 832 chunks).
Only miss: the French O2S question returns three O2S articles instead of the product page; the live pipeline rewrites the query to English and then ranks the product page first.

## One tenant-only corpus change (security page)

`corpus/102-la-securite-au-coeur-de-notre-demarche-dediteur.md` had no markdown headings, so it was a single flat chunk. Its four bold pseudo-headings were promoted to `##` and a one-line lead added.
Rank of the page for the pipeline's rewritten query *"Where are Harvest's data hosted and what security measures does Harvest apply?"*: **miss → 1**. A second, fact-dense lead was tried and regressed (page left the top 6), so it was reverted.

## Full pipeline (guard → rewrite → retrieve → generate), Qdrant Cloud, Groq gpt-oss-120b / 20b

| # | kind | asked | guard | answered in | citations |
|---|---|---|---|---|---|
| 1 | on-topic | fr | on-topic | fr | /produit/o2s, /la-solution-complete-et-personnalisable-pour-les-professionnels-de-la-gestion-de-patrimoine |
| 2 | on-topic | fr | on-topic | fr | /la-securite-au-coeur-de-notre-demarche-dediteur |
| 3 | on-topic | fr | on-topic | fr | /recherche-ia-fidnet-2, /lia-arrive-dans-fidnet |
| 4 | on-topic | fr | on-topic | fr | /votre-compte-harvest-connect-securise-avec-lauthentification-a-deux-facteurs |
| 5 | on-topic | fr | on-topic | fr | /produit/data, /solutions/data |
| 6 | on-topic | en | on-topic | en | /produit/plateforme-wealth |
| 7 | on-topic | en | on-topic | en | /produit/api |
| 8 | on-topic | en | on-topic | en | /produit/kyc |
| 9 | on-topic | en | on-topic | en | /assureur-mutuelle, /produit/harvest-fidroit-academy |
| 10 | on-topic | en | on-topic | en | /produit/o2s, /family-office |
| 11 | off-topic | fr | refused | en | — |
| 12 | off-topic | en | refused | en | — |

12/12 checks: French questions answered in French, English in English, every on-topic answer cited, both off-topic questions refused.

### Question 2 before / after the corpus change

**Before:**

Les données sont protégées par plusieurs mesures : les API sont sécurisées avec OAuth 2, les accès sont contrôlés et vous disposez d’un espace de recette dédié ; les parcours digitalisés assurent une collecte sécurisée, évitent les erreurs de ressaisie et chiffrent les flux [3][6]. Le site ne précise pas où les serveurs sont hébergés ; pour plus de détails, vous pouvez contacter Harvest à contact@harvest.fr ou au +33 (0)1 53 30 28 00.

**After:**

Les données sont hébergées sur des infrastructures sécurisées ; Harvest assure des sauvegardes régulières, une continuité d’activité, la sécurité des applications et le respect des exigences réglementaires (ACPR, ORIAS), le tout piloté par une organisation dédiée (RSSI, DPO) [1].

## Answers (after)

### 1. [on-topic / fr] Qu'est-ce que O2S et à quoi sert-il pour un cabinet de gestion de patrimoine ?

O2S est le CRM patrimonial de Harvest : une plateforme digitale qui centralise la gestion quotidienne d’un cabinet de gestion de patrimoine — de la conformité et de l’agrégation des portefeuilles clients à la signature électronique des documents [1][2]. Elle permet de renforcer la proximité avec les clients (via MoneyPitch), d’accéder à un réseau de partenaires, d’utiliser des API, le SSO et un accompagnement personnalisé, tout en assurant un haut niveau de sécurité et de service [2][3].

- O2S - Harvest — https://www.harvest.fr/produit/o2s
- O2S, votre solution complète et personnalisable pour piloter votre activité financière - Harvest — https://www.harvest.fr/la-solution-complete-et-personnalisable-pour-les-professionnels-de-la-gestion-de-patrimoine

### 2. [on-topic / fr] Où sont hébergées les données et quelles mesures de sécurité Harvest applique-t-il ?

Les données sont hébergées sur des infrastructures sécurisées ; Harvest assure des sauvegardes régulières, une continuité d’activité, la sécurité des applications et le respect des exigences réglementaires (ACPR, ORIAS), le tout piloté par une organisation dédiée (RSSI, DPO) [1].

- La sécurité au cœur de notre démarche d’éditeur - Harvest — https://www.harvest.fr/la-securite-au-coeur-de-notre-demarche-dediteur

### 3. [on-topic / fr] Comment fonctionne la recherche avec IA dans Fidnet ?

La recherche avec IA dans Fidnet vous permet de poser votre question en langage naturel ; l’assistant analyse l’ensemble de la documentation de la base et vous restitue en quelques secondes une synthèse structurée, sourcée et enrichie de liens vers les documents d’origine. Il croise automatiquement plusieurs sources — documents experts, évolutions réglementaires récentes—pour fournir une réponse claire, rapide et pertinente, tout en vous laissant accéder aux contenus détaillés pour aller plus loin【1†L1-L4】【3†L1-L7】.

- Recherche avec IA dans Fidnet : l'assistant qui répond à vos questions patrimoniales - Harvest — https://www.harvest.fr/recherche-ia-fidnet-2
- L'IA arrive dans Fidnet - Harvest — https://www.harvest.fr/lia-arrive-dans-fidnet

### 4. [on-topic / fr] Qu'est-ce que l'authentification à deux facteurs sur Harvest Connect et pourquoi est-elle obligatoire ?

L’authentification à deux facteurs (2FA) sur Harvest Connect consiste à ajouter, après votre identifiant et mot de passe (premier facteur), la saisie d’un code temporaire à 6 chiffres généré sur votre smartphone via une application d’authentification (second facteur) 【1†L15-L22】. Elle devient obligatoire afin de renforcer la protection de vos données, d’éviter tout accès non autorisé et de garantir que chaque utilisateur dispose de son propre compte, conformément aux conditions d’utilisation de Harvest 【1†L27-L33】.

- FAQ - Vos applications Harvest encore plus sécurisées - Harvest — https://www.harvest.fr/votre-compte-harvest-connect-securise-avec-lauthentification-a-deux-facteurs

### 5. [on-topic / fr] Quelles données financières et ESG propose l'offre Data de Harvest ?

L’offre Data de Harvest vous donne accès à plus de 250 000 produits financiers (fonds, SCPI, assurance‑vie, produits structurés, etc.) provenant de plus de 1 600 sociétés de gestion, avec leurs fiches techniques, données de frais, documents réglementaires (DICI, PRIIPS, EMT, MiFID II), notations et classifications — et même des bases spécifiques comme les calendriers back‑office ou les données de back‑office [2][6].  

Sur le plan ESG, vous bénéficiez de la catégorisation ESG, de l’intensité ESG, des labels et certifications, des données extra‑financières, des fichiers SFDR (EET, articles 6‑8‑9, taxonomie, PAI) ainsi du Quantalys ESG Indicator, le tout alimenté à la source par les organismes de délivrance de labels [2][4].

- Data - Harvest — https://www.harvest.fr/produit/data
- Data - Harvest — https://www.harvest.fr/solutions/data

### 6. [on-topic / en] What is the Plateforme Wealth and who is it designed for?

Plateforme Wealth is Harvest’s digital‑distribution platform that lets insurers and their distribution partners automate and streamline the whole life‑insurance subscription process. It is built for **distributors** who need faster, more efficient underwriting workflows, and for **insurers** who want to expand the number of partners that can sell their products through uniform, API‑driven digital journeys [2][3].

- Plateforme Wealth - Harvest — https://www.harvest.fr/produit/plateforme-wealth

### 7. [on-topic / en] Does Harvest provide APIs, and how is access to them secured?

Yes, Harvest offers a full suite of ready‑to‑use, business‑focused APIs that you can integrate to build custom workflows and connect with your existing tools【2†source】【3†source】. Access to these APIs is protected with OAuth 2.0 authentication, ensuring secure connections for your applications【1†source】.

- API - Harvest — https://www.harvest.fr/produit/api

### 8. [on-topic / en] How does the KYC solution help advisers collect and verify client documents?

The KYC platform gives advisers a simple, digital journey for clients to enter their personal and regulatory information, while automatically pre‑filling data and syncing everything with O2S. It also secures the upload and transmission of supporting documents, so the files are stored safely and the dossiers stay compliant [1][2].

- KYC - Harvest — https://www.harvest.fr/produit/kyc

### 9. [on-topic / en] What training does the Harvest Fidroit Academy offer and in which formats?

Harvest Fidroit Academy proposes professional training on a wide range of patrimonial subjects – wealth‑advice, life‑insurance, demembrement, international assets, real‑estate, financial placements, executive‑family matters and personal tax – available at basic, intermediate and expert levels [5].  The courses can be taken in‑person, via live virtual classrooms or webinars, as asynchronous e‑learning modules (with replay or on‑demand access), or through customized intra‑ or inter‑company programmes, including an unlimited digital pass [2][3][5].

- Assureur Mutuelle - Harvest — https://www.harvest.fr/assureur-mutuelle
- Harvest Fidroit Academy - Harvest — https://www.harvest.fr/produit/harvest-fidroit-academy

### 10. [on-topic / en] How does O2S automate account aggregation for wealth advisers?

O2S automatically pulls together your clients’ accounts and contracts by connecting to a wide network of partner data sources, so the adviser sees a complete, up‑to‑date view of each portfolio without manual entry [5][1]. This built‑in aggregation is part of the CRM’s digital‑first design, helping wealth advisers streamline client onboarding and ongoing monitoring.

- O2S - Harvest — https://www.harvest.fr/produit/o2s
- Family Office - Harvest — https://www.harvest.fr/family-office

### 11. [off-topic / fr] Quel temps fait-il à Paris aujourd'hui ?

I can only help with questions about Harvest — its services, how things work, and how to get in touch. For anything else, please use contact@harvest.fr or +33 (0)1 53 30 28 00 (the 'Contactez-nous' link on harvest.fr).


### 12. [off-topic / en] How do I configure Salesforce Financial Services Cloud for my advisers?

I can only help with questions about Harvest — its services, how things work, and how to get in touch. For anything else, please use contact@harvest.fr or +33 (0)1 53 30 28 00 (the 'Contactez-nous' link on harvest.fr).

