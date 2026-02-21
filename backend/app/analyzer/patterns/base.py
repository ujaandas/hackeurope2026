from abc import ABC, abstractmethod
from app.models import DetectedPattern


class PatternDetector(ABC):
    @abstractmethod
    def detect(self, code: str, language: str) -> list[DetectedPattern]:
        pass

    @property
    @abstractmethod
    def pattern_id(self) -> str:
        pass
