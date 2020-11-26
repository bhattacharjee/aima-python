#!/usr/bin/env python3

class NaiveBayesTextClassifier(object):

    def __init__(self):
        self.classes = set()
        self.vocabulary = set()
        self.records = list()

        pass

    def add_document(self, doc:str, doc_class:str)->None:
        assert(isinstance(doc_class, str) and isinstance(doc, str))



