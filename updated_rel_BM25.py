from collections import Counter
import math

class BM25_updated_rel:

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

        self.prevalence = {'flu': 0.00783368484, 'covid': 0.00002044893, 
                           'diabetes': 0.089, 'addisons disease': 0.00001 , 
                           'depression': 0.184, 'cardiac arrest': 0.00107261223,
                           'asthma': 0.08333333333, 'glaucoma': 0.00903886712, 
                           'leukemia': 0.00147898463, 'crohns disease': 0.01}

        self.id_to_disease = {'Flu': 'flu', 'Cov': 'covid', 'Dia': 'diabetes', 'Add': 'addisons disease', 
                              'Dep': 'depression', 'Car': 'cardiac arrest', 'Ast': 'asthma', 'Gla': 'glaucoma', 
                              'Leu': 'leukemia', 'Cro': 'crohns disease'}


    def get_doc_vectors(self):
        """
        Create document vectors (term frequency counters).

        Returns
        -------
        dict
            A dictionary where keys are document IDs and values are Counter objects representing document vectors.
        """
        document_vectors = {}
        for document in self.documents["documents"]:
            id = document["doc_id"]
            document_vectors[id] = Counter(document["text"].split())
        return document_vectors

    def calculate_avg_doc_length(self):
        """
        Calculate the average document length.

        Returns
        -------
        float
            The average document length.
        """

        total_length = sum(sum(self.doc_vectors[id].values()) for id in self.doc_vectors.keys())
        return total_length / self.doc_count
    
    def calculate_scores(self, query):
        """
        Calculate BM25 scores for each document with respect to the given query.

        Parameters
        ----------
        query : str
            The query for which BM25 scores are calculated.
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


    def top_docs(self, query, k, metric="tfidf", to_sort=True):
        """
        Get the top-k documents.

        Parameters
        ----------
        query : str
            The query for which top documents are retrieved.
        k : int 
            The number of top documents to retrieve.
        metric : str
            Which scoring metric to use.
        to_sort : bool
            Whether or not to sort the doc scores.

        Returns
        -------
        list
            A list of tuples containing document IDs and their corresponding BM25 scores.
        """
        if query not in self.scores:
            self.calculate_scores(query)

        scores = None
        if metric == "zero_to_five_weighted":
            scores = self.get_rarity(query)
        
        elif metric == "zero_to_five":
            scores = self.updated_scores(query)
        
        elif metric == "tfidf":
            scores = self.scores[query]
        
        if to_sort:
            return sorted(scores, key=lambda x: x[1], reverse=True)[:k]
        else:
            return scores
    
    def updated_scores(self, query):
        """ Returns a list of scores for the given query that are scaled to a
        range of 0 to 5. This allows a much easier understanding of document
        relevancy.

        Parameters
        ----------
        query : str
            The query to retrieve the transformed scores for.
        
        Returns
        -------
        list[tuple[str, float]]
            List of doc scores tuples
        """

        scores = self.scores[query]
        
        rounded_score_list = []
        for id, score in scores:
            
            all_scores = [a_score for a_id, a_score in scores]

            scaled_score = self.norm(score, all_scores) * 5
            rounded_score = round(scaled_score)
            rounded_score_list.append((id, rounded_score))

        return rounded_score_list

    
    def get_rarity(self, query):
        """ Returns a list of scores for the given query that are scaled to a
        range of 0 to 5 which are also weighted using that disease's rarity.

        Parameters
        ----------
        query : str
            The query to retrieve the transformed scores for.
        
        Returns
        -------
        list[tuple[str, float]]
            List of doc scores tuples
        """

        scores = self.updated_scores(query)

        rarity_scores = []
        for id, score in scores:
            disease = self.id_to_disease[id[:3]]
            rarity = self.prevalence[disease]

            adjusted_for_rarity = self.norm(rarity, self.prevalence.values()) * score

            rarity_scores.append((id, adjusted_for_rarity))

        return rarity_scores
        
    
    def norm(self, val, all_vals):
        """ Normalizes the given value to a range between 0 and 1 using the given list
        of values.

        Parameters
        ----------
        val : float
            The value to normalize.
        all_vals : list[float]
            The rest of values that are used to normalize the given val.
        
        Returns
        -------
        float
            The normalized value.
        """
        min_value = min(all_vals)
        max_value = max(all_vals)
        norm_value = (val - min_value) / (max_value - min_value)

        return norm_value

    
    def dcg(self, doc_scores):
        """ Calculates the Discounted Cumulative Gain of the given document scores.

        Parameters
        ----------
        doc_scores : list[tuple[str, float]]
            The document scores to calculate the DCG for.
        
        Returns
        -------
        float
            The DCG of the given document scores.
        """

        dcg_val = 0
        for i, id_score in enumerate(doc_scores, start=1):
            id, score = id_score
            dcg_val += ((2 ** score) - 1) / (math.log2(i + 1))

        return dcg_val
    

    def ndcg(self, doc_scores):
        """ Calculates the Normalized Discounted Cumulative Gain (nDCG) of the
        given document scores.

        Parameters
        ----------
        doc_scores : list[tuple[str, float]]
            The document scores to calculate the DCG for.
        
        Returns
        -------
        float
            The DCG of the given document scores.
        """
        
        sorted_rel_scores = sorted(doc_scores, key=lambda x: x[1], reverse = True)
        idcg = self.dcg(sorted_rel_scores)
        if idcg == 0:
            return 0
        else:
            ndcg = self.dcg(doc_scores) / idcg
            return ndcg




