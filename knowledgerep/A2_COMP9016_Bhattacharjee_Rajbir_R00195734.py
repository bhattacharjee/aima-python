#!/usr/bin/env python3

import os
import re
import string
import pandas as pd
import random
import json
import math
from sklearn.metrics import confusion_matrix, f1_score
random.seed(12345)

class NaiveBayesTextClassifier(object):

    def __init__(self, max_n_grams:int=1):
        self.max_n_grams = max_n_grams
        # the set of all classes
        self.classes = set()

        # the vocabullary, all words irrespective of class
        self.vocabulary = set()

        # for each class c, count of all the words in that class, count(w, c)
        self.count_w_c = dict()

        # the full training data
        self.train_data = None

        # prior probabilities for each class log(p(c))
        self.priors = dict()

        # conditional probabilities log(P(w|c))
        self.p_w_c = dict()

        # For each class w, count of all words in that class, count(c)
        self.count_c = dict()

        self.stopwords = set(['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you',\
            'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she',\
            'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs',\
            'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these',\
            'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have',\
            'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and',\
            'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for',\
            'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after',\
            'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under',\
            'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how',\
            'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', \
            'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just',\
            'don', 'should', 'now', 'the', 'a'])
        pass

    def cleanup_line(self, line:str)->list:
        # cleanup line
        ret = []
        ret2 = []
        for c in list(line):
            if c in string.punctuation:
                continue
            if c in list("<>(){}\\/"):
                continue
            if c in list('!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'):
                ret.append(' ')
            ret.append(c)
        if len(ret) < 0:
            raise AssertionError("cleaned up line contains no characters")
        last_c = None
        # If a number and a non-number are joined together, put a space in between
        for c in ret:
            if last_c != None:
                if last_c in list('0123456789') and c not in list('0123456789'):
                    ret2.append(' ')
                elif last_c not in list('0123456789') and c in list('0123456789'):
                    ret2.append(' ')
            last_c = c
            ret2.append(c)
        ret = "".join(ret2)
        # Replace numbers with ###
        ret = re.sub(r'\d+', r'###', ret)
        return ret

    def get_n_grams(self, words):
        all_grams = []
        for i in range(2, self.max_n_grams+1):
            for j in range(i-1, len(words)):
                temp = words[j-i+1:j+1]
                all_grams.append("".join(temp))
        all_grams = [w for w in all_grams if w != '']
        for w in words:
            all_grams.append(w)
        #print(all_grams)
        return all_grams


    def get_words(self, line:str)->list:
        """
        Take a line, and split it into words, perform any string manipulation
        required on it.
        Also if required, take n grams
        """
        line = line.lower()
        line = self.cleanup_line(line)
        words = re.split('\s+', line)
        words = [w for w in words if w not in self.stopwords]
        words = self.get_n_grams(words)
        return words

    def calculate_priors(self):
        n_inst = len(self.train_data)
        for c in self.classes:
            rows = self.train_data.loc[self.train_data['class_label'] == c]
            n_c = len(rows)
            # TODO: Apply smoothing here
            self.priors[c] = math.log(n_c / n_inst)

    def update_document(self, class_label:str, document:str)->None:
        if class_label not in self.count_w_c.keys():
            self.count_w_c[class_label] = dict()
        if class_label not in self.count_c.keys():
            self.count_c[class_label] = 0
        for word in self.get_words(document):
            self.count_c[class_label] += 1
            if word not in self.count_w_c[class_label].keys():
                self.count_w_c[class_label][word] = 0
            self.count_w_c[class_label][word] += 1
            if word not in self.vocabulary:
                self.vocabulary.add(word)

    def calculate_conditionals(self):
        for word in self.vocabulary:
            self.p_w_c[word] = {}
            for c in self.classes:
                c_w_c = 0
                c_c = 0
                try:
                    c_w_c = self.count_w_c[c][word]
                    c_c = self.count_c[c]
                except:
                    pass
                    # TODO: Print a message on debug
                pwc = (c_w_c + 1) / (c_c + len(self.vocabulary))
                assert(pwc >= 0 and pwc <= 1)
                pwc = math.log(pwc)
                self.p_w_c[word][c] = pwc

    def predict_one(self, document:str)->str:
        all_ps = []
        all_class_p_tuples = []
        for c in self.classes:
            p = self.priors[c]
            for word in self.get_words(document):
                try:
                    p += self.p_w_c[word][c]
                except:
                    pass
            all_ps.append(p)
            all_class_p_tuples.append((c, p, ))
        max_p = max(all_ps)
        for c, p in all_class_p_tuples:
            if p == max_p:
                return c

    def predict(self, documents:list)->list:
        ys = []
        for document in documents:
            y = self.predict_one(document)
            ys.append(y)
        return ys


    def fit(self, df:pd.DataFrame)->None:
        # Save the training data
        self.train_data = df

        # First get the classes
        self.classes = set(df.class_label.unique())
        for this_class in self.classes:
            self.count_w_c[this_class] = {}
            self.count_c[this_class] = 0

        # Calculate priori probabilities of all classes
        self.calculate_priors()

        for i in range(len(df)):
            class_label = df.iloc[i].class_label
            document = df.iloc[i].document
            self.update_document(class_label, document)

        self.calculate_conditionals()
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

def train_test_split(df:pd.DataFrame)->tuple:
    classes = set(df.class_label.unique())
    temp_split_tuples = list()
    for c in classes:
        reduced_df = df[df['class_label'] == c]
        train_instances = pd.DataFrame(columns=df.columns)
        test_instances = pd.DataFrame(columns=df.columns)
        for i in range(len(reduced_df)):
            if random.uniform(0, 1) < 0.2:
                test_instances = test_instances.append(reduced_df.iloc[i,:])
            else:
                train_instances = train_instances.append(reduced_df.iloc[i,:])
        temp_split_tuples.append((train_instances, test_instances, ))
    train_instances = pd.DataFrame(columns=df.columns)
    test_instances = pd.DataFrame(columns=df.columns)
    for train, test in temp_split_tuples:
        train_instances = train_instances.append(train)
        test_instances = test_instances.append(test)
    return train_instances.reset_index(), test_instances.reset_index()


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

def get_accuracy_score(y_test, y_predict):
    assert(len(y_test) == len(y_predict))
    n = len(y_test)
    c = 0
    for i, j in zip(y_test, y_predict):
        if i == j:
            c += 1
    return c/n

def NaiveBayesSmsSpamCollection():
    #df = read_lines_and_convert_to_df('SMSSpamCollection/SMSSpamCollection')
    #df = read_lines_and_convert_to_df('SMSSpamCollection/small.txt')
    df = read_lines_and_convert_to_df('SMSSpamCollection/no_duplicates.txt')
    nb = NaiveBayesTextClassifier(max_n_grams=5)
    train, test = train_test_split(df)
    nb.fit(train)
    X_test = test.document.to_list()
    y_test = test.class_label.to_list()
    y_predict = nb.predict(X_test)
    print(f"accuracy = {get_accuracy_score(y_predict, y_test)}")
    print(confusion_matrix(y_test, y_predict))

def NaiveBayesClinc150():
    with open ("./clinc150_uci/data_full.json", "r") as f:
        data = json.load(f)
    validation = data['val']
    train = data['train']
    test = data['test']
    train_X = []
    train_y = []
    test_X = []
    test_y = []
    for arr in train:
        train_X.append(arr[0])
        train_y.append(arr[1])
    train = pd.DataFrame({'class_label': train_y, 'document':train_X})
    [test.append(i) for i in validation]
    for arr in test:
        test_X.append(arr[0])
        test_y.append(arr[1])
    nb = NaiveBayesTextClassifier()
    #print("Trying to fit")
    nb.fit(train)
    #print("Fit finished")
    y_predict = nb.predict(test_X)
    #print("predict finished")
    print(f"accuracy = {get_accuracy_score(y_predict, test_y)}")
    print(confusion_matrix(test_y, y_predict))

def NaiveBayesYoutubeSpam():
    df = pd.DataFrame()
    for filename in os.listdir('YoutubeSpam'):
        if not filename.endswith(".csv"):
            continue
        filename = "YoutubeSpam/" + filename
        df = df = df.append(pd.read_csv(filename))
    comments = df.CONTENT.to_list()
    classes = df.CLASS.to_list()
    df = pd.DataFrame({'class_label': classes, 'document': comments})
    train, test = train_test_split(df)
    X_test = test.document.to_list()
    y_test = test.class_label.to_list()
    nb = NaiveBayesTextClassifier(max_n_grams=25)
    nb.fit(train)
    y_predict = nb.predict(X_test)
    print(f"accuracy = {get_accuracy_score(y_predict, y_test)}")
    print(confusion_matrix(y_test, y_predict))

def NaiveBayesSentimentLabeledSentences():
    documents = []
    class_labels = []
    compiled_re = re.compile("(.*)\s+(\d+)$")
    for filename in os.listdir('sentiment_labelled_sentences'):
        if not filename.endswith('labelled.txt'):
            continue
        filename = "sentiment_labelled_sentences/" + filename
        with open(filename, "r") as f:
            lines = [line.strip() for line in f.readlines()]
            for line in lines:
                m = compiled_re.search(line)
                if None != m:
                    documents.append(m.group(1))
                    class_labels.append(m.group(2))
    df = pd.DataFrame({'class_label': class_labels, 'document': documents})
    train, test = train_test_split(df)
    X_test = test.document.to_list()
    y_test = test.class_label.to_list()
    nb = NaiveBayesTextClassifier(max_n_grams=8)
    nb.fit(train)
    y_predict = nb.predict(X_test)
    print(f"accuracy = {get_accuracy_score(y_predict, y_test)}")
    print(confusion_matrix(y_test, y_predict))



def main():
    print('-' * 120)
    print("SMS Spam Classification")
    #NaiveBayesSmsSpamCollection()
    print('-' * 120)
    print("\nClinc 150")
    NaiveBayesClinc150()
    print('-' * 120)
    print("\nYoutube Spam")
    #NaiveBayesYoutubeSpam()
    print('-' * 120)
    print("\nSentiment Analysis")
    NaiveBayesSentimentLabeledSentences()
    print('-' * 120)


main()
