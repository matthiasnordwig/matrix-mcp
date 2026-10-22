# Demo: Claude Code with and without Matrix

The same questions over the same documents, answered once by Claude Code alone and once with this plugin.
The documents are public and can be rebuilt by anyone: three EU regulations in their **German** version
and one **English** report whose numbers sit in **charts** (442 pages in total).

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
tokens include cache reads, which make up most of them):

| Question | Config | Correct | Citation right | Ø cost $ | Ø input tokens | Ø output tokens | Ø tool calls | Ø time s |
|---|---|---|---|---|---|---|---|---|
| Q1 paraphrase | A | 2/2 | 2/2 | 0.42 | 381 k | 6.7 k | 14.5 | 86 |
| Q1 paraphrase | B | 2/2 | 2/2 | 0.33 | 187 k | 1.4 k | 6.0 | 26 |
| Q2 chart | A | 2/2 | 2/2 | 0.48 | 585 k | 7.0 k | 19.5 | 109 |
| Q2 chart | B | 1/2 | 1/2 | 0.39 | 407 k | 2.3 k | 11.0 | 51 |
| Q3 three acts | A | 2/2 | 2/2 | 0.93 | 1,279 k | 17.2 k | 37.0 | 245 |
| Q3 three acts | B | 2/2 | 2/2 | 0.57 | 428 k | 4.5 k | 15.5 | 62 |
| Q4 paraphrase | A | 2/2 | 2/2 | 0.29 | 357 k | 4.2 k | 14.5 | 64 |
| Q4 paraphrase | B | 2/2 | 2/2 | 0.30 | 191 k | 1.1 k | 5.5 | 27 |
| **All** | A | 8/8 | 8/8 | 0.53 | | | 21.4 | 126 |
| **All** | B | 7/8 | 7/8 | 0.40 | | | 9.5 | 42 |

The one miss (Q2, B, run 1): the stored chart picture was too small to read the label, and Claude then
tried to render the page with a shell command the test did not allow. The `ask` skill now says to open
such a page with Read; after that change one more B run per question: 4/4 correct with citations,
Ø $0.35 and 33 s.

**Table over the bridge** (`/matrix:table`, 4 rows, one run): Claude found one passage per act, let Matrix
propose the columns, answered the 5 model tasks itself (`llm_tasks` / `llm_answer`) and returned a correct
table with chunk ids — 3 min, $1.53, 25 turns.

## Where Matrix helps and where it does not

In short: **Claude Code alone answered everything correctly too** — `pdftotext` plus Grep over 442 pages
works, and Claude recognises the German terms behind an English question. Matrix did not make the
answers more correct here. What it changed is the effort: **about 3× faster, less than half the tool
calls, a quarter less cost**, and the gap grows with the number of documents a question touches (Q3: 245 s
→ 62 s, $0.93 → $0.57). For a single provision in a single act (Q4) the cost is the same.

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
