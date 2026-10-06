import json
from pathlib import Path
import unittest
from unittest.mock import patch
from agents import analyze, markdown, LiteratureAgent

class AgentTests(unittest.TestCase):
    def setUp(self):
        self.papers=json.loads((Path(__file__).resolve().parents[1]/'sample.json').read_text())
    def test_evidence_and_comparison(self):
        report=analyze(self.papers)
        self.assertEqual(len(report['papers']),2)
        self.assertEqual(len(report['comparison']['rows']),2)
        self.assertIn('84%', report['papers'][0]['evidence']['results'][0]['quote'])
        for p, raw in zip(report['papers'],self.papers):
            for q in p['summary']:
                self.assertIn(q['quote'],raw['text'])
    def test_critique_scope(self):
        report=analyze(self.papers)
        self.assertEqual(report['papers'][0]['critique']['checklist'][0]['status'],'Mention detected; verify adequacy')
        self.assertEqual(report['papers'][1]['critique']['checklist'][0]['status'],'Not detected in supplied text')
    def test_validation(self):
        for papers in ([],[{'title':'Metadata only','text':''}],['bad']):
            with self.assertRaises(ValueError):analyze(papers)
    def test_markdown(self):
        text=markdown(analyze(self.papers))
        self.assertIn('[P1, sentence',text)
        self.assertIn('Comparison limits',text)
    def test_search_validation(self):
        with self.assertRaises(ValueError): LiteratureAgent().run('x')
    def test_metadata_mapping(self):
        class Response:
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self):return json.dumps({'message':{'items':[{'title':['Paper'],'DOI':'10.1/demo','abstract':'<jats:p>Abstract &amp; methods.</jats:p>'}]}}).encode()
        with patch('agents.urlopen',return_value=Response()):
            result=LiteratureAgent().run('test research')
        self.assertEqual(result[0]['text'],'Abstract & methods.')
        self.assertEqual(result[0]['doi'],'10.1/demo')

if __name__=='__main__':unittest.main()
