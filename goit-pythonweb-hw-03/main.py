from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import urllib.parse
import pathlib
import mimetypes
import json

STORAGE_PATH = pathlib.Path('storage/data.json')
jinja_env = Environment(loader=FileSystemLoader('templates'))


def load_messages():
    if STORAGE_PATH.exists() and STORAGE_PATH.stat().st_size > 0:
        with open(STORAGE_PATH, 'r', encoding='utf-8') as fd:
            return json.load(fd)
    return {}


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        elif pr_url.path == '/read':
            self.send_read_page()
        else:
            static_path = pathlib.Path(pr_url.path.lstrip('/'))
            if static_path.exists():
                self.send_static(static_path)
            else:
                self.send_html_file('error.html', 404)

    def do_POST(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/message':
            data = self.rfile.read(int(self.headers['Content-Length']))
            data_parse = urllib.parse.unquote_plus(data.decode())
            data_dict = {
                key: value
                for key, value in [el.split('=') for el in data_parse.split('&')]
            }
            self.save_message(data_dict)
            self.send_response(302)
            self.send_header('Location', '/read')
            self.end_headers()

    def save_message(self, data_dict):
        messages = load_messages()
        messages[str(datetime.now())] = data_dict

        with open(STORAGE_PATH, 'w', encoding='utf-8') as fd:
            json.dump(messages, fd, ensure_ascii=False, indent=4)

    def send_read_page(self):
        template = jinja_env.get_template('read.html')
        html = template.render(messages=load_messages())
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(pathlib.Path('templates') / filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self, file_path):
        self.send_response(200)
        mime_type, _ = mimetypes.guess_type(str(file_path))
        self.send_header('Content-type', mime_type or 'text/plain')
        self.end_headers()
        with open(file_path, 'rb') as file:
            self.wfile.write(file.read())


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('0.0.0.0', 3000)
    http = server_class(server_address, handler_class)
    print('Server running on http://localhost:3000/')
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == '__main__':
    run()
