import pytest
from app.analyzer.patterns.network import NetworkPatternDetector


@pytest.fixture
def detector():
    return NetworkPatternDetector()


# ------------------------------------------------------------------ #
# Network calls inside loops
# ------------------------------------------------------------------ #

class TestNetworkInLoops:
    def test_curl_in_for_loop_cpp(self, detector):
        code = """
#include <curl/curl.h>
int main() {
    for (int i = 0; i < 100; i++) {
        curl_easy_perform(curl);
    }
    return 0;
}
"""
        patterns = detector.detect(code, "cpp")
        assert len(patterns) == 1
        assert patterns[0].name == "Network Call Inside Loop"
        assert patterns[0].severity.value == "high"

    def test_requests_in_for_loop_python(self, detector):
        code = """
import requests
for url in urls:
    response = requests.get(url)
    data.append(response.json())
"""
        patterns = detector.detect(code, "python")
        assert len(patterns) == 1
        assert patterns[0].name == "Network Call Inside Loop"

    def test_fetch_in_loop_javascript(self, detector):
        code = """
for (let i = 0; i < items.length; i++) {
    const res = fetch(items[i].url);
    results.push(res);
}
"""
        patterns = detector.detect(code, "javascript")
        assert len(patterns) == 1
        assert patterns[0].name == "Network Call Inside Loop"

    def test_no_false_positive_network_outside_loop(self, detector):
        code = """
import requests
response = requests.get("https://api.example.com/data")
for item in response.json():
    process(item)
"""
        patterns = detector.detect(code, "python")
        # Should not flag - the network call is outside the loop
        net_in_loop = [p for p in patterns if p.name == "Network Call Inside Loop"]
        assert len(net_in_loop) == 0

    def test_while_loop_with_send_cpp(self, detector):
        code = """
while (remaining > 0) {
    int sent = send(sockfd, buffer, len, 0);
    remaining -= sent;
}
"""
        patterns = detector.detect(code, "cpp")
        assert len(patterns) == 1


# ------------------------------------------------------------------ #
# Polling pattern detection
# ------------------------------------------------------------------ #

class TestPollingPattern:
    def test_polling_with_sleep_python(self, detector):
        code = """
import requests, time
while (True):
    response = requests.get("https://api.example.com/status")
    if response.json()["done"]:
        break
    time.sleep(5)
"""
        patterns = detector.detect(code, "python")
        polling = [p for p in patterns if p.name == "Polling Instead of Event-Driven"]
        assert len(polling) == 1
        assert polling[0].severity.value == "high"

    def test_polling_with_sleep_cpp(self, detector):
        code = """
while (true) {
    curl_easy_perform(curl);
    if (check_result()) break;
    sleep(10);
}
"""
        patterns = detector.detect(code, "cpp")
        polling = [p for p in patterns if p.name == "Polling Instead of Event-Driven"]
        assert len(polling) == 1

    def test_polling_with_setinterval_js(self, detector):
        code = """
while (true) {
    const res = fetch("/api/status");
    await sleep(3000);
}
"""
        patterns = detector.detect(code, "javascript")
        polling = [p for p in patterns if p.name == "Polling Instead of Event-Driven"]
        assert len(polling) == 1

    def test_for_ever_loop_polling(self, detector):
        code = """
for (;;) {
    curl_easy_perform(curl);
    sleep(5);
}
"""
        patterns = detector.detect(code, "cpp")
        polling = [p for p in patterns if p.name == "Polling Instead of Event-Driven"]
        assert len(polling) == 1

    def test_no_false_positive_loop_without_sleep(self, detector):
        code = """
while (true) {
    int bytes = recv(sockfd, buf, sizeof(buf), 0);
    if (bytes <= 0) break;
    process(buf);
}
"""
        patterns = detector.detect(code, "cpp")
        # recv in a tight loop without sleep is a read loop, not polling
        polling = [p for p in patterns if p.name == "Polling Instead of Event-Driven"]
        assert len(polling) == 0


# ------------------------------------------------------------------ #
# Duplicate network calls
# ------------------------------------------------------------------ #

class TestDuplicateNetworkCalls:
    def test_duplicate_requests_python(self, detector):
        code = """
import requests
data1 = requests.get("https://api.example.com/users")
# ... some processing ...
data2 = requests.get("https://api.example.com/users")
"""
        patterns = detector.detect(code, "python")
        dupes = [p for p in patterns if p.name == "Duplicate Network Calls"]
        assert len(dupes) == 1
        assert "2 times" in dupes[0].description

    def test_no_false_positive_different_urls(self, detector):
        code = """
import requests
data1 = requests.get("https://api.example.com/users")
data2 = requests.get("https://api.example.com/orders")
"""
        patterns = detector.detect(code, "python")
        dupes = [p for p in patterns if p.name == "Duplicate Network Calls"]
        assert len(dupes) == 0


# ------------------------------------------------------------------ #
# Language filtering
# ------------------------------------------------------------------ #

class TestLanguageFiltering:
    def test_unsupported_language_returns_empty(self, detector):
        code = "curl_easy_perform(curl);"
        patterns = detector.detect(code, "rust")
        assert len(patterns) == 0

    def test_typescript_supported(self, detector):
        code = """
for (let i = 0; i < 10; i++) {
    const res = fetch("/api/data");
}
"""
        patterns = detector.detect(code, "typescript")
        assert len(patterns) == 1
