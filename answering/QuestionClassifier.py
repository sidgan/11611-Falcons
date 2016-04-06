__author__ = 'avnishs'

import re

import numpy as np
from sklearn.metrics import accuracy_score
from sklearn.svm import SVC

from Dict2Mat import Dict2Mat
from FeatureExtractor import FeatureExtractor


class QuestionClassifier:
    LABELS = ['DESC', 'ENTY', 'LOC', 'ABBR', 'HUM', 'NUM']
    PATTERN = re.compile(r"(\w+):(\w+) (.+)")
    MODEL = None

    def __init__(self):
        pass

    def train(self, training_set):
        print 'Training: Extracting Features...'
        training_features = Dict2Mat()
        training_labels = list()
        fe = FeatureExtractor()
        count = 0;
        for sentence in training_set:
            count += 1
            match = self.PATTERN.match(sentence)
            training_features.add_document(fe.extract_features(match.group(3)))
            training_labels.append(self.LABELS.index(match.group(1)))
            print 'datapoint ' + str(count)
        # self.MODEL = linear_model.LogisticRegression(C=1e5)
        # self.MODEL = tree.DecisionTreeClassifier()
        self.MODEL = SVC()
        print 'Training: Preparing Model'
        self.MODEL.fit(training_features.get_doc_term_matrix(), np.array(training_labels))
        print 'Training: Complete'

    def test(self, testing_set):
        print 'Testing: Extracting Features...'
        if self.MODEL is None:
            print "Call the train function first!"
            return None
        count = 0
        fe = FeatureExtractor()
        testing_features = Dict2Mat()
        testing_labels = list()
        for sentence in testing_set:
            count += 1
            match = self.PATTERN.match(sentence)
            testing_features.add_document(fe.extract_features(match.group(3)))
            testing_labels.append(self.LABELS.index(match.group(1)))
            print 'datapoint ' + str(count)
        print 'Testing: Making predictions'
        predictions = self.MODEL.predict(testing_features.get_doc_term_matrix())
        print 'Testing: Complete'
        return accuracy_score(testing_labels, predictions), predictions

    def predict(self, question):
        if self.MODEL is None:
            print "Call the train function first!"
            return None
        fe = FeatureExtractor()
        return self.LABELS[self.MODEL.predict(fe.extract_features(question))]
