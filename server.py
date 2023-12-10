import http.server

import os

class WNCGIHTTPRequestHandler(http.server.CGIHTTPRequestHandler):
    cgi_directories = [
        '/',
        '/cgi-bin'
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory='./wnframework/v170/', *kwargs)

    def do_GET(self) -> None:
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.py')
            self.end_headers()
        else:
            return super().do_GET()

    def is_cgi(self) -> bool:
        return super().is_cgi() and self.path.endswith('.py')


def main():
    httpd = http.server.HTTPServer(
        ("", 8000),
        WNCGIHTTPRequestHandler
    )
    httpd.serve_forever()

if __name__ == '__main__':
    main()