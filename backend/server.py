import json
import os
import threading

from http.server import BaseHTTPRequestHandler, HTTPServer
from backend.indexer import index
from backend.model import Model, compute_tf, compute_idf
from backend.xml_parser import Lexer
import snowball_mod
stemmer = snowball_mod.stemmer('english')
model = Model()
dict_lock = threading.Lock()


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
            with dict_lock:
                for path, tf_index in model.tdfi.items():  # ~ 1600 docs
                    rank = 0
                    for token in Lexer(query_string):
                        stemmed_word = stemmer.stemWord(token)
                        rank += (compute_tf(stemmed_word.upper(), tf_index.get('total_term_counts'), tf_index.get('index')) * compute_idf(stemmed_word.upper(), model))
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
    print(f"In serve.. and got index_file:: {args.folder_name}")
    index_file = "index.json"
    global model
    if os.path.getsize(index_file) == 0:
        print(f"Index file empty..")
        model = Model()
    else:
        with open(index_file, "r") as json_file:
            model = Model.from_dict(json.load(json_file))

    print(f"Got.. index docs = {len(model.tdfi)}")

    index_thread = threading.Thread(target=index, args=(args.folder_name, model, dict_lock))

    try:
        index_thread.start()
        http_server = HTTPServer(('localhost', 6969), OurSimpleHTTPRequestHandler)
        print(f"Starting to listen at localhost:6969")
        http_server.serve_forever()
    finally:
        index_thread.join()
