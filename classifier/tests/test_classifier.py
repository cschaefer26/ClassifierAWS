import unittest
from unittest.mock import Mock

from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline

from classifier.model import TextClassifier


class TestClassifier(unittest.TestCase):

    def test_text_classifier(self) -> None:
        classifier_pipe = Pipeline([('vectorizer', CountVectorizer()),
                                    ('classifier', RandomForestClassifier())])
        classifier_pipe.fit(['x1', 'x2'] * 10, ['y1', 'y2'] * 10)
        text_classifier = TextClassifier(classes=['y1', 'y2'],
                                         pipeline=classifier_pipe)
        result = text_classifier('x1')
        self.assertTrue(result['y1'] > 0.95)
