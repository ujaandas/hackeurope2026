import os
import pytest
from fastapi.testclient import TestClient

# Use a temp database for tests
os.environ["DATABASE_PATH"] = "/tmp/greenlinter_test.db"

from app.main import app as fastapi_app
from app.analyzer.engine import AnalysisEngine
from app.analyzer.patterns.sorting import SortingPatternDetector
from app.analyzer.patterns.memory import MemoryPatternDetector
from app.db.database import init_db
import app.db.database as db_module

db_module.DB_PATH = "/tmp/greenlinter_test.db"


@pytest.fixture(autouse=True)
def setup_app():
    import asyncio
    loop = asyncio.new_event_loop()
    loop.run_until_complete(init_db())
    engine = AnalysisEngine()
    engine.register(SortingPatternDetector())
    engine.register(MemoryPatternDetector())
    fastapi_app.state.engine = engine
    yield
    loop.close()
    if os.path.exists("/tmp/greenlinter_test.db"):
        os.remove("/tmp/greenlinter_test.db")


@pytest.fixture
def client():
    return TestClient(fastapi_app)


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_bubble_sort(client):
    code = """
void bubbleSort(int arr[], int n) {
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
    response = client.post("/api/analyze", json={
        "filename": "test.cpp",
        "code": code,
        "language": "cpp",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.cpp"
    assert len(data["patterns"]) >= 1
    assert data["total_energy_score"] > 10
    assert data["estimated_kwh"] > 0


def test_analyze_clean_code(client):
    code = """
#include <algorithm>
#include <vector>
void sortData(std::vector<int>& v) {
    std::sort(v.begin(), v.end());
}
"""
    response = client.post("/api/analyze", json={
        "filename": "clean.cpp",
        "code": code,
        "language": "cpp",
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data["patterns"]) == 0
    assert data["total_energy_score"] == 10.0


def test_analyze_memory_leak(client):
    code = """
void process(int n) {
    for (int i = 0; i < n; i++) {
        int* buf = new int[1024];
        buf[0] = i;
    }
}
"""
    response = client.post("/api/analyze", json={
        "filename": "leaky.cpp",
        "code": code,
        "language": "cpp",
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data["patterns"]) >= 1


def test_dashboard_empty(client):
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "total_optimizations" in data
    assert "sustainability_score" in data
    assert "history" in data
    assert data["total_optimizations"] == 0
