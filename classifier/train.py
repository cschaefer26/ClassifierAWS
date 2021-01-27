# adapted from https://scikit-learn.org/stable/tutorial/text_analytics/working_with_text_data.html

import numpy as np
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from classifier.model import TextClassifier

if __name__ == '__main__':
    categories = ['alt.atheism', 'soc.religion.christian', 'comp.graphics', 'sci.med']
    X_train = fetch_20newsgroups(subset='train', categories=categories)
    X_test = fetch_20newsgroups(subset='test', categories=categories)
    classifier_pipe = Pipeline([('vectorizer', TfidfVectorizer()),
                                ('classifier', LogisticRegression())])

    classifier_pipe.fit(X_train['data'], X_train['target'])
    predicted = classifier_pipe.predict(X_test['data'])
    test_accuracy = np.mean(predicted == X_test['target'])
    print(f'accuracy: {test_accuracy}')

    # save and load model
    text_classifier = TextClassifier(classes=X_test['target_names'],
                                     pipeline=classifier_pipe)
    text_classifier.save('/tmp/classifier.pkl')
    text_classifier = TextClassifier.load('/tmp/classifier.pkl')
    sample_pred = text_classifier('May god bless you.')
    print(f'sample pred: {sample_pred}')


