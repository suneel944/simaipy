from __future__ import annotations

import difflib
import html
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple


@dataclass
class TestResult:
    """Represents a single test case result."""

    test_id: str
    prompt: str
    actual_response: str
    expected_response: str
    passed: bool
    similarity_score: Optional[float] = None
    negative_similarity_score: Optional[float] = None
    category: Optional[str] = None
    type: Optional[str] = None


class TestReportGenerator:
    """Generates professional HTML test reports with interactive dashboards."""

    def __init__(self, output_dir: Path | str = "test-reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results: List[TestResult] = []

    def add_result(self, result: TestResult) -> None:
        """Add a test result to the report."""
        self.results.append(result)

    def _highlight_differences(self, actual: str, expected: str) -> Tuple[str, str]:
        """
        Highlight differences using a line-by-line comparison.
        Returns HTML strings for actual and expected panels.
        """
        if not actual and not expected:
            return "", ""
        if not actual:
            return "", self._format_text(expected)
        if not expected:
            return self._format_text(actual), ""

        actual_lines = actual.splitlines()
        expected_lines = expected.splitlines()

        matcher = difflib.SequenceMatcher(None, actual_lines, expected_lines)

        out_actual = []
        out_expected = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                for line in actual_lines[i1:i2]:
                    out_actual.append(self._format_text(line))
                for line in expected_lines[j1:j2]:
                    out_expected.append(self._format_text(line))

            elif tag == "delete":
                # Line exists in Actual but not Expected (Deletion)
                for line in actual_lines[i1:i2]:
                    out_actual.append(
                        f'<div class="diff-line del">{self._format_text(line)}</div>'
                    )

            elif tag == "insert":
                # Line exists in Expected but not Actual (Insertion)
                for line in expected_lines[j1:j2]:
                    out_expected.append(
                        f'<div class="diff-line ins">{self._format_text(line)}</div>'
                    )

            elif tag == "replace":
                # Lines are different; try to highlight word diffs
                for idx in range(max(i2 - i1, j2 - j1)):
                    a_line = actual_lines[i1 + idx] if idx < (i2 - i1) else None
                    e_line = expected_lines[j1 + idx] if idx < (j2 - j1) else None

                    if a_line is not None and e_line is not None:
                        a_html, e_html = self._highlight_words(a_line, e_line)
                        out_actual.append(
                            f'<div class="diff-line replace">{a_html}</div>'
                        )
                        out_expected.append(
                            f'<div class="diff-line replace">{e_html}</div>'
                        )
                    elif a_line is not None:
                        # a_line is guaranteed to be str here due to the None check
                        out_actual.append(
                            f'<div class="diff-line del">{self._format_text(a_line)}</div>'
                        )
                    elif e_line is not None:
                        # e_line is guaranteed to be str here due to the None check
                        out_expected.append(
                            f'<div class="diff-line ins">{self._format_text(e_line)}</div>'
                        )

        return "\n".join(out_actual), "\n".join(out_expected)

    def _highlight_words(self, a_line: str, e_line: str) -> Tuple[str, str]:
        """Highlight character/word differences within a replaced line."""
        # Simple word-based diff
        a_words = a_line.split(" ")
        e_words = e_line.split(" ")

        matcher = difflib.SequenceMatcher(None, a_words, e_words)
        a_out: List[str] = []
        e_out: List[str] = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                a_out.extend(html.escape(w) for w in a_words[i1:i2])
                e_out.extend(html.escape(w) for w in e_words[j1:j2])
            elif tag == "replace":
                a_out.append(
                    f'<span class="word-del">{" ".join(map(html.escape, a_words[i1:i2]))}</span>'
                )
                e_out.append(
                    f'<span class="word-ins">{" ".join(map(html.escape, e_words[j1:j2]))}</span>'
                )
            elif tag == "delete":
                a_out.append(
                    f'<span class="word-del">{" ".join(map(html.escape, a_words[i1:i2]))}</span>'
                )
            elif tag == "insert":
                e_out.append(
                    f'<span class="word-ins">{" ".join(map(html.escape, e_words[j1:j2]))}</span>'
                )

        return " ".join(a_out), " ".join(e_out)

    def _format_text(self, text: str) -> str:
        """Escape HTML and apply basic formatting."""
        if not text:
            return "&nbsp;"  # Maintain line height
        return html.escape(text)

    def _generate_html(self) -> str:
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        pass_rate = (passed / total * 100) if total > 0 else 0
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # JSON data removed as it's not currently used in the HTML output

        return f"""<!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Test Assurance Report</title>
                        <link rel="preconnect" href="https://fonts.googleapis.com">
                        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
                        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
                        <style>
                            :root {{
                                --primary: #4F46E5;
                                --primary-light: #EEF2FF;
                                --success: #10B981;
                                --success-bg: #ECFDF5;
                                --danger: #EF4444;
                                --danger-bg: #FEF2F2;
                                --text-main: #1F2937;
                                --text-muted: #6B7280;
                                --border: #E5E7EB;
                                --bg-body: #F3F4F6;
                                --bg-card: #FFFFFF;
                                
                                --diff-ins-bg: #dcfce7;
                                --diff-ins-text: #166534;
                                --diff-del-bg: #fee2e2;
                                --diff-del-text: #991b1b;
                            }}

                            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
                            
                            body {{
                                font-family: 'Inter', sans-serif;
                                background-color: var(--bg-body);
                                color: var(--text-main);
                                line-height: 1.5;
                                padding-bottom: 40px;
                            }}

                            /* --- Header & Stats --- */
                            .dashboard-header {{
                                background: var(--bg-card);
                                border-bottom: 1px solid var(--border);
                                padding: 20px 40px;
                                position: sticky;
                                top: 0;
                                z-index: 50;
                                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                            }}

                            .header-content {{
                                max-width: 1400px;
                                margin: 0 auto;
                                display: flex;
                                justify-content: space-between;
                                align-items: center;
                            }}

                            .brand h1 {{ font-size: 20px; font-weight: 700; color: #111; display: flex; align-items: center; gap: 10px; }}
                            .brand .timestamp {{ font-size: 13px; color: var(--text-muted); font-weight: 400; margin-left: 10px; }}

                            .stats-grid {{
                                display: grid;
                                grid-template-columns: repeat(4, 1fr);
                                gap: 15px;
                                max-width: 1400px;
                                margin: 30px auto;
                                padding: 0 20px;
                            }}

                            .stat-card {{
                                background: var(--bg-card);
                                padding: 20px;
                                border-radius: 12px;
                                border: 1px solid var(--border);
                                box-shadow: 0 1px 2px rgba(0,0,0,0.05);
                                display: flex;
                                flex-direction: column;
                            }}

                            .stat-label {{ font-size: 13px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }}
                            .stat-value {{ font-size: 28px; font-weight: 700; margin-top: 5px; }}
                            .stat-card.passed .stat-value {{ color: var(--success); }}
                            .stat-card.failed .stat-value {{ color: var(--danger); }}

                            /* --- Controls --- */
                            .controls {{
                                max-width: 1400px;
                                margin: 0 auto 20px;
                                padding: 0 20px;
                                display: flex;
                                gap: 15px;
                                align-items: center;
                            }}

                            .search-bar {{
                                flex: 1;
                                position: relative;
                            }}
                            
                            .search-bar input {{
                                width: 100%;
                                padding: 10px 15px;
                                padding-left: 35px;
                                border-radius: 8px;
                                border: 1px solid var(--border);
                                font-size: 14px;
                                transition: border-color 0.2s;
                            }}
                            .search-bar input:focus {{ outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }}
                            .search-icon {{ position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: var(--text-muted); }}

                            .filter-btn {{
                                padding: 8px 16px;
                                border-radius: 8px;
                                border: 1px solid var(--border);
                                background: var(--bg-card);
                                cursor: pointer;
                                font-size: 14px;
                                font-weight: 500;
                                color: var(--text-muted);
                                transition: all 0.2s;
                            }}
                            .filter-btn:hover {{ background: #F9FAFB; }}
                            .filter-btn.active {{ background: var(--text-main); color: white; border-color: var(--text-main); }}

                            /* --- Test Cases --- */
                            .test-list {{ max-width: 1400px; margin: 0 auto; padding: 0 20px; display: flex; flex-direction: column; gap: 15px; }}

                            .test-card {{
                                background: var(--bg-card);
                                border-radius: 12px;
                                border: 1px solid var(--border);
                                overflow: hidden;
                                transition: transform 0.2s, box-shadow 0.2s;
                            }}
                            
                            .test-header {{
                                padding: 15px 20px;
                                display: flex;
                                align-items: center;
                                justify-content: space-between;
                                cursor: pointer;
                                background: #FAFAFA;
                                border-bottom: 1px solid transparent;
                            }}
                            .test-header:hover {{ background: #F3F4F6; }}
                            .test-card.expanded .test-header {{ border-bottom-color: var(--border); }}

                            .test-info {{ display: flex; align-items: center; gap: 15px; }}
                            .test-id {{ font-family: 'JetBrains Mono', monospace; font-size: 13px; background: #E5E7EB; padding: 4px 8px; border-radius: 4px; color: #374151; }}
                            .test-title {{ font-weight: 600; font-size: 15px; color: var(--text-main); }}
                            
                            .status-badge {{
                                padding: 4px 12px;
                                border-radius: 99px;
                                font-size: 12px;
                                font-weight: 700;
                                text-transform: uppercase;
                            }}
                            .status-badge.passed {{ background: var(--success-bg); color: var(--success); }}
                            .status-badge.failed {{ background: var(--danger-bg); color: var(--danger); }}

                            .test-body {{
                                display: none;
                                padding: 20px;
                                animation: slideDown 0.2s ease-out;
                            }}
                            .test-card.expanded .test-body {{ display: block; }}

                            @keyframes slideDown {{ from {{ opacity: 0; transform: translateY(-10px); }} to {{ opacity: 1; transform: translateY(0); }} }}

                            .prompt-box {{
                                background: #F8FAFC;
                                border: 1px solid var(--border);
                                border-radius: 8px;
                                padding: 15px;
                                margin-bottom: 20px;
                                position: relative;
                            }}
                            
                            .section-label {{ font-size: 12px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; margin-bottom: 8px; display: block; }}
                            .prompt-text {{ font-family: 'Inter', sans-serif; font-size: 15px; color: #334155; white-space: pre-wrap; }}

                            .comparison-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
                            
                            .panel {{ border: 1px solid var(--border); border-radius: 8px; overflow: hidden; display: flex; flex-direction: column; }}
                            .panel-header {{
                                padding: 10px 15px;
                                font-size: 13px;
                                font-weight: 600;
                                background: #F9FAFB;
                                border-bottom: 1px solid var(--border);
                                display: flex;
                                justify-content: space-between;
                                align-items: center;
                            }}
                            .panel.actual .panel-header {{ border-top: 3px solid var(--danger); }}
                            .panel.expected .panel-header {{ border-top: 3px solid var(--success); }}

                            .code-content {{
                                padding: 15px;
                                font-family: 'JetBrains Mono', monospace;
                                font-size: 13px;
                                line-height: 1.6;
                                background: #fff;
                                overflow-x: auto;
                                min-height: 100px;
                            }}

                            /* Diff Styling */
                            .diff-line {{ padding: 0 4px; border-radius: 2px; }}
                            .diff-line.del {{ background: var(--diff-del-bg); color: var(--diff-del-text); text-decoration: line-through; opacity: 0.8; }}
                            .diff-line.ins {{ background: var(--diff-ins-bg); color: var(--diff-ins-text); }}
                            .diff-line.replace {{ background: #fff7ed; color: #c2410c; }}
                            
                            .word-del {{ background: #fecaca; text-decoration: line-through; }}
                            .word-ins {{ background: #bbf7d0; }}

                            .copy-btn {{
                                background: transparent;
                                border: 1px solid var(--border);
                                border-radius: 4px;
                                padding: 4px 8px;
                                font-size: 11px;
                                cursor: pointer;
                                color: var(--text-muted);
                            }}
                            .copy-btn:hover {{ background: #F3F4F6; color: var(--primary); border-color: var(--primary); }}

                            .scores {{ margin-top: 15px; display: flex; gap: 15px; font-size: 13px; }}
                            .score-pill {{ background: #F3F4F6; padding: 4px 10px; border-radius: 4px; font-weight: 500; color: #4B5563; }}
                            
                            @media (max-width: 768px) {{
                                .stats-grid {{ grid-template-columns: 1fr 1fr; }}
                                .comparison-grid {{ grid-template-columns: 1fr; }}
                            }}
                        </style>
                    </head>
                    <body>

                        <header class="dashboard-header">
                            <div class="header-content">
                                <div class="brand">
                                    <h1>Test Report <span class="timestamp">{timestamp}</span></h1>
                                </div>
                                <div>
                                    </div>
                            </div>
                        </header>

                        <div class="stats-grid">
                            <div class="stat-card">
                                <span class="stat-label">Total Tests</span>
                                <span class="stat-value">{total}</span>
                            </div>
                            <div class="stat-card passed">
                                <span class="stat-label">Passed</span>
                                <span class="stat-value">{passed}</span>
                            </div>
                            <div class="stat-card failed">
                                <span class="stat-label">Failed</span>
                                <span class="stat-value">{failed}</span>
                            </div>
                            <div class="stat-card">
                                <span class="stat-label">Pass Rate</span>
                                <span class="stat-value">{pass_rate:.1f}%</span>
                            </div>
                        </div>

                        <div class="controls">
                            <div class="search-bar">
                                <span class="search-icon">🔍</span>
                                <input type="text" id="searchInput" placeholder="Search by ID, prompt, or content...">
                            </div>
                            <button class="filter-btn active" onclick="filterTests('all', this)">All</button>
                            <button class="filter-btn" onclick="filterTests('passed', this)">Passed</button>
                            <button class="filter-btn" onclick="filterTests('failed', this)">Failed</button>
                            <button class="filter-btn" onclick="toggleAllDetails()">Toggle Details</button>
                        </div>

                        <div class="test-list" id="testList">
                            {self._render_test_cases()}
                        </div>

                        <script>
                            function toggleTest(header) {{
                                header.parentElement.classList.toggle('expanded');
                            }}

                            function toggleAllDetails() {{
                                const cards = document.querySelectorAll('.test-card');
                                const anyCollapsed = Array.from(cards).some(c => !c.classList.contains('expanded'));
                                
                                cards.forEach(card => {{
                                    if (anyCollapsed) card.classList.add('expanded');
                                    else card.classList.remove('expanded');
                                }});
                            }}

                            function filterTests(status, btn) {{
                                // Update buttons
                                if(btn) {{
                                    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                                    btn.classList.add('active');
                                }}

                                const cards = document.querySelectorAll('.test-card');
                                cards.forEach(card => {{
                                    const isPassed = card.getAttribute('data-status') === 'true';
                                    if (status === 'all') card.style.display = 'block';
                                    else if (status === 'passed' && isPassed) card.style.display = 'block';
                                    else if (status === 'failed' && !isPassed) card.style.display = 'block';
                                    else card.style.display = 'none';
                                }});
                            }}

                            // Search Functionality
                            document.getElementById('searchInput').addEventListener('input', (e) => {{
                                const term = e.target.value.toLowerCase();
                                const cards = document.querySelectorAll('.test-card');
                                
                                cards.forEach(card => {{
                                    const text = card.innerText.toLowerCase();
                                    if(text.includes(term)) {{
                                        card.style.display = 'block';
                                    }} else {{
                                        card.style.display = 'none';
                                    }}
                                }});
                            }});

                            function copyToClipboard(text, btn) {{
                                navigator.clipboard.writeText(text).then(() => {{
                                    const original = btn.innerText;
                                    btn.innerText = 'Copied!';
                                    setTimeout(() => btn.innerText = original, 1500);
                                }});
                            }}
                        </script>
                    </body>
                    </html>
            """

    def _render_test_cases(self) -> str:
        html_out = ""
        for result in self.results:
            diff_actual, diff_expected = self._highlight_differences(
                result.actual_response, result.expected_response
            )

            # Escape for JS copy attribute
            safe_prompt = html.escape(result.prompt).replace("'", "&apos;")

            similarity_html = ""
            if result.similarity_score is not None:
                similarity_html = f'<div class="score-pill">Similarity: {result.similarity_score:.2f}</div>'

            html_out += f"""
        <div class="test-card" data-status="{str(result.passed).lower()}">
            <div class="test-header" onclick="toggleTest(this)">
                <div class="test-info">
                    <span class="test-id">{result.test_id}</span>
                    <span class="test-title">{result.prompt[:60]}...</span>
                </div>
                <span class="status-badge {"passed" if result.passed else "failed"}">
                    {"PASSED" if result.passed else "FAILED"}
                </span>
            </div>
            <div class="test-body">
                <div class="prompt-box">
                    <div style="display:flex; justify-content:space-between;">
                        <span class="section-label">Prompt</span>
                        <button class="copy-btn" onclick="copyToClipboard('{safe_prompt}', this)">Copy</button>
                    </div>
                    <div class="prompt-text">{html.escape(result.prompt)}</div>
                </div>

                <div class="comparison-grid">
                    <div class="panel actual">
                        <div class="panel-header">
                            <span>Actual Response</span>
                        </div>
                        <div class="code-content">{diff_actual}</div>
                    </div>
                    <div class="panel expected">
                        <div class="panel-header">
                            <span>Expected Response</span>
                        </div>
                        <div class="code-content">{diff_expected}</div>
                    </div>
                </div>
                
                <div class="scores">
                    {similarity_html}
                    {f'<div class="score-pill">Neg. Sim: {result.negative_similarity_score:.2f}</div>' if result.negative_similarity_score else ""}
                    {f'<div class="score-pill">Category: {result.category}</div>' if result.category else ""}
                </div>
            </div>
        </div>
"""
        return html_out

    def generate_report(self, filename: str | None = None) -> Path:
        """Generate and save the HTML report."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_report_{timestamp}.html"

        if not filename.endswith(".html"):
            filename += ".html"

        report_path = self.output_dir / filename
        with report_path.open("w", encoding="utf-8") as f:
            f.write(self._generate_html())

        return report_path


if __name__ == "__main__":
    # Example usage for testing the look
    gen = TestReportGenerator()

    # 1. Passed Case
    gen.add_result(
        TestResult(
            test_id="TC-001",
            prompt="What is 2+2?",
            actual_response="The sum is 4.",
            expected_response="The sum is 4.",
            passed=True,
            similarity_score=1.0,
        )
    )

    # 2. Failed Case with Diff
    gen.add_result(
        TestResult(
            test_id="TC-002",
            prompt="List the primary colors.",
            actual_response="Red\nBlue\nGreen\nYellow",
            expected_response="Red\nBlue\nYellow",
            passed=False,
            similarity_score=0.75,
            category="Knowledge",
        )
    )

    # 3. Complex Text Diff
    gen.add_result(
        TestResult(
            test_id="TC-003",
            prompt="Explain JSON.",
            actual_response="JSON (JavaScript Object Notation) is a lightweight data-interchange format.\nIt is easy for humans to read and write.",
            expected_response="JSON (JavaScript Object Notation) is a heavy data format.\nIt is difficult for humans to read.",
            passed=False,
            similarity_score=0.45,
        )
    )

    path = gen.generate_report("demo_report.html")
    print(f"Report generated at: {path.absolute()}")
