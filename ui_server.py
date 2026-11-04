"""Local, dependency-free demonstration UI. Run: python3 ui_server.py"""

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import sys
from threading import Lock, Timer
from urllib.parse import urlparse
import webbrowser

ROOT = Path(__file__).resolve().parent


class DemoServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address):
        super().__init__(address, Handler)
        self.run_lock = Lock()
        self.active = None

    def stop_run(self, run_id, reason='cancelled'):
        with self.run_lock:
            active = self.active
            if active and active['id'] == run_id:
                active['reason'] = reason
                if active['process'].poll() is None:
                    active['process'].terminate()
                return True
        return False


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def reply(self, status, data, content_type='application/json'):
        body = json.dumps(data).encode() if content_type == 'application/json' else data
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def allowed_host(self):
        return self.headers.get('Host') in (f'127.0.0.1:{self.server.server_port}',
                                            f'localhost:{self.server.server_port}')

    def do_GET(self):
        if not self.allowed_host():
            return self.reply(403, {'error': 'Use the local server address.'})
        route = urlparse(self.path).path
        if route == '/api/examples':
            from sudoku import load_examples
            return self.reply(200, load_examples())
        if route == '/api/baselines':
            from benchmarks import saved_baselines
            return self.reply(200, saved_baselines())
        files = {'/': ('index.html', 'text/html; charset=utf-8'),
                 '/app.js': ('app.js', 'text/javascript; charset=utf-8'),
                 '/style.css': ('style.css', 'text/css; charset=utf-8')}
        if route not in files:
            return self.reply(404, {'error': 'Not found.'})
        name, mime = files[route]
        self.reply(200, (ROOT / 'ui' / name).read_bytes(), mime)

    def do_POST(self):
        if not self.allowed_host():
            return self.reply(403, {'error': 'Use the local server address.'})
        origin = self.headers.get('Origin')
        if origin and origin != f'http://{self.headers.get("Host")}':
            return self.reply(403, {'error': 'Cross-origin requests are not supported.'})
        if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
            return self.reply(415, {'error': 'Expected application/json.'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 65536:
                raise ValueError('Request size must be 1..65536 bytes.')
            params = json.loads(self.rfile.read(length))
            if not isinstance(params, dict):
                raise ValueError('Expected a JSON object.')
        except (ValueError, UnicodeError) as exc:
            return self.reply(400, {'error': str(exc)})
        route = urlparse(self.path).path
        run_id = params.get('run_id')
        if not isinstance(run_id, str) or not 1 <= len(run_id) <= 80:
            return self.reply(400, {'error': 'Missing or invalid run ID.'})
        if route == '/api/stop':
            return self.reply(200, {'stopped': self.server.stop_run(run_id)})
        if route != '/api/run':
            return self.reply(404, {'error': 'Not found.'})
        with self.server.run_lock:
            if self.server.active:
                return self.reply(409, {'error': 'An experiment is already running. Stop it first.'})
            process = subprocess.Popen([sys.executable, '-u', str(ROOT / 'demo_runner.py')],
                                       cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.DEVNULL, text=True, bufsize=1)
            active = {'id': run_id, 'process': process, 'reason': None}
            self.server.active = active
        timer = Timer(125, self.server.stop_run, args=(run_id, 'resource_limit'))
        timer.daemon = True
        timer.start()
        self.send_response(200)
        self.send_header('Content-Type', 'application/x-ndjson')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Connection', 'close')
        self.end_headers()
        try:
            process.stdin.write(json.dumps(params) + '\n')
            process.stdin.close()
            for line in process.stdout:
                self.wfile.write(line.encode())
                self.wfile.flush()
            process.wait()
            if active['reason']:
                event = {'type': 'stopped', 'status': active['reason'],
                         'message': 'Run stopped.' if active['reason'] == 'cancelled'
                         else 'Overall demonstration time limit reached.'}
                self.wfile.write((json.dumps(event) + '\n').encode())
            elif process.returncode not in (0, 1):
                self.wfile.write((json.dumps({'type': 'error', 'message': 'Experiment process ended unexpectedly.'}) + '\n').encode())
        except (BrokenPipeError, ConnectionResetError):
            self.server.stop_run(run_id)
        finally:
            timer.cancel()
            if process.poll() is None:
                process.terminate()
            process.wait()
            process.stdout.close()
            with self.server.run_lock:
                if self.server.active is active:
                    self.server.active = None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()
    server = DemoServer(('127.0.0.1', args.port))
    url = f'http://127.0.0.1:{server.server_port}'
    print(f'Search Lab: {url}\nPress Ctrl+C to stop the server.', flush=True)
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        if server.active:
            server.stop_run(server.active['id'])
        server.server_close()


if __name__ == '__main__':
    main()
