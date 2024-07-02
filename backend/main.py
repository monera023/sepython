from xml.sax import parse
from xml.sax.handler import ContentHandler
import io
import os
import json
import argparse
import math
from http.server import HTTPServer, BaseHTTPRequestHandler

global_term_freq_index = {}
class FileHandler(ContentHandler):

    def __init__(self):
        self.string_buffer = io.StringIO()
        super().__init__()

    def characters(self, content):
        if content.strip() != "":
            # print(f"Content.. {repr(content)}")
            self.string_buffer.write(content)
            self.string_buffer.write(" ")  # space to keep it tidy and later split it


class Lexer:
    def __init__(self, content):
        self.content = content

    def trim_left(self):
        while len(self.content) > 0 and not self.content[0].isalnum():
            self.content = self.content[1:]

    def chop_content(self, chop_till_index):
        token = self.content[:chop_till_index]
        self.content = self.content[chop_till_index:]
        return token

    def chop_while(self, predicate):
        index = 0
        while index < len(self.content) and predicate(self.content[index]):
            index += 1
        token = self.chop_content(index)
        return token

    def next_token(self):
        self.trim_left()
        if len(self.content) == 0:
            raise StopIteration

        if self.content[0].isnumeric():
            token = self.chop_while(str.isnumeric)
            return token

        if self.content[0].isalpha():
            token = self.chop_while(str.isalpha)
            return token

        token = self.chop_content(1)
        return token

    def __iter__(self):
        return LexerIterator(self)

class LexerIterator:
    def __init__(self, lexer):
        self.lexer = lexer
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        return self.lexer.next_token()


def read_xml_file(file_path):
    # print(f"In read_xml_file for:: {file_path}")
    handler = FileHandler()
    try:
        with open(file_path, "r") as file:
            parse(file, handler)
    except Exception as e:
        print(f"Got error {e}")
        raise e
    return handler.string_buffer

def tf(term, term_freq_dict):
    all_sum = 0
    for _, value in term_freq_dict.items():
        all_sum += value

    return float(term_freq_dict.get(term, 0) / all_sum)


def idf(term):
    total_documents = len(global_term_freq_index)
    doc_counts = max(sum(1 for value in global_term_freq_index.values() if term in value), 1)
    return math.log10(total_documents / doc_counts)


def iterate_dir(path, term_freq_index):
    print(f"Iterate for folder= {path}")
    with os.scandir(path) as itr:
        for entry in itr:
            if entry.is_dir():
                iterate_dir(entry.path, term_freq_index)
            elif entry.is_file():
                if "xhtml" in entry.path:
                    print(f"Indexing file= {entry.path}")
                    # Step 1
                    content = read_xml_file(entry.path)
                    # Step 2
                    lexer = Lexer(list(content.getvalue()))
                    # Step 3
                    tf = {}
                    for item in lexer:
                        term = "".join(item).upper()
                        val = tf.get(term, 0)
                        tf[term] = (val + 1)
                    # Step 4
                    term_freq_index[entry.path] = tf



def index(args):
    print(f"In index.. for {args.folder_name}")
    term_freq_index = {}  # Dict of file_path and tf dict from the document
    iterate_dir(args.folder_name, term_freq_index)
    index_file = "index.json"
    with open(index_file, "w") as json_file:
        json.dump(term_freq_index, json_file)


def search(args):
    print(f"In search for {args.index_file}")
    with open(args.index_file, "r") as json_file:
        term_freq_index = json.load(json_file)
    print(f"index.json contains {len(term_freq_index)} files")


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
            print(header_len)
            post_body = self.rfile.read(int(header_len))
            query_string = post_body.decode('utf-8')
            print(f"query_string = {query_string}")
            tf_for_file = []
            for path, tf_index in global_term_freq_index.items():
                rank = 0
                for token in Lexer(query_string):
                    rank += (tf(token.upper(), tf_index) * idf(token.upper()))
                    # print(f"Token={token.upper()} and rank_term = {tf(token.upper(), tf_index) * idf(token.upper())}")
                # print(f"tf for path={path} => {total_tf}")
                tf_for_file.append((path, rank))
            sorted_tf = sorted(tf_for_file, key=lambda x: x[1])
            sorted_tf.reverse()
            output = []
            for row in sorted_tf[:10]:
                print(row)
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
        global global_term_freq_index
        global_term_freq_index = json.load(json_file)
    print(f"Got.. index docs = {len(global_term_freq_index)}")
    http_server = HTTPServer(('localhost', 6969), OurSimpleHTTPRequestHandler)
    print(f"Starting to listen at localhost:6969")
    http_server.serve_forever()


def main():
    parser = argparse.ArgumentParser(description="Local Search Engine Commands")
    subparsers = parser.add_subparsers(help="commands")

    parser_index = subparsers.add_parser('index', help="Index a given folder")
    parser_index.add_argument('folder_name', type=str, help="Name of the folder to index")
    parser_index.set_defaults(func=index)

    parser_search = subparsers.add_parser('search', help="Search a index file based on query")
    parser_search.add_argument('index_file', type=str, help="Index file name")
    parser_search.set_defaults(func=search)

    parser_serve = subparsers.add_parser('serve', help="Server request through http server.. <To be Implemented>")
    parser_serve.add_argument('index_file', type=str, help="Index file")
    parser_serve.set_defaults(func=serve)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    print(f"Starting..")
    main()
