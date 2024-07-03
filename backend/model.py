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


def tf(term, term_freq_dict):
    all_sum = 0
    for _, value in term_freq_dict.items():
        all_sum += value

    return float(term_freq_dict.get(term, 0) / all_sum)


def idf(term, model: Model):
    total_documents = len(model.tdfi)
    doc_counts = max(sum(1 for value in model.tdfi.values() if term in value), 1)  # We can cache this initially. Doc -> # of occur
    return math.log10(total_documents / doc_counts)
