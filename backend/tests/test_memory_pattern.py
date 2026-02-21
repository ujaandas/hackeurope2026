import pytest
from app.analyzer.patterns.memory import MemoryPatternDetector


@pytest.fixture
def detector():
    return MemoryPatternDetector()


def test_detects_new_in_loop(detector):
    code = """
#include <cstdlib>
void processData(int n) {
    for (int i = 0; i < n; i++) {
        int* buffer = new int[1024];
        buffer[0] = i;
    }
}
"""
    patterns = detector.detect(code, "cpp")
    alloc_patterns = [p for p in patterns if p.pattern_id == "excessive_alloc"]
    assert len(alloc_patterns) >= 1
    assert alloc_patterns[0].severity == "high"


def test_detects_malloc_in_loop(detector):
    code = """
#include <cstdlib>
void process(int n) {
    for (int i = 0; i < n; i++) {
        char* buf = (char*)malloc(4096);
        buf[0] = 'a';
    }
}
"""
    patterns = detector.detect(code, "cpp")
    alloc_patterns = [p for p in patterns if p.pattern_id == "excessive_alloc"]
    assert len(alloc_patterns) >= 1


def test_detects_memory_leak(detector):
    code = """
void leaky() {
    int* a = new int[100];
    char* b = (char*)malloc(200);
    int* c = new int[300];
    // Only one free
    free(b);
}
"""
    patterns = detector.detect(code, "cpp")
    leak_patterns = [p for p in patterns if p.pattern_id == "memory_leak"]
    assert len(leak_patterns) >= 1


def test_no_false_positive_balanced(detector):
    code = """
void clean() {
    int* a = new int[100];
    delete[] a;
}
"""
    patterns = detector.detect(code, "cpp")
    leak_patterns = [p for p in patterns if p.pattern_id == "memory_leak"]
    assert len(leak_patterns) == 0


def test_no_alloc_outside_loop(detector):
    code = """
void process() {
    int* buffer = new int[1024];
    for (int i = 0; i < 1024; i++) {
        buffer[i] = i;
    }
    delete[] buffer;
}
"""
    patterns = detector.detect(code, "cpp")
    alloc_in_loop = [p for p in patterns if p.pattern_id == "excessive_alloc"]
    assert len(alloc_in_loop) == 0


def test_pattern_fields(detector):
    code = """
void bad(int n) {
    for (int i = 0; i < n; i++) {
        int* buf = new int[1024];
    }
}
"""
    patterns = detector.detect(code, "cpp")
    assert len(patterns) >= 1
    p = patterns[0]
    assert p.line_start > 0
    assert p.estimated_energy_cost > 0
    assert len(p.description) > 0
    assert len(p.suggestion) > 0
