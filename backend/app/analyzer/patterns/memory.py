import re
from app.analyzer.patterns.base import PatternDetector
from app.models import DetectedPattern, PatternSeverity


class MemoryPatternDetector(PatternDetector):
    @property
    def pattern_id(self) -> str:
        return "excessive_alloc"

    def detect(self, code: str, language: str) -> list[DetectedPattern]:
        if language not in ("cpp", "c"):
            return []
        patterns = []
        lines = code.split("\n")
        patterns.extend(self._detect_alloc_in_loops(lines))
        patterns.extend(self._detect_memory_leaks(lines))
        return patterns

    def _detect_alloc_in_loops(self, lines: list[str]) -> list[DetectedPattern]:
        results = []
        loop_re = re.compile(r"\b(for|while)\s*\(")
        alloc_re = re.compile(r"\b(new\s+\w+|malloc\s*\(|calloc\s*\(|realloc\s*\()")

        i = 0
        while i < len(lines):
            line = lines[i]
            if loop_re.search(line):
                loop_start = i + 1
                brace_depth = 0
                j = i

                # Find loop body
                while j < len(lines):
                    brace_depth += lines[j].count("{") - lines[j].count("}")
                    if brace_depth > 0:
                        j += 1
                        break
                    j += 1

                alloc_lines = []
                loop_end = j

                while j < len(lines) and brace_depth > 0:
                    current = lines[j]
                    brace_depth += current.count("{") - current.count("}")
                    if alloc_re.search(current):
                        alloc_lines.append(j + 1)
                    if brace_depth <= 0:
                        loop_end = j + 1
                        break
                    j += 1

                if alloc_lines:
                    results.append(
                        DetectedPattern(
                            pattern_id=self.pattern_id,
                            name="Heap Allocation Inside Loop",
                            severity=PatternSeverity.HIGH,
                            line_start=loop_start,
                            line_end=loop_end,
                            description=(
                                f"Memory allocation (new/malloc) detected inside loop body "
                                f"at line(s) {', '.join(str(l) for l in alloc_lines)}. "
                                f"This causes repeated heap allocations which are expensive."
                            ),
                            suggestion=(
                                "Pre-allocate memory before the loop or use stack allocation. "
                                "Consider std::vector::reserve() or allocating a buffer once "
                                "and reusing it across iterations."
                            ),
                            estimated_energy_cost=75.0,
                            estimated_energy_saved=50.0,
                        )
                    )
                i = max(loop_end, i + 1)
                continue
            i += 1
        return results

    def _detect_memory_leaks(self, lines: list[str]) -> list[DetectedPattern]:
        results = []
        alloc_re = re.compile(r"\b(new\s+\w+|malloc\s*\(|calloc\s*\()")
        dealloc_re = re.compile(r"\b(delete\s*\[?\]?\s*\w+|free\s*\()")

        alloc_count = 0
        dealloc_count = 0
        alloc_first_line = None

        for i, line in enumerate(lines):
            # Skip comments
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("/*"):
                continue
            if alloc_re.search(line):
                alloc_count += 1
                if alloc_first_line is None:
                    alloc_first_line = i + 1
            if dealloc_re.search(line):
                dealloc_count += 1

        if alloc_count > dealloc_count and alloc_first_line is not None:
            results.append(
                DetectedPattern(
                    pattern_id="memory_leak",
                    name="Potential Memory Leak",
                    severity=PatternSeverity.MEDIUM,
                    line_start=alloc_first_line,
                    line_end=len(lines),
                    description=(
                        f"Found {alloc_count} allocation(s) but only {dealloc_count} "
                        f"deallocation(s). Memory may be leaking."
                    ),
                    suggestion=(
                        "Use smart pointers (std::unique_ptr, std::shared_ptr) instead of raw "
                        "new/delete for automatic memory management. This also reduces energy "
                        "waste from memory pressure and potential swap usage."
                    ),
                    estimated_energy_cost=50.0,
                    estimated_energy_saved=30.0,
                )
            )
        return results
