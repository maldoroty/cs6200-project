from collections import Counter
import math

class BM25:

    def __init__(self, documents, k1=1.5, b=0.75):
        """
        Initialize the BM25 scoring model.

        Parameters:
        - documents (dict): A dictionary containing document data, including document IDs and text.
        - k1 (float): The positive parameter for controlling term saturation (default is 1.5).
        - b (float): The parameter for controlling the impact of document length on scoring (default is 0.75).
        """
        self.documents = documents
        self.k1 = k1
        self.b = b
        self.doc_count = len(documents["documents"])
        self.doc_vectors = self.get_doc_vectors()
        self.avg_doc_length = self.calculate_avg_doc_length()
        self.scores = {}

    def get_doc_vectors(self):
        """
        Create document vectors (term frequency counters).

        Returns:
        - dict: A dictionary where keys are document IDs and values are Counter objects representing document vectors.
        """
        document_vectors = {}
        for document in self.documents["documents"]:
            id = document["doc_id"]
            document_vectors[id] = Counter(document["text"].split())
        return document_vectors

    def calculate_avg_doc_length(self):
        """
        Calculate the average document length.

        Returns:
        - float: The average document length.
        """
        total_length = sum(sum(self.doc_vectors[id].values()) for id in self.doc_vectors.keys())
        return total_length / self.doc_count
    
    def calculate_scores(self, query):
        """
        Calculate BM25 scores for each document with respect to the given query.

        Parameters:
        - query (str): The query for which BM25 scores are calculated.
        """
        scores = []
        for id in self.doc_vectors.keys():
            document = self.doc_vectors[id]
            score = 0
            for word in query.split():
                df = sum(1 for doc_vector in self.doc_vectors.values() if word in doc_vector)
                idf = math.log((self.doc_count - df + 0.5) / (df + 0.5) + 1)
                tf = document.get(word, 0)
                doc_length = sum(document.values())
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * (doc_length / self.avg_doc_length))
                score += idf * (numerator / denominator)    
            scores.append((id, score))
        self.scores[query] = scores
    
    def top_docs(self, query, k):
        """
        Get the top-k documents.

        Parameters:
        - query (str): The query for which top documents are retrieved.
        - k (int): The number of top documents to retrieve.

        Returns:
        - list: A list of tuples containing document IDs and their corresponding BM25 scores, sorted by score in descending order.
        """
        if query not in self.scores:
            self.calculate_scores(query)
        return sorted(self.scores[query], key=lambda x: x[1], reverse=True)[:k]

    def mean_avg_precision(self, queries, relevance_data, k):
        """
        Calculate the mean average precision for a list of queries.

        Parameters:
        - queries (list): A list of queries.
        - relevance_data (dict): A dictionary containing relevance information for each query.
        - k (int): The number of top documents considered.

        Returns:
        - float: The mean average precision across all queries.
        """
        avg_p = []
        for query in queries:
            rel = 0
            prec = 0
            relevant_docs = relevance_data[query]
            self.calculate_scores(query)
            hits = self.top_docs(query, k)
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
