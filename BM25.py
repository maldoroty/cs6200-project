from collections import Counter
import math

class BM25:

    def __init__(self, documents, k1=1.5, b=0.75):
        self.documents = documents
        self.k1 = k1
        self.b = b
        self.doc_count = len(documents["documents"])
        self.doc_vectors = self.get_doc_vectors()
        self.avg_doc_length = self.calculate_avg_doc_length()
        self.scores = []

    def get_doc_vectors(self):
        document_vectors = {}
        for document in self.documents["documents"]:
            id = document["doc_id"]
            document_vectors[id] = Counter(document["text"].split())
        return document_vectors

    def calculate_avg_doc_length(self):
        total_length = sum(sum(self.doc_vectors[id].values()) for id in self.doc_vectors.keys())
        return total_length / self.doc_count
    
    def calculate_scores(self, query):
        for id in self.doc_vectors.keys():
            document = self.doc_vectors[id]
            score = 0
            for word in query:
                df = sum(1 for doc_vector in self.doc_vectors.values() if word in doc_vector)
                idf = math.log((self.doc_count - df + 0.5) / (df + 0.5) + 1)
                tf = document.get(word, 0)
                doc_length = sum(document.values())
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * (doc_length / self.avg_doc_length))
                score += idf * (numerator / denominator)    
            self.scores.append((id, score))
    
    def top_docs(self, k):
        return sorted(self.scores, key=lambda x: x[1], reverse=True)[:k]

def mean_avg_precision(queries, relevance_data, hits):
    avg_p = []
    for query in queries:
        rel = 0
        prec = 0
        relevant_docs = relevance_data[query]

        for i, (doc_id, _) in enumerate(hits):
            if doc_id in relevant_docs and relevant_docs[doc_id] == 1:
                rel += 1
                prec += rel / (i + 1)

        if rel > 0:
            avg_p.append(prec / rel)
        else:
            avg_p.append(0)

    map = sum(avg_p) / len(avg_p)
    return map
