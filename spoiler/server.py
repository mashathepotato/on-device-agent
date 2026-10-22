"""Loopback-only API and demo. Public article fetch, extraction, and local inference."""
import json
import mimetypes
import os
import secrets
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from .core import Engine
from .articles import fetch_article, ArticleError
from .extension_id import EXTENSION_ID

ROOT = Path(__file__).resolve().parent.parent
TOKEN = secrets.token_urlsafe(24)
ENGINE = Engine()
EXTENSION = os.environ.get('SPOILER_EXTENSION_ORIGIN', 'chrome-extension://' + EXTENSION_ID)
ORIGIN = 'http://127.0.0.1:8765'


class Handler(BaseHTTPRequestHandler):
    def allowed(self):
        return self.headers.get('Host') == '127.0.0.1:8765' and self.headers.get('Origin') in (ORIGIN, EXTENSION or ORIGIN)

    def reply(self, code, data):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Cache-Control', 'no-store')
        if self.allowed():
            self.send_header('Access-Control-Allow-Origin', self.headers.get('Origin'))
            self.send_header('Vary', 'Origin')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        if not self.allowed():
            return self.reply(403, {'error': 'Origin denied'})
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', self.headers['Origin'])
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Spoiler-Token')
        self.send_header('Access-Control-Allow-Methods', 'POST')
        self.end_headers()

    def do_GET(self):
        if self.headers.get('Host') != '127.0.0.1:8765':
            return self.reply(403, {'error': 'Host denied'})
        if self.path == '/api/examples':
            path = ROOT / 'data/webis/validation.jsonl'
            if not path.exists():
                return self.reply(200, {'examples': []})
            rows = [json.loads(line) for line in path.read_text().splitlines()[:30]]
            return self.reply(200, {'examples': [{'id': r['id'], 'headline': r['headline'], 'article': r['article']} for r in rows]})
        if self.path == '/api/status':
            return self.reply(200, {'models': ENGINE.models})
        files = {'/': 'web/index.html', '/app.js': 'web/app.js', '/style.css': 'web/style.css'}
        if self.path not in files:
            return self.reply(404, {'error': 'Not found'})
        path = ROOT / files[self.path]
        data = path.read_bytes().replace(b'__TOKEN__', TOKEN.encode())
        self.send_response(200)
        self.send_header('Content-Type', mimetypes.guess_type(str(path))[0])
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.path == '/api/pair':
            if not self.allowed() or self.headers.get('Origin') != EXTENSION:
                return self.reply(403, {'error': 'Only the installed Get to the Point extension can pair'})
            return self.reply(200, {'token': TOKEN, 'models': ENGINE.models})
        if not self.allowed() or self.headers.get('X-Spoiler-Token') != TOKEN:
            return self.reply(403, {'error': 'Origin/token denied'})
        if self.path not in ('/api/spoil', '/api/spoil-link', '/api/preview'):
            return self.reply(404, {'error': 'Not found'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 150000:
                raise ValueError('Request too large or empty')
            body = json.loads(self.rfile.read(length))
            if not isinstance(body, dict):
                raise ValueError('Request must be a JSON object')
            if self.path == '/api/preview':
                result = ENGINE.preview(body.get('url'), body.get('headline'), body.get('snippet',''), body.get('mode','original'))
                result.update(total_ms=result['request_ms'],fetch_ms=0,fetch_cache_hit=False)
            elif self.path == '/api/spoil-link':
                started = time.perf_counter()
                try:
                    source = fetch_article(body.get('url'))
                except ArticleError as error:
                    if not body.get('headline'): raise
                    failed_fetch_ms=round((time.perf_counter()-started)*1000,2)
                    result=ENGINE.preview(body.get('url'),body['headline'],body.get('snippet',''),body.get('mode','original'))
                    result.update(fetch_ms=failed_fetch_ms,fetch_cache_hit=False,
                                  fallback_reason=str(error),publisher_status=error.publisher_status)
                else:
                    headline = body.get('headline') or source['article_title']
                    result = ENGINE.generate(headline, source['article'], body.get('mode', 'original'))
                    result.update({key: value for key, value in source.items() if key != 'article'})
                result['total_ms'] = round((time.perf_counter()-started)*1000, 2)
            else:
                result = ENGINE.generate(body.get('headline'), body.get('article'), body.get('mode', 'original'))
            self.reply(200, result)
        except ArticleError as error:
            self.reply(422, {'error': str(error), 'code': error.code,
                             'publisher_status': error.publisher_status})
        except (ValueError, TypeError) as error:
            self.reply(400, {'error': str(error)})
        except Exception as error:
            self.reply(503, {'error': 'Local inference failed. Start Ollama and pull the configured model.', 'detail': str(error)})


def main():
    print('Demo: ' + ORIGIN, flush=True)
    print('Extension pairing token: ' + TOKEN, flush=True)
    print('Extension origin: ' + (EXTENSION or 'disabled; set SPOILER_EXTENSION_ORIGIN and restart'), flush=True)
    ThreadingHTTPServer(('127.0.0.1', 8765), Handler).serve_forever()


if __name__ == '__main__':
    main()
