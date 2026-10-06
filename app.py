from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import base64
import io
import json
from urllib.error import URLError
from agents import analyze, LiteratureAgent, markdown

ROOT = Path(__file__).resolve().parent

class Handler(BaseHTTPRequestHandler):
    def respond(self, status, data, mime='application/json'):
        body = json.dumps(data).encode() if mime == 'application/json' else data
        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        assets = {'/': ('index.html', 'text/html; charset=utf-8'), '/main.js': ('main.js', 'text/javascript'), '/style.css': ('style.css', 'text/css'), '/sample': ('sample.json', 'application/json; charset=utf-8')}
        if self.path not in assets:
            return self.respond(404, {'error': 'Not found'})
        file, mime = assets[self.path]
        self.respond(200, (ROOT / file).read_bytes(), mime)

    def do_POST(self):
        try:
            size = int(self.headers.get('Content-Length', 0))
            if not 0 < size <= 12_000_000:
                raise ValueError('Request exceeds the 12 MB limit or is empty.')
            data = json.loads(self.rfile.read(size))
            if self.path == '/api/analyze':
                result = analyze(data['papers'])
                result['markdown'] = markdown(result)
                return self.respond(200, result)
            if self.path == '/api/search':
                return self.respond(200, {'papers': LiteratureAgent().run(data['query'])})
            if self.path == '/api/pdf':
                try:
                    from pypdf import PdfReader
                except ImportError:
                    raise ValueError('PDF support needs pypdf. Run: python -m pip install -r requirements.txt')
                content = base64.b64decode(data['content'], validate=True)
                if len(content) > 8_000_000:
                    raise ValueError('PDF must be under 8 MB.')
                reader = PdfReader(io.BytesIO(content))
                if len(reader.pages) > 100:
                    raise ValueError('PDF must have at most 100 pages.')
                text = '\n'.join(p.extract_text() or '' for p in reader.pages)
                if len(text.strip()) < 80:
                    raise ValueError('No usable text found. Scanned PDFs need OCR first.')
                return self.respond(200, {'text': text[:250000], 'truncated': len(text) > 250000})
            self.respond(404, {'error': 'Not found'})
        except (URLError, TimeoutError) as exc:
            self.respond(502, {'error': 'Literature service unavailable. Check internet access or import text instead.'})
        except Exception as exc:
            self.respond(400, {'error': str(exc) or 'Unable to process input.'})

if __name__ == '__main__':
    print('Chetan Research Lab: http://127.0.0.1:8001 (Ctrl+C to stop)', flush=True)
    ThreadingHTTPServer(('127.0.0.1', 8001), Handler).serve_forever()
