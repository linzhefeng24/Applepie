"""Local numerical microservice; no database access, no external network calls."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json, traceback, os, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from settings import read_settings
from threading import BoundedSemaphore
from engine import analyze, backtest
slots=BoundedSemaphore(2)
class Handler(BaseHTTPRequestHandler):
    def reply(self,status,body):
        raw=json.dumps(body,ensure_ascii=False,allow_nan=False).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
    def do_GET(self):
        self.reply(200 if self.path=='/health' else 404,dict(status='ok',service='quant') if self.path=='/health' else dict(error='Not found'))
    def do_POST(self):
        if self.path not in ('/analyze','/backtest'): return self.reply(404,dict(error='Not found'))
        size=int(self.headers.get('Content-Length','0'))
        if not 0<size<=8_000_000:return self.reply(413,dict(error='请求体无效或过大'))
        if not slots.acquire(blocking=False):return self.reply(429,dict(error='计算队列已满，请稍后重试'))
        try:
            payload=json.loads(self.rfile.read(size));result=(analyze if self.path=='/analyze' else backtest)(payload);self.reply(200,result)
        except (ValueError,KeyError,TypeError) as e:self.reply(400,dict(error=str(e)))
        except Exception:
            traceback.print_exc();self.reply(500,dict(error='数值计算失败'))
        finally:slots.release()
if __name__=='__main__':
    cfg=read_settings();host=cfg['SERVICE_HOST'];port=int(cfg['QUANT_PORT'])
    print(f'quant ready on {host}:{port}',flush=True);ThreadingHTTPServer((host,port),Handler).serve_forever()
