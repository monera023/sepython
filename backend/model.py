import math


class Model:
    def __init__(self, ):
        self.df = {}  # Key:(Term) Value: (# of docs in which Term appears)
        self.tdfi = {} # Main Key:(FilePath), Value: Has Dict with Keys: 'index'(term_freq_index for that file). 'total_terms_count', 'last_modified' of file

    def to_dict(self):
        return {
            'df': self.df,
            'tdfi': self.tdfi
        }

    @classmethod
    def from_dict(cls, data):
        model = cls()
        model.df = data.get('df', {})
        model.tdfi = data.get('tdfi', {})
        return model

    def remove_document(self, file_path):
        if file_path in self.tdfi:
            for key in self.tdfi[file_path]['index'].keys():
                if key in self.df:
                    count = self.df[key]
                    self.df[key] = (count - 1)


    def model_check(self):
        total_documents = len(self.tdfi)
        for value in self.df.values():
            assert value <= total_documents, "Term doc counts should be <= Total Docs"


def compute_tf(term, num_of_terms_in_doc, term_freq_dict):
    return float(term_freq_dict.get(term, 0) / num_of_terms_in_doc)


def compute_idf(term, model: Model):
    total_documents = len(model.tdfi)
    doc_counts = model.df.get(term, 1)
    return math.log10(total_documents / doc_counts)
