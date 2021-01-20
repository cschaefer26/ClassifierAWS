import joblib
from typing import List, Dict

from sklearn.pipeline import Pipeline


class TextClassifier:

    def __init__(self, classes: List[str], pipeline: Pipeline):
        self.classes = classes
        self.pipe = pipeline

    def __call__(self, text: str) -> Dict[str, float]:
        pipe_results = self.pipe.predict_proba([text])[0]
        return {self.classes[i]: t for i, t in enumerate(pipe_results)}

    def save(self, path: str) -> None:
        joblib.dump(self, path)

    @classmethod
    def load(cls, path) -> 'TextClassifier':
        classifier = joblib.load(path)
        return classifier
