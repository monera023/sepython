import os
import json
import argparse

from backend.model import Model
from backend.server import serve
from backend.xml_parser import read_xml_file, Lexer
import snowball_mod
global_term_freq_index = {}

model = Model()


def iterate_dir(path, _model: Model, stemmer):
    print(f"Iterate for folder= {path}")
    with (os.scandir(path) as itr):
        for entry in itr:
            if entry.is_dir():
                iterate_dir(entry.path, _model, stemmer)
            elif entry.is_file():
                if "xhtml" in entry.path:
                    print(f"Indexing file= {entry.path}")
                    # Step 1
                    content = read_xml_file(entry.path)
                    # Step 2
                    lexer = Lexer(list(content.getvalue()))
                    # Step 3
                    _tf = {}
                    term_count = 0
                    for item in lexer:
                        joined_word = "".join(item)
                        stemmed_word = stemmer.stemWord(joined_word)
                        term = stemmed_word.upper()
                        val = _tf.get(term, 0)
                        _tf[term] = (val + 1)
                        term_count += 1
                    # Step 4
                    for key in _tf.keys():
                        val = _model.df.get(key, 0)
                        _model.df[key] = (val + 1)
                    _model.tdfi[entry.path] = {
                        'index': _tf,
                        'total_term_counts': term_count
                    }


def index(args):
    print(f"In index.. for {args.folder_name}")
    _model: Model = Model()
    stemmer = snowball_mod.stemmer('english')
    iterate_dir(args.folder_name, _model, stemmer)
    index_file = "index.json"
    print(f"Starting save of index..")
    import time
    start_t = time.time()
    with open(index_file, "w") as json_file:
        json.dump(_model.to_dict(), json_file)
    end_t = time.time()
    print(f"Saved index.. in {(end_t - start_t)*1000} ms")


def search(args):
    print(f"In search for {args.index_file}")
    with open(args.index_file, "r") as json_file:
        term_freq_index = json.load(json_file)
    print(f"index.json contains {len(term_freq_index)} files")


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
