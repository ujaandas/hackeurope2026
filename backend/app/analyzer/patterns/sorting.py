import re
from app.analyzer.patterns.base import PatternDetector
from app.models import DetectedPattern, PatternSeverity


class SortingPatternDetector(PatternDetector):
    @property
    def pattern_id(self) -> str:
        return "inefficient_sort"

    def detect(self, code: str, language: str) -> list[DetectedPattern]:
        if language not in ("cpp", "c", "python"):
            return []
        patterns = []
        lines = code.split("\n")
        patterns.extend(self._detect_nested_loops(lines, language))
        return patterns

    def _detect_nested_loops(self, lines: list[str], language: str) -> list[DetectedPattern]:
        results = []
        loop_re = re.compile(r"\b(for|while)\s*\(")
        swap_re = re.compile(
            r"(std::swap|swap\s*\(|temp\s*=|tmp\s*=|\]\s*=\s*\w+\[.*\]\s*;)",
            re.IGNORECASE,
        )
        size_re = re.compile(r"(\.size\(\)|\.length\(\)|\bn\b|\blen\b|\bsize\b)")

        i = 0
        while i < len(lines):
            line = lines[i]
            if loop_re.search(line):
                outer_start = i + 1
                brace_depth = 0
                has_opening = "{" in line
                if has_opening:
                    brace_depth = line.count("{") - line.count("}")

                j = i + 1
                if not has_opening:
                    # Find opening brace
                    while j < len(lines):
                        if "{" in lines[j]:
                            brace_depth = lines[j].count("{") - lines[j].count("}")
                            j += 1
                            break
                        j += 1

                # Scan inside outer loop for inner loop
                inner_start = None
                inner_has_swap = False
                outer_end = j

                while j < len(lines) and brace_depth > 0:
                    current = lines[j]
                    brace_depth += current.count("{") - current.count("}")

                    if loop_re.search(current) and inner_start is None:
                        inner_start = j + 1

                    if inner_start is not None and swap_re.search(current):
                        inner_has_swap = True

                    if brace_depth <= 0:
                        outer_end = j + 1
                        break
                    j += 1

                if inner_start is not None:
                    if inner_has_swap:
                        results.append(
                            DetectedPattern(
                                pattern_id=self.pattern_id,
                                name="O(n²) Bubble Sort Pattern",
                                severity=PatternSeverity.HIGH,
                                line_start=outer_start,
                                line_end=outer_end,
                                description=(
                                    "Nested loop with element swapping detected. "
                                    "This is characteristic of O(n²) sorting algorithms "
                                    "like bubble sort or selection sort."
                                ),
                                suggestion=(
                                    "Replace with std::sort() which uses O(n log n) introsort. "
                                    "This reduces CPU cycles by ~100x for large inputs."
                                ),
                                estimated_energy_cost=85.0,
                                estimated_energy_saved=60.0,
                            )
                        )
                    else:
                        # Generic nested loop - still O(n²)
                        outer_has_size = any(
                            size_re.search(lines[k])
                            for k in range(i, min(outer_end, len(lines)))
                        )
                        if outer_has_size:
                            results.append(
                                DetectedPattern(
                                    pattern_id=self.pattern_id,
                                    name="O(n²) Nested Loop Iteration",
                                    severity=PatternSeverity.MEDIUM,
                                    line_start=outer_start,
                                    line_end=outer_end,
                                    description=(
                                        "Nested loops iterating over collection size detected. "
                                        "This results in O(n²) time complexity."
                                    ),
                                    suggestion=(
                                        "Consider using a more efficient algorithm, hash map lookup, "
                                        "or STL algorithms to reduce to O(n) or O(n log n)."
                                    ),
                                    estimated_energy_cost=70.0,
                                    estimated_energy_saved=45.0,
                                )
                            )
                    i = outer_end
                    continue
            i += 1
        return results
