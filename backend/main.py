from xml.sax import parse
from xml.sax.handler import ContentHandler
import io
import os
import itertools

all_documents = {}  # dict[str, dict[str, int]]
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

    def next_token(self):
        self.trim_left()
        if len(self.content) == 0:
            raise StopIteration

        if self.content[0].isnumeric():
            index = 0
            while index < len(self.content) and self.content[index].isnumeric():
                index += 1
            token = self.chop_content(index)
            return token

        if self.content[0].isalpha():
            index = 0
            while index < len(self.content) and self.content[index].isalpha():
                index += 1
            token = self.chop_content(index)
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
    file_path = "../docs.gl/gl4/glClear.xhtml"
    file_path_1 = "../docs.gl/gl4/glVertexAttribDivisor.xhtml"
    dir_path = "../docs.gl/gl4"
    with os.scandir(dir_path) as itr:
        for entry in itr:
            # print(f"FileName:: {entry.path}.. isFile:: {entry.is_file()}")
            # content = read_xml_file(entry.path)
            # print(f"Final string buffer...{list(content.getvalue())}.. {content.getvalue()}")
            break

    content = read_xml_file(file_path_1)
    lexer = Lexer(list(content.getvalue()))
    for item in lexer:
        print("".join(item).upper())


if __name__ == "__main__":
    print(f"OK")
    process()
