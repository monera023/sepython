import io
from xml.sax import ContentHandler, parse


class FileHandler(ContentHandler):
    def __init__(self):
        self.string_buffer = io.StringIO()
        super().__init__()

    def characters(self, content):
        if content.strip() != "":
            # print(f"Content.. {repr(content)}")
            self.string_buffer.write(content)
            self.string_buffer.write(" ")  # space to keep it tidy and later split it


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
