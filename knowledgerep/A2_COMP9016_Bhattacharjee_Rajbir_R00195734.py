#!/usr/bin/env python3

import re
import pandas as pd

class NaiveBayesTextClassifier(object):

    def __init__(self):
        self.classes = set()
        self.vocabulary = set()
        self.records = list()
        pass

    def fit(self, data:pd.DataFrame)->None:




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
