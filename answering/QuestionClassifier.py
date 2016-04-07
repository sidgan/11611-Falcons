__author__ = 'avnishs'

import Queue
import re
import pickle
import numpy as np
from sklearn import linear_model
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.externals import joblib

from Dict2Mat import Dict2Mat
from FeatureExtractor import FeatureExtractor


class QuestionClassifier:
    LABELS = ['DESC', 'ENTY', 'LOC', 'ABBR', 'HUM', 'NUM']
    PATTERN = re.compile(r"(\w+):(\w+) (.+)")
    MODEL = None
    FEATURE_TEMPLATE = None

    def __init__(self, use_pickle=False):  # TODO: Set use_pickle = False to re-train models
        self.use_pickle = use_pickle
        if self.use_pickle:
            print 'Loading pickled model'
            self.MODEL = joblib.load('../data/q_classifier.pkl')
            self.FEATURE_TEMPLATE = joblib.load('../data/feature_dict.pkl')

    def train(self, training_set):
        if self.use_pickle:
            print 'Pickled model was loaded'
        else:
            print 'Training: Extracting Features...'
            q = Queue.Queue()
            training_features = Dict2Mat()
            training_labels = list()
            fe = FeatureExtractor()
            count = 0
            for sentence in training_set:
                count += 1
                match = self.PATTERN.match(sentence)
                # threading.Thread(target=fe.extract_features, args = (match.group(3),q)).start()
                training_features.add_document(fe.extract_features(match.group(3)))
                training_labels.append(self.LABELS.index(match.group(1)))
                print 'datapoint ' + str(count)

            # q.join()
            # map(lambda item:training_features.add_document(item),q)
            self.MODEL = linear_model.LogisticRegression(n_jobs=4, class_weight='balanced',
                                                         multi_class='multinomial', solver='newton-cg')
            # self.MODEL = tree.DecisionTreeClassifier()
            # self.MODEL = SVC()
            # self.MODEL = RandomForestClassifier(n_jobs=4)
            # self.MODEL = BaggingClassifier(base_estimator=linear_model.LogisticRegression(n_jobs=4, class_weight='balanced',
            #                                              multi_class='multinomial', solver='newton-cg'))
            # self.MODEL = BaggingClassifier(base_estimator=AdaBoostClassifier(base_estimator=tree.DecisionTreeClassifier(), n_estimators=20))
            self.FEATURE_TEMPLATE = training_features.get_dictionary()
            print 'Training: Preparing Model'
            self.MODEL.fit(training_features.get_doc_term_matrix(), np.array(training_labels))

            joblib.dump(self.FEATURE_TEMPLATE, "../data/feature_dict.pkl")
            joblib.dump(self.MODEL, "../data/q_classifier.pkl")

            print 'Training: Complete'


    def test(self, testing_set):
        print 'Testing: Extracting Features...'
        if self.MODEL is None:
            print "Call the train function first!"
            return None
        count = 0
        fe = FeatureExtractor()
        testing_features = Dict2Mat(False)
        testing_labels = list()
        for sentence in testing_set:
            count += 1
            match = self.PATTERN.match(sentence)
            testing_features.add_document(fe.extract_features(match.group(3)))
            testing_labels.append(self.LABELS.index(match.group(1)))
            print 'datapoint ' + str(count)
        print 'Testing: Making predictions'
        predictions = self.MODEL.predict(testing_features.get_doc_term_matrix(self.FEATURE_TEMPLATE))
        print 'Testing: Complete'
        from collections import Counter
        print Counter(predictions)
        print confusion_matrix(testing_labels, predictions)
        return accuracy_score(testing_labels, predictions), predictions

    def predict(self, question):
        if self.MODEL is None or not self.use_pickle:
            print "Call the train function first!"
            return None
        fe = FeatureExtractor()
        return self.LABELS[self.MODEL.predict(fe.extract_features(question))]
