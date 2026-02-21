import pytest
from app.analyzer.patterns.sorting import SortingPatternDetector


@pytest.fixture
def detector():
    return SortingPatternDetector()


def test_detects_bubble_sort(detector):
    code = """
#include <vector>
void bubbleSort(std::vector<int>& arr) {
    int n = arr.size();
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }
}
"""
    patterns = detector.detect(code, "cpp")
    assert len(patterns) >= 1
    assert any("sort" in p.name.lower() or "n²" in p.name for p in patterns)
    assert any(p.severity == "high" for p in patterns)


def test_detects_nested_loop_with_swap(detector):
    code = """
void sort(int arr[], int n) {
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            if (arr[i] > arr[j]) {
                std::swap(arr[i], arr[j]);
            }
        }
    }
}
"""
    patterns = detector.detect(code, "cpp")
    assert len(patterns) >= 1


def test_no_false_positive_single_loop(detector):
    code = """
void print(std::vector<int>& arr) {
    for (int i = 0; i < arr.size(); i++) {
        std::cout << arr[i] << std::endl;
    }
}
"""
    patterns = detector.detect(code, "cpp")
    assert len(patterns) == 0


def test_ignores_non_cpp(detector):
    code = """
for i in range(n):
    for j in range(n):
        if arr[i] > arr[j]:
            arr[i], arr[j] = arr[j], arr[i]
"""
    # Python detection not implemented for sorting yet
    patterns = detector.detect(code, "python")
    # Should not crash, may or may not detect
    assert isinstance(patterns, list)


def test_pattern_has_required_fields(detector):
    code = """
void sort(int arr[], int n) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (arr[i] > arr[j]) {
                int temp = arr[i];
                arr[i] = arr[j];
                arr[j] = temp;
            }
        }
    }
}
"""
    patterns = detector.detect(code, "cpp")
    assert len(patterns) >= 1
    p = patterns[0]
    assert p.pattern_id == "inefficient_sort"
    assert p.line_start > 0
    assert p.line_end > p.line_start
    assert p.estimated_energy_cost > 0
    assert p.estimated_energy_saved > 0
    assert len(p.description) > 0
    assert len(p.suggestion) > 0
