from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from threading import BoundedSemaphore
import hmac,hashlib,json,os,traceback

def serve(name,port,route,handler):
    trusted=json.loads(os.environ.get('TRUSTED_SERVICE_HASHES','{}'))
    allowed='optimization' if name=='quant_optimizer' else 'backtest'
    if allowed not in trusted:raise RuntimeError('Trusted caller is not configured')
    slots=BoundedSemaphore(2)
    class Handler(BaseHTTPRequestHandler):
        def reply(self,status,payload):
            data=json.dumps(payload,ensure_ascii=False,allow_nan=False).encode()
            self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
        def do_GET(self):
            self.reply(200 if self.path=='/health' else 404,{'status':'ok','service':name} if self.path=='/health' else {'error':'Not found'})
        def do_POST(self):
            if self.path!=route:return self.reply(404,{'error':'Not found'})
            if self.headers.get('X-Service-Name')!=allowed or not hmac.compare_digest(hashlib.sha256(self.headers.get('X-Internal-Token','').encode()).hexdigest(),trusted[allowed]):return self.reply(403,{'error':'Internal service authorization required'})
            try:size=int(self.headers.get('Content-Length','0'))
            except ValueError:return self.reply(400,{'error':'Invalid content length'})
            if not 0<size<=8_000_000:return self.reply(413,{'error':'Request body too large'})
            if not slots.acquire(blocking=False):return self.reply(429,{'error':'计算队列已满，请稍后重试'})
            try:self.reply(200,handler(json.loads(self.rfile.read(size))))
            except (ValueError,TypeError,KeyError) as error:self.reply(400,{'error':str(error)})
            except Exception:traceback.print_exc();self.reply(500,{'error':'数值计算失败'})
            finally:slots.release()
    print(f'{name} ready on {port}',flush=True)
    ThreadingHTTPServer((os.environ.get('SERVICE_HOST','127.0.0.1'),int(port)),Handler).serve_forever()
