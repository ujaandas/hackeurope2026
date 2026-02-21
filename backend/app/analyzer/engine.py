from app.analyzer.patterns.base import PatternDetector
from app.models import DetectedPattern


class AnalysisEngine:
    def __init__(self):
        self.detectors: list[PatternDetector] = []

    def register(self, detector: PatternDetector):
        self.detectors.append(detector)

    def analyze(self, code: str, language: str) -> list[DetectedPattern]:
        all_patterns = []
        for detector in self.detectors:
            all_patterns.extend(detector.detect(code, language))
        return all_patterns
