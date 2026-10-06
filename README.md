# Chetan Research Paper Analyzer

A local multi-agent application that searches literature, summarizes research papers, extracts methodologies, compares results, and generates a structured critical review.

## Project Details

- **Student:** Ghosh Chetan Devdulal
- **Roll Number / Problem Statement:** 5
- **Course:** CE509 — Agentic AI Laboratory
- **Project:** Automated Research Paper Summarizer & Critique System

## Features

- Search journal-article metadata through Crossref.
- Import selectable-text PDFs, TXT files, or a JSON reading list.
- Generate extractive summaries with source sentence references.
- Identify methodology, datasets, results, and limitations.
- Screen for baseline comparisons, uncertainty reporting, reproducibility, and validation.
- Compare evidence from multiple papers side by side.
- Generate questions for further research and review.
- Export reports in Markdown and JSON formats.
- Run local analysis without API keys.

## Technology Stack

- **Backend:** Python standard-library HTTP server
- **Frontend:** HTML, CSS, and JavaScript
- **PDF Extraction:** pypdf
- **Literature Search:** Crossref REST API
- **Analysis:** Extractive NLP and keyword-based screening

The agents use deterministic rules rather than an LLM. Summaries contain selected source sentences, and critique findings identify reporting signals that require human verification.

## Requirements

- Python 3.10 or newer
- A modern web browser
- Internet access for literature search and initial dependency installation

## Installation and Setup

### Windows

1. Download this repository using **Code → Download ZIP**, then extract it.
2. Install Python and select **Add Python to PATH** during installation.
3. Open the extracted project folder.
4. Double-click `setup.bat` to install the PDF dependency.
5. Double-click `start.bat` to start the application.
6. Open this address in your browser:

   http://127.0.0.1:8001/

Keep the terminal window open while using the application. Press **Ctrl+C** to stop the server.

### Using the Terminal

Open a terminal in the project folder and run:

```bash
python -m pip install -r requirements.txt
python app.py
```

On macOS or Linux, use `python3` instead of `python`.

Text import, JSON import, demo data, and analysis work without additional packages. The `pypdf` dependency is required for PDF import.

## How to Use

### Try the Demo

1. Click **Load fictional demo**.
2. Click **Analyze reading list**.
3. Review the summaries, methodology evidence, comparison table, and critical screening.
4. Export the report using **Markdown** or **JSON**.

The demo papers and their results are fictional.

### Analyze Your Own Paper

1. Click **Read PDF / TXT** and select a paper, or paste its text into the editor.
2. Review the extracted text.
3. Enter the title, authors, year, and optional DOI.
4. Click **Add paper**.
5. Add more papers if you want a comparison.
6. Click **Analyze reading list**.

IEEE papers can be imported when their PDFs contain selectable text. Check extraction carefully because two-column layouts may affect reading order.

### Search Literature

1. Enter a topic in the search field.
2. Click **Search**.
3. Select **Use in editor** for a relevant result.
4. Review the available abstract or add full paper text.
5. Click **Add paper**, then analyze.

Crossref returns metadata and sometimes abstracts. It does not automatically provide every paper’s full text or access to paywalled content.

## Multi-Agent Architecture

```text
LiteratureAgent → Search results → Paper editor
                                      ↓
                              IngestionAgent
                                      ↓
                       SummaryAgent + MethodologyAgent
                                      ↓
                               CritiqueAgent
                                      ↓
                              ComparisonAgent
                                      ↓
                             Review Coordinator
                                      ↓
                            Report and Export
```

| Agent | Responsibility |
|---|---|
| LiteratureAgent | Retrieves journal-article metadata from Crossref |
| IngestionAgent | Validates paper titles, text, and input limits |
| SummaryAgent | Ranks and selects source sentences for summaries |
| MethodologyAgent | Extracts sentences about methods, data, results, and limitations |
| CritiqueAgent | Detects methodological reporting signals and raises review questions |
| ComparisonAgent | Builds a cross-paper evidence matrix |
| Review Coordinator | Assembles the final structured report |

## Input Limits

- Up to **10 papers** per analysis
- At least **80 characters** of text per paper
- Maximum **250,000 characters** per paper
- PDF files up to **8 MB** and **100 pages**
- Scanned PDFs require OCR before importing

PDF extraction exceeding the text limit is truncated with a warning.

## JSON Input Example

Import an array of paper objects:

```json
[
  {
    "title": "Example Research Paper",
    "authors": "Author One, Author Two",
    "year": "2025",
    "doi": "",
    "source_type": "Full-text excerpt",
    "text": "Paste the paper text here. Each paper must contain at least 80 characters of usable text."
  }
]
```

See `sample.json` for a complete demonstration.

## Project Structure

```text
├── app.py              # Local HTTP server and PDF extraction
├── agents.py           # Analysis agents and literature search
├── index.html          # Application interface
├── style.css           # Interface styling
├── main.js             # Browser interactions and report rendering
├── sample.json         # Fictional demonstration papers
├── requirements.txt    # PDF dependency
├── setup.bat           # Windows dependency installer
├── start.bat           # Windows application launcher
├── README.md           # Project documentation
└── tests/
    └── test_agents.py  # Automated agent tests
```

## Running Tests

From the project folder, run:

```bash
python -m unittest discover -s tests -v
```

The tests cover source-grounded summaries, result extraction, critique signals, comparison output, invalid inputs, Markdown export, and metadata parsing.

## Privacy

- The server listens only on `127.0.0.1`.
- Uploaded papers are processed in memory and are not saved by the application.
- Literature search queries are sent to Crossref.
- Imported paper text is not sent to an external AI service.

## Limitations

- This is a deterministic multi-agent prototype, not an LLM-based peer reviewer.
- Keyword rules can miss relevant evidence or detect misleading matches.
- A missing signal in an abstract does not mean it is absent from the full paper.
- A detected mention does not establish methodological quality.
- Sentence references refer to extracted text, not PDF page numbers.
- Results from different datasets or evaluation protocols may not be directly comparable.
- Research questions are suggestions for further review, not verified research gaps.
- Summaries and findings should be checked against the original papers.

## Reference

[Crossref REST API Documentation](https://www.crossref.org/documentation/retrieve-metadata/rest-api/)
