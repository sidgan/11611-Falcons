__author__ = 'avnishs'

import re
import logging
import numpy as np
from sklearn import linear_model
from sklearn.externals import joblib
from collections import Counter
from Dict2Mat import Dict2Mat
from FeatureExtractor import FeatureExtractor
from sklearn.metrics import accuracy_score, confusion_matrix

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
logger = logging.getLogger('')


class QuestionClassifier:
    LABELS = ['DESC', 'ENTY', 'LOC', 'ABBR', 'HUM', 'NUM']
    PATTERN = re.compile(r"(\w+):(\w+) (.+)")
    MODEL = None
    FEATURE_TEMPLATE = None
    USE_PICKLE = False
    FEATURE_EXTRACTOR = None

    def __init__(self, use_pickle=False):  # TODO: Set use_pickle = False to re-train models
        self.USE_PICKLE = use_pickle
        self.FEATURE_EXTRACTOR = FeatureExtractor()
        if self.USE_PICKLE:
            logger.debug('Loading pickled model')

            self.MODEL = joblib.load('../data/q_classifier.pkl')
            self.FEATURE_TEMPLATE = joblib.load('../data/feature_dict.pkl')

            logger.debug('Model loaded successfully')

    def train(self, training_set):
        """
        Run training on the training corpus of labelled questions
        :param training_set: set of labelled questions
        """
        if not self.USE_PICKLE:
            logger.debug('Training: Extracting Features...')

            training_features = Dict2Mat()
            training_labels = list()

            for idx, sentence in enumerate(training_set):
                match = self.PATTERN.match(sentence)
                training_features.add_document(self.FEATURE_EXTRACTOR.get_question_features(match.group(3)))
                training_labels.append(self.LABELS.index(match.group(1)))
                logger.debug('Processed training data-point ' + str(idx + 1))

            # Train a one-vs-one logistic regression model with class weights to overcome class imbalance
            self.MODEL = linear_model.LogisticRegression(n_jobs=4, class_weight='balanced',
                                                         multi_class='multinomial', solver='newton-cg')
            # self.MODEL = tree.DecisionTreeClassifier()
            # self.MODEL = SVC()
            # self.MODEL = RandomForestClassifier(n_jobs=4)
            # self.MODEL = BaggingClassifier(base_estimator=linear_model.LogisticRegression(n_jobs=4, class_weight='balanced',
            #                                              multi_class='multinomial', solver='newton-cg'))
            # self.MODEL = BaggingClassifier(base_estimator=AdaBoostClassifier(base_estimator=tree.DecisionTreeClassifier(), n_estimators=20))
            self.FEATURE_TEMPLATE = training_features.get_dictionary()

            logger.debug('Training: Fitting model')

            self.MODEL.fit(training_features.get_doc_term_matrix(), np.array(training_labels))

            logger.debug('Training: Dumping fitted model and dictionary into pickle file')

            joblib.dump(self.FEATURE_TEMPLATE, "../data/feature_dict.pkl")
            joblib.dump(self.MODEL, "../data/q_classifier.pkl")

            logger.debug('Training: Completed')

    def test(self, testing_set):
        """
        Run testing on the testing corpus of labelled questions
        :param testing_set: set of test questions
        """
        if self.MODEL is None:
            logger.error('Error: Call the train function first!')
            exit()

        print 'Testing: Extracting Features...'

        testing_features = Dict2Mat(False)
        testing_labels = list()

        for idx, sentence in enumerate(testing_set):
            match = self.PATTERN.match(sentence)
            testing_features.add_document(self.FEATURE_EXTRACTOR.get_question_features(match.group(3)))
            testing_labels.append(self.LABELS.index(match.group(1)))
            print 'Processed training data-point ' + str(idx + 1)

        print 'Testing: Making predictions'

        predictions = self.MODEL.predict(testing_features.get_doc_term_matrix(self.FEATURE_TEMPLATE))

        print 'Testing: Complete'

        logger.debug(Counter(map(lambda i: self.LABELS[i], predictions)))
        logger.debug(confusion_matrix(testing_labels, predictions))
        return accuracy_score(testing_labels, predictions), predictions

    def predict(self, question):
        """
        Predicts the label for the question
        :param question: question for which label is to be predicted
        :return: prediction label
        """
        if self.MODEL is None:
            logger.error('Call the train function first!')
            return None
        testing_features = Dict2Mat(False)
        testing_features.add_document(self.FEATURE_EXTRACTOR.get_question_features(question))
        predictions = self.MODEL.predict(testing_features.get_doc_term_matrix(self.FEATURE_TEMPLATE))
        return self.LABELS[predictions]
