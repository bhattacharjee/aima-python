#!/usr/bin/env python3

import re
import string
import pandas as pd

class NaiveBayesTextClassifier(object):

    def __init__(self):
        # the set of all classes
        self.classes = set()

        # the vocabullary
        self.vocabulary = set()

        self.records = list()

        # count of each word in each class
        self.word_count_by_class = dict()

        # the full training data
        self.train_data = None

        # prior probabilities for each class
        self.priors = dict()

        # Total number of words in all documents of each class
        self.total_word_count_by_class = dict()
        pass

    def cleanup_line(line:str)->list:
        # cleanup line
        ret = []
        for c in list(line):
            if c in string.punctuation:
                continue
            if c in list("<>(){}\\/"):
                continue
            ret.append(c)
        if len(ret) < 0:
            raise AssertionError("cleaned up line contains no characters")
        return "".join(ret)

    def get_words(line:str)->list:
        """
        Take a line, and split it into words, perform any string manipulation
        required on it.
        Also if required, take 2-3 grams
        """
        line = line.lower()
        line = self.cleanup_line(line)
        print (line)

    def calculate_priors(self):
        n_inst = len(self.train_data)
        for c in self.classes:
            rows = self.train_data.loc[self.train_data['class_label'] == c]
            n_c = len(rows)
            # TODO: Apply smoothing here
            self.priors[c] = n_c / n_inst

    def fit(self, df:pd.DataFrame)->None:
        # Save the training data
        self.train_data = df

        # First get the classes
        self.classes = set(df.class_label.unique())
        for this_class in self.classes:
            self.word_count_by_class[this_class] = {}
            self.total_word_count_by_class[this_class] = 0

        # Calculate priori probabilities of all classes
        self.calculate_priors()

        # Identify all unique words
        # Calculate Priori Probabilities
        # Calculate conditional probabilities of each word




def read_lines(filename:str)->list:
    with open(filename, "r") as f:
        return [line.strip() for line in f.readlines()]

class LineParser(object):
    def __init__(self):
        self.compiled_re = re.compile("(\S+)\s*(\S.*)")
        pass

    def parse_line(self, line:str)->tuple:
        """
        Take a line that, and split it into two items
        eg: "ham       this is something"
        is split into
        ("ham", "this is something")
        """
        m = self.compiled_re.search(line)
        assert(None != m.group(1) and isinstance(m.group(1), str))
        assert(None != m.group(2) and isinstance(m.group(2), str))
        return(m.group(1), m.group(2))

def read_lines_and_convert_to_df(filename)->pd.DataFrame:
    lines = read_lines(filename)
    lp = LineParser()
    labels = []
    documents = []
    for line in lines:
        label, text = lp.parse_line(line)
        labels.append(label)
        documents.append(text)
    labels = pd.Series(labels, dtype=str)
    documents = pd.Series(documents, dtype=str)
    df = pd.DataFrame({'class_label': labels, 'document': documents})
    return df

def main():
    df = read_lines_and_convert_to_df("small.txt")
    nb = NaiveBayesTextClassifier()
    nb.fit(df)

main()
