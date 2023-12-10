import http.server

import os

DIRECTORY = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        'wnframework/v170/'
    )
)

class WNCGIHTTPRequestHandler(http.server.CGIHTTPRequestHandler):
    cgi_directories = [
        '/',
        '/cgi-bin'
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, *kwargs)

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

    address = f"{httpd.server_address[0]}:{httpd.server_address[1]}"

    print(f'Starting Server at {address}')
    httpd.serve_forever()

if __name__ == '__main__':
    main()