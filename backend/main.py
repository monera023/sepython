import json
import argparse

from backend.indexer import index
from backend.server import serve
global_term_freq_index = {}


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
    parser_serve.add_argument('folder_name', type=str, help="Name of the folder to index")
    parser_serve.set_defaults(func=serve)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    print(f"Starting..")
    main()
