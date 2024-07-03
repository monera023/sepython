import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from backend.model import tf, idf, Model
from backend.xml_parser import Lexer

model = Model()


def server_static_file(request, file_path, content_type):
    request.send_response(200)
    request.send_header('Content-type', content_type)
    with open(file_path, "rb") as f:
        home_page = f.read()
    request.end_headers()
    request.wfile.write(home_page)


class OurSimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            print(f"IN GET for:: {self.path}")
            server_static_file(self, "index.html", "text/html")
        elif self.path == "/index.js":
            print(f"IN GET for:: {self.path}")
            server_static_file(self, "index.js", "text/javascript")
        else:
            self.send_error(404)
            self.end_headers()

    def do_POST(self):
        print(f"In post for {self.path}")
        if self.path == "/api/search":
            header_len = self.headers.get('Content-Length')
            post_body = self.rfile.read(int(header_len))
            query_string = post_body.decode('utf-8')
            print(f"query_string = {query_string}")
            tf_for_file = []
            for path, tf_index in model.tdfi.items():  # ~ 1600 docs
                rank = 0
                for token in Lexer(query_string):
                    rank += (tf(token.upper(), tf_index) * idf(token.upper(), model))
                tf_for_file.append((path, rank))
            sorted_tf = sorted(tf_for_file, key=lambda x: x[1])
            sorted_tf.reverse()
            output = []
            for row in sorted_tf[:10]:
                # print(row)
                output.append(row[0])

            response = {
                "docs": output
            }

            response_json = json.dumps(response)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(response_json.encode())


def serve(args):
    print(f"In serve.. and got index_file:: {args.index_file}")
    with open(args.index_file, "r") as json_file:
        global model
        model = Model.from_dict(json.load(json_file))
    print(f"Got.. index docs = {len(model.tdfi)}")
    http_server = HTTPServer(('localhost', 6969), OurSimpleHTTPRequestHandler)
    print(f"Starting to listen at localhost:6969")
    http_server.serve_forever()
