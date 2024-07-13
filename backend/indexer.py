import os
from backend.model import Model
from backend.xml_parser import read_xml_file, Lexer
import snowball_mod
import json


def iterate_dir(path, _model: Model, stemmer, dict_lock):
    print(f"Iterate for folder= {path}")
    with (os.scandir(path) as itr):
        for entry in itr:
            if entry.is_dir():
                iterate_dir(entry.path, _model, stemmer, dict_lock)
            elif entry.is_file():
                if "xhtml" in entry.path:
                    with dict_lock:
                        path_index: dict = _model.tdfi.get(entry.path, {})
                        if 'last_modified_time' in path_index and path_index['last_modified_time'] >= int(entry.stat().st_mtime):
                            print(f"Not indexing file={entry.path} as it is not modified diff={path_index['last_modified_time'] - int(entry.stat().st_mtime)}")
                            continue
                        print(f"Indexing file= {entry.path}")

                        # Step 1 to remove term counts for this document
                        _model.remove_document(entry.path)

                    # Step 2
                    content = read_xml_file(entry.path)
                    # Step 3
                    lexer = Lexer(list(content.getvalue()))
                    # Step 4
                    _tf = {}
                    term_count = 0
                    for item in lexer:
                        joined_word = "".join(item)
                        stemmed_word = stemmer.stemWord(joined_word)
                        term = stemmed_word.upper()
                        val = _tf.get(term, 0)
                        _tf[term] = (val + 1)
                        term_count += 1
                    # Step 5
                    with dict_lock:
                        for key in _tf.keys():
                            val = _model.df.get(key, 0)
                            _model.df[key] = (val + 1)
                        _model.tdfi[entry.path] = {
                            'index': _tf,
                            'total_term_counts': term_count,
                            'last_modified_time': int(entry.stat().st_mtime)
                        }


def index(folder_name: str, model: Model, dict_lock):
    print(f"In index.. for {folder_name} for len_model = {len(model.tdfi)}")
    index_file = "index.json"

    stemmer = snowball_mod.stemmer('english')
    iterate_dir(folder_name, model, stemmer, dict_lock)

    model.model_check()

    print(f"Starting save of index..")
    import time
    start_t = time.time()
    with open(index_file, "w") as json_file:
        json.dump(model.to_dict(), json_file)
    end_t = time.time()
    print(f"Saved index.. in {(end_t - start_t)*1000} ms")
