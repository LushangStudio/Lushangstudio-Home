"""Local workspace launcher; /leave/ proxies the loopback-only demo."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
    def do_GET(self):
        if self.path=='/apps.json':
            rows=json.loads((ROOT/'apps.json').read_text())
            for row in rows:
                if row['id']=='leave':row.update(status='available',tag='本地演示')
                if row['id']=='wordtxt':row.update(status='available',tag='原项目 · 本地预览')
            data=json.dumps(rows,ensure_ascii=False).encode();self.send_response(200);self.send_header('Content-Type','application/json; charset=utf-8');self.end_headers();self.wfile.write(data)
        elif self.path=='/leave':self.send_response(308);self.send_header('Location','/leave/');self.end_headers()
        elif self.path.startswith('/leave/'):self.proxy()
        elif self.path=='/wordtxt':self.send_response(308);self.send_header('Location','/wordtxt/');self.end_headers()
        elif self.path.startswith('/wordtxt/'):
            from urllib.parse import unquote, urlsplit
            base=(ROOT.parent/'Plugin-WordTxT/frontend/dist').resolve()
            rel=unquote(urlsplit(self.path).path[len('/wordtxt/'):]) or 'index.html'
            target=(base/rel).resolve()
            if not target.is_relative_to(base) or not target.is_file():self.send_error(404);return
            self.send_response(200);self.send_header('Content-Type',self.guess_type(str(target)));self.end_headers();self.wfile.write(target.read_bytes())
        elif self.path.startswith('/api/'):self.proxy(wordtxt=True)
        elif self.path.split('?')[0] in ('/','/index.html','/style.css','/app.js'):super().do_GET()
        else:self.send_error(404)
    def do_POST(self):
        if self.path.startswith('/leave/'):self.proxy()
        elif self.path.startswith('/api/'):self.proxy(wordtxt=True)
        else:self.send_error(404)
    def proxy(self,wordtxt=False):
        body=self.rfile.read(int(self.headers.get('Content-Length','0'))) if self.command=='POST' else None
        headers={k:v for k,v in self.headers.items() if k.lower() in ('content-type','cookie')}
        url='http://127.0.0.1:8000'+self.path if wordtxt else 'http://127.0.0.1:8001/'+self.path[len('/leave/'):]
        req=Request(url,data=body,headers=headers,method=self.command)
        try:r=urlopen(req,timeout=90)
        except HTTPError as e:r=e
        except URLError:self.send_error(502,'Start the corresponding backend on port 8000 or 8001 first');return
        with r:
            self.send_response(r.status)
            for k,v in r.headers.items():
                if k.lower() not in ('transfer-encoding','connection','server','date'):self.send_header(k,v)
            self.end_headers();self.wfile.write(r.read())
if __name__=='__main__':print('Home: http://127.0.0.1:8080');ThreadingHTTPServer(('127.0.0.1',8080),Handler).serve_forever()
