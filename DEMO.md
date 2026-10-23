# Demo: Claude Code with and without Matrix

The same questions over the same documents, answered once by Claude Code alone and once with this plugin.
The documents are public and can be rebuilt by anyone: three EU regulations in their **German** version
and one **English** report whose numbers sit in **charts** (442 pages in total). The first measurement was made with an earlier version of the plugin (before 0.2.3); a second, larger one
(14 documents, 1,592 pages, four languages, version 0.2.3) follows after it.

| File | Document | Pages | Source (reuse allowed) |
|---|---|---|---|
| `dora.pdf` | Regulation (EU) 2022/2554, digital operational resilience (DORA), German | 79 | EUR-Lex, CELEX 32022R2554 |
| `ai-act.pdf` | Regulation (EU) 2024/1689, AI Act, German | 144 | EUR-Lex, CELEX 32024R1689 |
| `dsgvo.pdf` | Regulation (EU) 2016/679, GDPR (DSGVO), German | 88 | EUR-Lex, CELEX 32016R0679 |
| `enisa-tl-2024.pdf` | ENISA Threat Landscape 2024, English, CC BY 4.0 | 131 | enisa.europa.eu |

## Try it yourself

1. Put the four PDFs into a folder, e.g. `~/Documents/eu-corpus`
   (EUR-Lex: open the CELEX number, choose German, PDF; ENISA: "ENISA Threat Landscape 2024").
2. Install the plugin (see [README](README.md)) and add the folder under **Folders Claude may read**.
3. Start Claude Code anywhere and type:

```
/matrix:index ~/Documents/eu-corpus "EU corpus"
```

Then type the questions, one at a time:

```
/matrix:ask Under the EU rules on digital operational resilience of the financial sector, how often do the larger financial entities have to run advanced testing that simulates real attackers?
/matrix:ask In ENISA's threat landscape report for 2024, which share of the analysed incidents concerned threats against data (breaches, leaks)?
/matrix:ask An incident at a bank affects personal data, a high-risk AI system and the bank's ICT at the same time. What deadlines for reporting to the authorities do the GDPR, the AI Act and DORA each set?
/matrix:ask For how long must the provider of a high-risk AI system keep its technical documentation available for the national authorities?
```

And one table over the documents:

```
/matrix:table For each regulation: which incidents must be reported, to whom, and within which deadline?
```

## The questions and the right answers

Fixed before any run. Pages are PDF pages (1 = first page of the file).

| # | Kind | Right answer | Where |
|---|---|---|---|
| Q1 | English paraphrase of German text ("advanced testing that simulates real attackers" = *bedrohungsorientierte Penetrationstests, TLPT*) | At least every three years; the authority may change the frequency | `dora.pdf` p. 46, Art. 26(1) |
| Q2 | Number only in a chart | 19.01 % (≈ 1.91 K incidents), third after DoS/DDoS (41.1 %) and ransomware (25.79 %) | `enisa-tl-2024.pdf` p. 10 (printed 9), Figure 2 |
| Q3 | Spread over three acts | GDPR: where feasible within 72 hours. AI Act: at the latest 15 days, 2 days (widespread infringement, critical infrastructure), 10 days (death). DORA: no hours in the act — initial, intermediate and final report within limits set by technical standards | `dsgvo.pdf` p. 52 (Art. 33); `ai-act.pdf` p. 101–102 (Art. 73); `dora.pdf` p. 42–43 (Art. 19, 20) |
| Q4 | English paraphrase, single act | Ten years after placing on the market or putting into service | `ai-act.pdf` p. 63, Art. 18(1) |

## How it was measured

- **A — Claude Code alone:** tools `Read`, `Grep`, `Glob`, and `Bash` only for `pdftotext`.
- **B — Claude Code with Matrix:** the same tools plus the plugin (its read tools approved:
  `search_context`, `lookup_exact`, `get_chunks`, `get_page_image`, `list_contexts`, `list_documents`,
  `verify_citations`).
- Same prompt for both: the question, "give a short answer and, for every fact, its source as file name
  and PDF page number; do not answer from memory".
- `claude -p --output-format stream-json --verbose` (final result object = `--output-format json`, plus
  the tool calls), two runs per question and configuration, empty working directory, the PDF folder
  added with `--add-dir`, only project settings. Tokens and cost as Claude Code reports them.
- Indexing runs once before the B runs and is counted separately (it is paid once per folder, not per
  question). The script: `scripts/bench_claude_plugin.py` in the Matrix repository.

## Results

**Indexing (once):** 442 pages → 1,779 passages, 269 s on the development Mac (Apple silicon,
EmbeddingGemma 2 for text and graphics pages).

**Search alone (no Claude, first right page among the top 8 hits):**

| Question | As asked (English) | Worded like the documents |
|---|---|---|
| Q1 | not in top 8 (the English report's keyword hits win) | rank 1 |
| Q2 | rank 1 (the chart page) | rank 1 |
| Q3 | not in top 8 | one query per act: AI Act rank 1, GDPR rank 2, DORA rank 3 |
| Q4 | rank 3 | rank 1 |

**Claude Code A vs. B** (2026-10-22, Claude Code 2.1.222, model Sonnet, 2 runs each; Ø per run; input
tokens include cache reads, which make up most of them; **All** = mean of the four questions):

| Question | Config | Correct | Citation right | Ø input tokens | Ø output tokens | Ø tool calls | Ø time s |
|---|---|---|---|---|---|---|---|
| Q1 paraphrase | A | 2/2 | 2/2 | 381 k | 6.7 k | 14.5 | 86 |
| Q1 paraphrase | B | 2/2 | 2/2 | 187 k | 1.4 k | 6.0 | 26 |
| Q2 chart | A | 2/2 | 2/2 | 585 k | 7.0 k | 19.5 | 109 |
| Q2 chart | B | 1/2 | 1/2 | 407 k | 2.3 k | 11.0 | 51 |
| Q3 three acts | A | 2/2 | 2/2 | 1,279 k | 17.2 k | 37.0 | 245 |
| Q3 three acts | B | 2/2 | 2/2 | 428 k | 4.5 k | 15.5 | 62 |
| Q4 paraphrase | A | 2/2 | 2/2 | 357 k | 4.2 k | 14.5 | 64 |
| Q4 paraphrase | B | 2/2 | 2/2 | 191 k | 1.1 k | 5.5 | 27 |
| **All** | A | 8/8 | 8/8 | 651 k | 8.8 k | 21.4 | 126 |
| **All** | B | 7/8 | 7/8 | 303 k | 2.3 k | 9.5 | 42 |

The one miss (Q2, B, run 1): the stored chart picture was too small to read the label, and Claude then
tried to render the page with a shell command the test did not allow. The `ask` skill now says to open
such a page with Read; after that change one more B run per question: 4/4 correct with citations,
Ø 33 s.

**Table over the bridge** (`/matrix:table`, 4 rows, one run): Claude found one passage per act, let Matrix
propose the columns, answered the 5 model tasks itself (`llm_tasks` / `llm_answer`) and returned a correct
table with chunk ids — 3 min, 25 turns.

## Where Matrix helps and where it does not (first measurement)

In short: **Claude Code alone answered everything correctly too** — `pdftotext` plus Grep over 442 pages
works, and Claude recognises the German terms behind an English question. Matrix did not make the
answers more correct here. What it changed is the effort: **about 3× faster, less than half the tool
calls, less than half the input tokens (Ø 303 k instead of 651 k) and a quarter of the output tokens**, and the gap
grows with the number of documents a question touches (Q3: 245 s → 62 s, 1,279 k → 428 k input tokens). For a single
provision in a single act (Q4) the gap is smallest in absolute terms (64 s → 27 s, 357 k → 191 k input tokens).

- **Wording and language.** Claude mostly searched in English even with the hint to search in the
  documents' language too, and still found the German provisions; it switched to German when the English
  hits missed (Q3). Asked literally in English, the keyword and picture channels pull the English report up,
  so a German query is the safer second try.
- **Charts.** The share in Q2 is not in the text layer at all. Matrix finds the chart page at rank 1;
  reading the value needs a large enough picture (see the miss above). Claude Code alone found it too,
  by rendering PDF pages — with twice the time.
- **Citations.** Every hit carries file, page and section; all correct answers cited the right pages.
- **Cost of entry.** Indexing takes minutes once per folder, and the search model is a one-time download
  of about 1.2 GB. For one short, well-structured document Claude Code alone is just as good.

## Second measurement: 14 documents, 1,592 pages, four languages (version 0.2.3)

The first test is small: 442 pages, so Claude Code alone copes well. This one is larger and mixed, and it measures
two things separately: how well the **search** finds the right place (no Claude involved, 30 questions), and what a
handful of **real questions** cost Claude Code alone and with the plugin.

- **Corpus:** 14 public documents, 1,592 pages — EU acts in German (DORA, AI Act, GDPR, MiCA), English (NIS2),
  French (Data Act) and Spanish (Cyber Resilience Act); NIST publications (SP 800-53 Rev. 5, SP 800-61 Rev. 3,
  CSF 2.0, AI RMF); reports with charts (ENISA Threat Landscape 2024, European Court of Auditors special
  report 05/2022 in German, Eurostat *Schlüsseldaten über Europa* 2018). Indexed once: 5,950 passages and
  408 graphics pages in 16 min on the development Mac.
- **30 questions** of six kinds: worded like the text (5), paraphrased (5), in another language than the
  document (6), value only in a chart (4), answer spread over several documents (4), exception in another
  paragraph than the basic rule (6). Every right place (file, page, article) was read in the document before
  any run and is checked again by the script.
- **Measured:** the question as asked goes to `search_context` (10 hits). Top-k = the first right place is
  among the first k hits; MRR = mean of 1/rank; coverage = share of all right places in the top 10 (below 1
  when the answer needs several documents). Tokens = characters of the result / 4.

### Search, version 0.2.2 → 0.2.3

What changed in 0.2.3: the best passages are put first by a re-ranking model (optional, about 0.6 GB, Apache-2.0,
downloaded once after you agree); each hit carries its outline path (document › chapter › article › paragraph) and
`get_section` reads a whole article; results are excerpts of about 300 characters with hits of one article merged,
instead of whole passages; and the index follows its folder by itself. Measured with the re-ranker installed
(2026-10-23, the question as asked, 10 hits):

| Kind | Questions | Top-1 | Top-5 | Top-10 | MRR | Ø tokens per search |
|---|---|---|---|---|---|---|
| Worded like the text | 5 | 3 → 4 | 5 → 5 | 5 → 5 | 0.80 → 0.90 | 5,846 → 927 |
| Paraphrased | 5 | 3 → 3 | 4 → 4 | 4 → 4 | 0.64 → 0.65 | 5,601 → 1,205 |
| Other language | 6 | 2 → 4 | 3 → 5 | 5 → 5 | 0.43 → 0.72 | 5,831 → 1,226 |
| Value only in a chart | 4 | 3 → 3 | 3 → 4 | 3 → 4 | 0.75 → 0.83 | 4,145 → 1,145 |
| Spread over documents | 4 | 0 → 0 | 1 → 3 | 3 → 3 | 0.19 → 0.33 | 5,594 → 1,213 |
| Exception elsewhere | 6 | 1 → 3 | 3 → 6 | 6 → 6 | 0.39 → 0.71 | 5,789 → 1,240 |
| **All** | **30** | **12 → 17** | **19 → 27** | **26 → 27** | **0.53 → 0.70** | **5,530 → 1,163** |

- **Right place first for 17 of 30 questions (was 12), within the first five for 27 (was 19).** Coverage of all
  right places 0.72 → 0.78. Still not in the top 10: the German ban on social scoring asked in other words, DORA's
  threat-led testing asked in English, and the GDPR + Data Act question on data portability. A question spread
  over several acts still finds one or two of them per search — Claude has to search once per act.
- **A search result shrinks from about 5,500 to about 1,160 tokens** (all 30 together: 166 k → 35 k, minus 79 %).
  The price: the excerpt shows where to look, not what to quote. The exact wording of the right passage stands in
  the excerpts of the first three hits for 14 of 30 questions (23 of 30 in the full passages), so Claude reads
  the passage it cites with `get_chunks` or `get_section`. The whole article of the first hit holds the right
  quote for 16 of 30 questions (24 of 30 within the first three hits); the article of one hit costs about
  1,300 tokens.
- **Without the re-ranker** (nothing downloaded): Top-1/5/10 14 / 20 / 26, MRR 0.58, about 1,190 tokens — the
  smaller results and the outline path alone already lift the first rank a little; the jump in the top five
  (20 → 27) comes from re-ranking, which costs about 4 s per search instead of 56 ms.
- **Caveat:** the same 30 questions were used to choose the number of candidates, the excerpt length and the
  re-ranking model, so the 0.2.3 figures are somewhat optimistic for questions nobody tuned for. 0.2.2 and
  0.2.3 were measured on the same index and the same questions.

### Claude Code alone vs. with the plugin, 4 questions

2026-10-23, Claude Code 2.1.309, model Sonnet, **one run per cell**, working directory = the document folder.
A: tools `Read`, `Grep`, `Glob`, `Bash` (allowed only for `pdftotext`). B: the same plus plugin 0.2.3 with the
re-ranker installed. Same prompt as above (short answer, file name and PDF page for every fact, do not answer
from memory). Input tokens = all rounds including cache reads; rounds = Claude Code turns. One question per kind:
paraphrased, other language, spread over three acts, exception elsewhere. Pages are PDF pages (which here equal the
printed page numbers).

| Question | Config | Answer | Citations (file, page) | Input tokens | Output tokens | Rounds | Time s |
|---|---|---|---|---|---|---|---|
| P4 paraphrased: when may I demand that a company deletes everything it stores about me? (GDPR Art. 17) | A | right | right (43, 44) | 162,857 | 3,829 | 13 | 50 |
| | B | right | one slip: grounds (b)–(f) and paragraph 2 given as p. 43, they are on p. 44 | 94,456 | 1,329 | 5 | 23 |
| C2 other language: how long must the provider of a high-risk AI system keep its technical documentation? (asked in English, text in German) | A | right | right (63) | 186,420 | 3,117 | 13 | 38 |
| | B | right | right (63) | 76,738 | 734 | 4 | 20 |
| S3 spread: highest fines under GDPR, AI Act, NIS2 | A | right | right (83, 115, 60) | 143,510 | 4,237 | 12 | 55 |
| | B | right | one slip: GDPR 20 M tier given as p. 82, it is on p. 83 | 137,539 | 2,220 | 9 | 51 |
| E1 exception: must a company with 50 employees keep a record of processing activities? (GDPR Art. 30(5)) | A | right | right (50, 51) | 121,883 | 2,820 | 11 | 37 |
| | B | right | right (50, 51) | 96,477 | 1,309 | 5 | 23 |
| **All 4** | A | 4/4 | 4/4 | 614,670 | 14,003 | 49 | 180 |
| **All 4** | B | 4/4 | 2/4 pages exact | 405,210 | 5,592 | 23 | 117 |

B against A: 34 % fewer input tokens, 60 % fewer output tokens, less than half the rounds, 35 % less time.

Honest reading:

- **Correctness is the same, the effort is lower, but by less than in the first test** (there: about 3× faster).
  Claude Code alone found every answer in 10 to 12 tool calls with `pdftotext` and Grep; each of these questions
  names a distinctive act and topic, which suits keyword search. Questions without such handles may widen the gap;
  that was not measured.
- **The question spread over three acts gained almost nothing** (143.5 k vs. 137.5 k input tokens, 55 s vs. 51 s):
  Claude searched five times, once per act and wording, which is what the search cannot avoid yet (coverage 0.4
  for this kind above).
- **Citations are where the plugin was worse:** two page numbers were one page off, both with the same cause. A
  hit lists the page on which its passage starts; when a passage runs over a page break, the text of the next page
  is inside it (GDPR Art. 17(1)(b)–(f) and Art. 83(5) both sit at the top of the following page, the hit says
  p. 43 and p. 82). Claude Code alone read the page text itself and had exact pages. Known issue, not fixed in
  0.2.3; file, article and passage were right in every B answer.
- **Not in the table:** indexing (16 min once for this folder), and the one-time downloads (search model about 1.2 GB,
  re-ranking model about 0.6 GB). Indexing costs no Claude tokens. The saving here is roughly 50,000 input tokens per
  question; for a one-off question about a few documents, indexing is not worth it.
- **Sample size:** one run per cell; run-to-run differences of 10–20 % are normal. Three of the four questions (P4,
  C2, S3) were also used while developing 0.2.3; E1 was added for this test.

Rebuild and rerun (from the Matrix repository; `--baseline` compares with an earlier run question by question):

```
python3 scripts/bench_search.py fetch   --corpus DIR
python3 scripts/bench_search.py index   --corpus DIR --bench BENCH --onnx ONNX_DIR --reuse
python3 scripts/bench_search.py measure --bench BENCH --reranker bge-reranker-v2-m3 --baseline BENCH/search-0.2.2.json
```
