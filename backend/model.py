import math


class Model:
    def __init__(self, ):
        self.df = {}
        self.tdfi = {}

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


def compute_tf(term, num_of_terms_in_doc, term_freq_dict):
    return float(term_freq_dict.get(term, 0) / num_of_terms_in_doc)


def compute_idf(term, model: Model):
    total_documents = len(model.tdfi)
    doc_counts = model.df.get(term, 1)
    return math.log10(total_documents / doc_counts)
