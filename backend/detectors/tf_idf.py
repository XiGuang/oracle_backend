import math
import numpy as np

class TfIdf:
    def __init__(self):
        self.num_docs = 0
        self.vocab = {}
        self.idf=[]
        self.wordmap={}

    def add_corpus(self, corpus):
        self._merge_corpus(corpus)

        tfidf_list = []
        for sentence in corpus:
            tfidf_list.append(self.get_tfidf(sentence))
        return tfidf_list

    def _merge_corpus(self, corpus):
        """
        统计语料库，输出词表，并统计包含每个词的文档数。
        """
        count=0
        self.num_docs = len(corpus)
        for sentence in corpus:
            words = list(sentence)
            words = set(words)
            for word in words:
                self.vocab[word] = self.vocab.get(word, 0.0) + 1.0

        for word in self.vocab.keys():
            self.idf.append(self._get_idf(word))
            self.wordmap[word]=count
            count+=1


    def _get_idf(self, term):
        """
        计算 IDF 值
        """
        return math.log(self.num_docs / (self.vocab.get(term, 0.0) + 1.0))

    def get_tfidf(self, sentence):
        tfidf = np.zeros(len(self.idf))
        terms = list(sentence)
        terms_set = set(terms)
        num_terms = len(terms)

        for term in terms_set:
            # 计算 TF 值
            tf = float(terms.count(term)) / num_terms
            # 计算 IDF 值，在实际实现时，可以提前将所有词的 IDF 提前计算好，然后直接使用。
            idf = self.idf[self.wordmap[term]]
            # 计算 TF-IDF 值
            tfidf[self.wordmap[term]] = tf * idf
        return list(tfidf)


