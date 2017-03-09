try:
    from http.server import BaseHTTPRequestHandler, HTTPServer
except ImportError:
    from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import os
import ssl
PORT_NUMBER = 9444


class myHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/ok":
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.send_header('X-Custom-Header','header-test')
            self.end_headers()
            self.wfile.write(b"ok")
            return
        elif self.path == "/403":
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"Forbidden")
            return

        self.send_response(404)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(b"Not Found")
        return


cert_path = os.path.join(os.path.dirname(__file__), 'server-cert2.pem')
key_path = os.path.join(os.path.dirname(__file__), 'server_key2.pem')
ca_path = os.path.join(os.path.dirname(__file__), 'cacert2.pem')


server = HTTPServer(('localhost', PORT_NUMBER), myHandler)
server.socket = ssl.wrap_socket(server.socket,
                                keyfile=key_path,
                                certfile=cert_path,
                                ca_certs=ca_path,
                                server_side=True)
server.serve_forever()
