import re
from app.analyzer.patterns.base import PatternDetector
from app.models import DetectedPattern, PatternSeverity


class NetworkPatternDetector(PatternDetector):
    """Detects unnecessary network call patterns and polling anti-patterns.

    Covers C/C++ (libcurl, sockets, Boost.Beast), Python (requests, httpx,
    urllib, aiohttp), and JavaScript/TypeScript (fetch, axios, XMLHttpRequest).
    """

    @property
    def pattern_id(self) -> str:
        return "network_waste"

    def detect(self, code: str, language: str) -> list[DetectedPattern]:
        if language not in ("cpp", "c", "python", "javascript", "typescript"):
            return []
        patterns = []
        lines = code.split("\n")
        patterns.extend(self._detect_network_in_loops(lines, language))
        patterns.extend(self._detect_polling_pattern(lines, language))
        patterns.extend(self._detect_repeated_identical_calls(lines, language))
        return patterns

    # ------------------------------------------------------------------ #
    # Network call regexes per language family
    # ------------------------------------------------------------------ #

    _NETWORK_CALL_RE = {
        "cpp": re.compile(
            r"\b(curl_easy_perform|send\s*\(|recv\s*\(|sendto\s*\(|recvfrom\s*\("
            r"|boost::beast|http::async_read|http::async_write"
            r"|httplib::Client|cpr::(Get|Post|Put|Delete|Patch))"
        ),
        "c": re.compile(
            r"\b(curl_easy_perform|send\s*\(|recv\s*\(|sendto\s*\(|recvfrom\s*\()"
        ),
        "python": re.compile(
            r"\b(requests\.(get|post|put|delete|patch|head|options)\s*\("
            r"|httpx\.(get|post|put|delete|patch|head|options|request)\s*\("
            r"|urllib\.request\.urlopen\s*\("
            r"|aiohttp\.ClientSession|session\.(get|post|put|delete|patch)\s*\("
            r"|urlopen\s*\()"
        ),
        "javascript": re.compile(
            r"\b(fetch\s*\(|axios\.(get|post|put|delete|patch|request)\s*\("
            r"|XMLHttpRequest|\.open\s*\(\s*['\"](?:GET|POST|PUT|DELETE)"
            r"|http\.request\s*\(|https\.request\s*\()"
        ),
    }
    _NETWORK_CALL_RE["typescript"] = _NETWORK_CALL_RE["javascript"]

    # Matches C-style for/while loops and Python-style "for x in y:"
    _LOOP_RE = re.compile(r"\b(for|while)\s*[\(\{]|\bfor\s+\w+\s+in\s+")

    _SLEEP_RE = {
        "cpp": re.compile(
            r"\b(sleep\s*\(|usleep\s*\(|std::this_thread::sleep_for"
            r"|Sleep\s*\(|nanosleep\s*\()\b"
        ),
        "c": re.compile(r"\b(sleep\s*\(|usleep\s*\(|nanosleep\s*\(|Sleep\s*\()\b"),
        "python": re.compile(
            r"\b(time\.sleep\s*\(|asyncio\.sleep\s*\(|sleep\s*\()\b"
        ),
        "javascript": re.compile(
            r"\b(setTimeout\s*\(|setInterval\s*\(|await\s+.*sleep\s*\()\b"
        ),
    }
    _SLEEP_RE["typescript"] = _SLEEP_RE["javascript"]

    # ------------------------------------------------------------------ #
    # 1. Network calls inside loops
    # ------------------------------------------------------------------ #

    def _get_loop_body(
        self, lines: list[str], start: int, language: str
    ) -> tuple[int, int]:
        """Return (body_start, body_end) indices for the loop starting at `start`.

        For brace-delimited languages, tracks { } depth.
        For Python, uses indentation to determine the block.
        """
        if language == "python":
            # Python: loop body is the indented block after the `:`
            header = lines[start]
            if ":" not in header:
                return start + 1, start + 1
            body_start = start + 1
            if body_start >= len(lines):
                return body_start, body_start
            # Determine indent of first body line
            first_body = lines[body_start]
            indent = len(first_body) - len(first_body.lstrip())
            if indent == 0 and first_body.strip() == "":
                # skip blank lines to find first real body line
                while body_start < len(lines) and lines[body_start].strip() == "":
                    body_start += 1
                if body_start >= len(lines):
                    return body_start, body_start
                first_body = lines[body_start]
                indent = len(first_body) - len(first_body.lstrip())
            j = body_start
            while j < len(lines):
                ln = lines[j]
                if ln.strip() == "":
                    j += 1
                    continue
                cur_indent = len(ln) - len(ln.lstrip())
                if cur_indent < indent:
                    break
                j += 1
            return body_start, j
        else:
            # Brace-delimited languages
            brace_depth = 0
            j = start
            while j < len(lines):
                brace_depth += lines[j].count("{") - lines[j].count("}")
                if brace_depth > 0:
                    j += 1
                    break
                j += 1
            body_start = j
            while j < len(lines) and brace_depth > 0:
                brace_depth += lines[j].count("{") - lines[j].count("}")
                if brace_depth <= 0:
                    j += 1
                    break
                j += 1
            return body_start, j

    def _detect_network_in_loops(
        self, lines: list[str], language: str
    ) -> list[DetectedPattern]:
        results = []
        net_re = self._NETWORK_CALL_RE.get(language)
        if net_re is None:
            return results

        i = 0
        while i < len(lines):
            line = lines[i]
            if self._LOOP_RE.search(line):
                loop_start = i + 1  # 1-indexed
                body_start, loop_end = self._get_loop_body(lines, i, language)

                net_call_lines = []
                for j in range(body_start, loop_end):
                    if net_re.search(lines[j]):
                        net_call_lines.append(j + 1)

                if net_call_lines:
                    results.append(
                        DetectedPattern(
                            pattern_id=self.pattern_id,
                            name="Network Call Inside Loop",
                            severity=PatternSeverity.HIGH,
                            line_start=loop_start,
                            line_end=loop_end,
                            description=(
                                f"Network/HTTP call detected inside loop body at "
                                f"line(s) {', '.join(str(l) for l in net_call_lines)}. "
                                f"Each iteration incurs network latency and energy "
                                f"overhead from NIC wake-ups and TCP handshakes."
                            ),
                            suggestion=(
                                "Batch requests into a single call where possible. "
                                "Use bulk/batch API endpoints, or collect parameters "
                                "and make one request after the loop. This reduces "
                                "network round-trips and radio/NIC energy consumption."
                            ),
                            estimated_energy_cost=90.0,
                            estimated_energy_saved=65.0,
                        )
                    )
                i = max(loop_end, i + 1)
                continue
            i += 1
        return results

    # ------------------------------------------------------------------ #
    # 2. Polling pattern (loop + sleep + network call)
    # ------------------------------------------------------------------ #

    def _detect_polling_pattern(
        self, lines: list[str], language: str
    ) -> list[DetectedPattern]:
        results = []
        net_re = self._NETWORK_CALL_RE.get(language)
        sleep_re = self._SLEEP_RE.get(language)
        if net_re is None or sleep_re is None:
            return results

        i = 0
        while i < len(lines):
            line = lines[i]
            # Look for while(true)-style loops (True for Python, true for C/JS)
            is_while_loop = re.search(
                r"\b(while)\s*\(?\s*(true|True|1|TRUE)\s*\)?", line
            )
            is_for_ever = re.search(r"\bfor\s*\(\s*;\s*;\s*\)", line)

            if is_while_loop or is_for_ever:
                loop_start = i + 1
                body_start, loop_end = self._get_loop_body(lines, i, language)

                has_sleep = False
                has_net_call = False

                for j in range(body_start, loop_end):
                    current = lines[j]
                    if sleep_re.search(current):
                        has_sleep = True
                    if net_re.search(current):
                        has_net_call = True

                if has_sleep and has_net_call:
                    results.append(
                        DetectedPattern(
                            pattern_id="polling_pattern",
                            name="Polling Instead of Event-Driven",
                            severity=PatternSeverity.HIGH,
                            line_start=loop_start,
                            line_end=loop_end,
                            description=(
                                "Infinite loop with sleep + network call detected. "
                                "This polling pattern keeps the CPU and NIC active "
                                "even when no new data is available, wasting energy."
                            ),
                            suggestion=(
                                "Replace polling with an event-driven approach: "
                                "use WebSockets, server-sent events (SSE), OS-level "
                                "select/epoll/kqueue, or message queues (MQTT, AMQP). "
                                "This lets the CPU sleep until data arrives, reducing "
                                "energy consumption by 60-90%."
                            ),
                            estimated_energy_cost=95.0,
                            estimated_energy_saved=70.0,
                        )
                    )
                i = max(loop_end, i + 1)
                continue
            i += 1
        return results

    # ------------------------------------------------------------------ #
    # 3. Repeated identical network calls (same URL/endpoint)
    # ------------------------------------------------------------------ #

    def _detect_repeated_identical_calls(
        self, lines: list[str], language: str
    ) -> list[DetectedPattern]:
        results = []
        # Match calls with a URL string argument
        url_call_re = re.compile(
            r"""(?:requests\.(?:get|post|put|delete|patch)|"""
            r"""httpx\.(?:get|post|put|delete|patch)|"""
            r"""fetch|axios\.(?:get|post|put|delete|patch)|"""
            r"""curl_easy_setopt\s*\([^,]+,\s*CURLOPT_URL)\s*\(\s*"""
            r"""(['"])(https?://[^'"]+)\1"""
        )

        seen_urls: dict[str, list[int]] = {}

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("#"):
                continue
            match = url_call_re.search(line)
            if match:
                url = match.group(2)
                seen_urls.setdefault(url, []).append(i + 1)

        for url, line_nums in seen_urls.items():
            if len(line_nums) >= 2:
                results.append(
                    DetectedPattern(
                        pattern_id="duplicate_network_call",
                        name="Duplicate Network Calls",
                        severity=PatternSeverity.MEDIUM,
                        line_start=line_nums[0],
                        line_end=line_nums[-1],
                        description=(
                            f"The same endpoint '{url}' is called {len(line_nums)} "
                            f"times at lines {', '.join(str(l) for l in line_nums)}. "
                            f"Redundant network calls waste energy on repeated "
                            f"TCP connections and data transfer."
                        ),
                        suggestion=(
                            "Cache the response and reuse it, or restructure to "
                            "call the endpoint once. Consider using an HTTP cache "
                            "layer or memoization for identical requests."
                        ),
                        estimated_energy_cost=60.0,
                        estimated_energy_saved=40.0,
                    )
                )
        return results
