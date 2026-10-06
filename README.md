# Chetan Research Lab

**Student:** Ghosh Chetan Devdulal · **Roll / PS:** 5 · **Course:** CE509 Agentic AI Laboratory

**Assignment:** Automated Research Paper Summarizer & Critique System. Agents search literature, summarize papers, extract methodologies, compare results, and generate a critical review.

## Easy Windows setup

1. Install Python 3.10 or newer from https://www.python.org/downloads/ and select **Add Python to PATH**.
2. Extract or copy this entire folder.
3. For PDF support, double-click `setup.bat` once (internet needed to install pypdf). Text, JSON, demo, and analysis work without third-party packages.
4. Double-click `start.bat`. Keep its terminal window open.
5. Open http://127.0.0.1:8001/ in a browser.
6. Click **Load fictional demo**, then **Analyze reading list**.
7. Press Ctrl+C in the terminal to stop.

On macOS/Linux, open a terminal in this folder and run `python3 -m pip install -r requirements.txt`, then `python3 app.py`.

## Using your papers

- Search a topic to retrieve up to eight Crossref journal-article metadata records. Select **Use in editor**. Abstracts are not always available, so provide verified full text when needed. Search requires internet; local analysis does not.
- Import selectable-text PDF or TXT, check the extracted text, enter title/authors/year/DOI, then **Add paper**. Scanned PDFs require OCR outside this project. PDF import is limited to 8 MB and 100 pages; extracted text is capped at 250,000 characters with a warning.
- Import JSON matching `sample.json`: an array of objects with `title`, `authors`, `year`, `doi`, `source_type`, and `text`. Analyze up to ten papers at once.
- Export the completed review as Markdown or JSON. Reports contain source sentence references and side-by-side evidence.

## Agent architecture

Browser → local HTTP service → IngestionAgent → SummaryAgent + MethodologyAgent → CritiqueAgent → ComparisonAgent → review coordinator.

LiteratureAgent searches Crossref through a separate endpoint. Each remaining agent has its own role and returns structured data consumed by downstream agents. The trace is visible in the report.

This implementation uses deterministic extractive NLP and keyword screening, not an LLM or autonomous planning framework. SummaryAgent ranks source sentences by normalized word-frequency score and returns three in source order. MethodologyAgent selects sentences matching methodological, dataset, results, and limitation patterns. CritiqueAgent reports detected mentions of baselines, uncertainty, reproducibility, and validation. ComparisonAgent assembles source excerpts without ranking incompatible metrics. If your instructor specifically requires an LLM agent framework, that is an additional integration beyond this prototype.

## Interpretation and limits

The demo papers and their metrics are fictional. Sentence references refer to the parsed text, not PDF page numbers. Summary quotes are extracted, not verified facts. Keywords can miss synonyms and produce false positives. Missing evidence in an abstract is not evidence that a paper omitted it. A detected reporting signal is not proof of quality. The research-gap section contains follow-up questions, not established scientific gaps. Comparison requires checking dataset, metric, population, and protocol compatibility in the original papers. Multi-column PDF extraction may reorder content. Paper text is data; instructions within papers are never executed.

## Privacy and portability

The server binds only to localhost. Imported text and PDFs are processed in memory and are not saved by the application. Literature queries are sent to Crossref; imported paper text is not. No API keys are required. Send the entire project folder as a ZIP to another person; they need Python and optionally pypdf.

## Tests

```powershell
python -m unittest discover -s tests -v
```

Tests verify source-grounded summaries, result extraction, methodological flags, comparison output, invalid inputs, Markdown export, and mocked metadata parsing. No network is required for tests.

## Files

`app.py`: HTTP server and PDF extraction. `agents.py`: agent pipeline and literature search. `index.html`, `style.css`, `main.js`: UI. `sample.json`: fictional inputs. `requirements.txt`: optional PDF dependency. `setup.bat`, `start.bat`: Windows launchers. `tests/`: automated verification.

Crossref API reference: https://www.crossref.org/documentation/retrieve-metadata/rest-api/
