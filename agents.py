"""Auditable, extractive research agents. No claims are generated as facts."""
import re
from collections import Counter
import html
import json
from urllib.request import Request, urlopen
from urllib.parse import urlencode

STOP = set('the a an and or of to in is are was were this that for with on as by we our from it be has have at not using study results'.split())

def sentences(text):
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+|\n+', text) if len(s.strip()) > 20]

def words(text):
    return [w for w in re.findall(r'[a-z]{3,}', text.lower()) if w not in STOP]

class LiteratureAgent:
    def run(self, query):
        if not isinstance(query, str) or not 3 <= len(query.strip()) <= 200:
            raise ValueError('Enter a search topic between 3 and 200 characters.')
        url = 'https://api.crossref.org/works?' + urlencode({'query': query, 'rows': 8, 'filter': 'type:journal-article'})
        req = Request(url, headers={'User-Agent': 'ChetanResearchLab/1.0 (educational local prototype)'})
        with urlopen(req, timeout=20) as response:
            payload = json.load(response)
        papers = []
        for item in payload['message']['items']:
            abstract = html.unescape(re.sub(r'<[^>]+>', ' ', item.get('abstract', '')))
            parts = item.get('published', {}).get('date-parts', [[]])[0]
            papers.append({'title': (item.get('title') or ['Untitled'])[0], 'authors': ', '.join(' '.join([a.get('given', ''), a.get('family', '')]).strip() for a in item.get('author', [])[:6]), 'year': str(parts[0]) if parts else '', 'doi': item.get('DOI', ''), 'text': abstract.strip(), 'source_type': 'Crossref abstract'})
        return papers

class IngestionAgent:
    def run(self, papers):
        if not isinstance(papers, list) or not 1 <= len(papers) <= 10:
            raise ValueError('Add between 1 and 10 papers.')
        out = []
        for i, p in enumerate(papers):
            if not isinstance(p, dict):
                raise ValueError('Each paper must be an object.')
            title, text = str(p.get('title', '')).strip(), str(p.get('text', '')).strip()
            if not title or len(text) < 80:
                raise ValueError(f'Paper {i+1}: add a title and at least 80 characters of paper text. Metadata alone cannot be analyzed.')
            if len(text) > 250000:
                raise ValueError('Limit each paper to 250,000 characters.')
            out.append({k: str(p.get(k, '')) for k in ('title', 'authors', 'year', 'doi', 'source_type')} | {'id': f'P{i+1}', 'text': text})
        return out

class SummaryAgent:
    def run(self, p):
        ss = sentences(p['text'])
        counts = Counter(words(p['text']))
        ranked = sorted(enumerate(ss), key=lambda pair: sum(counts[w] for w in words(pair[1])) / max(1, len(words(pair[1]))), reverse=True)[:3]
        summary = [{'sentence': i+1, 'quote': s} for i, s in sorted(ranked)]
        return {'summary': summary, 'keywords': [w for w, _ in counts.most_common(6)]}

class MethodologyAgent:
    PATTERNS = {'method': r'\b(method|propos|model|algorithm|randomiz|interview|survey|experiment|train|design)', 'data': r'\b(dataset|data set|sample|participants|patients|corpus|benchmark|observations)\b', 'results': r'\b(result|achiev|accuracy|precision|recall|f1|improv|outperform|significant|auc)', 'limitations': r'\b(limit|future work|bias|small sample|generaliz|threats to validity)'}
    def run(self, p):
        ss = sentences(p['text'])
        return {key: [{'sentence': i+1, 'quote': s} for i, s in enumerate(ss) if re.search(pattern, s, re.I)][:3] for key, pattern in self.PATTERNS.items()}

class CritiqueAgent:
    def run(self, p, evidence):
        checks = {'baseline comparison': r'\b(baseline|control group|compared with|compared to)\b', 'uncertainty reporting': r'\b(confidence interval|standard deviation|p-value|error bar|variance)\b', 'reproducibility details': r'\b(source code|github|hyperparameter|random seed|code available)\b', 'external validation': r'\b(external validation|independent dataset|held.out|cross.validation)\b'}
        ss = sentences(p['text'])
        checklist = []
        for label, pattern in checks.items():
            hits = [{'sentence': i+1, 'quote': s} for i, s in enumerate(ss) if re.search(pattern, s, re.I)][:2]
            checklist.append({'criterion': label, 'status': 'Mention detected; verify adequacy' if hits else 'Not detected in supplied text', 'evidence': hits})
        questions = [f"Check {c['criterion']} in the full paper and supplementary material." for c in checklist if not c['evidence']]
        if not evidence['limitations']:
            questions.append('Review author-stated limitations; none were detected in this excerpt.')
        return {'checklist': checklist, 'questions': questions, 'scope': 'Keyword screening of supplied text. A detected mention is not proof of methodological quality, and absence in an excerpt is not absence in the paper.'}

class ComparisonAgent:
    def run(self, papers):
        rows = [{'id': p['id'], 'title': p['title'], 'method': p['evidence']['method'], 'data': p['evidence']['data'], 'results': p['evidence']['results']} for p in papers]
        common = set(papers[0]['keywords'])
        for p in papers[1:]:
            common &= set(p['keywords'])
        return {'rows': rows, 'common_keywords': sorted(common), 'caution': 'Results are quoted side by side, not ranked. Different datasets, metrics, splits, and evaluation protocols may prevent direct comparison.'}

def analyze(papers):
    clean = IngestionAgent().run(papers)
    result = []
    for p in clean:
        evidence = MethodologyAgent().run(p)
        result.append({k: v for k, v in p.items() if k != 'text'} | SummaryAgent().run(p) | {'evidence': evidence, 'critique': CritiqueAgent().run(p, evidence), 'sentence_count': len(sentences(p['text']))})
    comparison = ComparisonAgent().run(result)
    return {'papers': result, 'comparison': comparison, 'review': {'overview': f'Analyzed {len(result)} supplied papers/excerpts using extractive evidence and methodological screening.', 'research_gaps_to_verify': list(dict.fromkeys(q for p in result for q in p['critique']['questions'])), 'limitations': 'This is a deterministic multi-agent prototype, not an LLM peer reviewer. Summaries are selected source sentences. Screening questions are hypotheses for further review, not established research gaps. Verify every quote against the original paper; PDF extraction can reorder columns.'}, 'trace': ['IngestionAgent: validated paper inputs', 'SummaryAgent: selected source sentences', 'MethodologyAgent: extracted method, data, results, limitations', 'CritiqueAgent: assessed reporting signals', 'ComparisonAgent: assembled evidence matrix', 'Review coordinator: assembled critical review']}

def markdown(report):
    lines = ['# Research review', '', report['review']['overview']]
    for p in report['papers']:
        lines += ['', f"## [{p['id']}] {p['title']}", f"Authors: {p['authors']} | Year: {p['year']} | DOI: {p['doi']}", '', '### Extractive summary']
        lines += [f"- [{p['id']}, sentence {q['sentence']}] {q['quote']}" for q in p['summary']]
        for key, quotes in p['evidence'].items():
            lines += ['', '### ' + key.capitalize()]
            lines += [f"- [{p['id']}, sentence {q['sentence']}] {q['quote']}" for q in quotes] or ['Not detected in supplied text.']
        lines += ['', '### Critical screening'] + [f"- {c['criterion']}: {c['status']}" for c in p['critique']['checklist']]
    lines += ['', '## Questions for further review'] + ['- ' + q for q in report['review']['research_gaps_to_verify']]
    lines += ['', '## Comparison limits', report['comparison']['caution'], '', '## Scope', report['review']['limitations']]
    return '\n'.join(lines)
