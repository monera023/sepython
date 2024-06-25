from xml.sax import parse
from xml.sax.handler import ContentHandler
import io
import os
import json


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
def index_document(doc_content: str) -> dict[str, int]:
    # TODO: Implement
    pass

def process():
    file_path_1 = "../docs.gl/gl4/glVertexAttribDivisor.xhtml"
    dir_path = "../docs.gl/gl4"
    term_freq_index = {}  # Dict of file_path and tf dict from the document
    with os.scandir(dir_path) as itr:
        for entry in itr:
            print(f"Indexing file:: {entry.path} ...")
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

    index_file = "index.json"
    with open(index_file, "w") as json_file:
        json.dump(term_freq_index, json_file)

    # content = read_xml_file(file_path_1)
    # lexer = Lexer(list(content.getvalue()))
    # for item in lexer:
    #     term = "".join(item).upper()
    #     val = tf.get(term, 0)
    #     tf[term] = (val + 1)
    #
    # sorted_dict = dict(sorted(tf.items(), key=lambda item: item[1], reverse=True)[:10]) # Take top 10 entries
    # for key, value in sorted_dict.items():
    #     print(f"{key} => {value}")


def process_1():
    index_file = "index.json"
    with open(index_file, "r") as json_file:
        term_freq_index = json.load(json_file)
    print(f"index.json contains {len(term_freq_index)} files")


if __name__ == "__main__":
    print(f"OK")
    # process()
    process_1()
