from __future__ import annotations

import contextlib
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from dacheck import core
from tools import build_notebooks as nb
from tools import build_site as site


class CheckerTests(unittest.TestCase):
    def setUp(self):
        self.registry = dict(core._REGISTRY)
        self.loaded = core._LOADED
        core._LOADED = True
        self.env = patch.dict(os.environ, {"DACHECK_STRICT": "0", "DACHECK_NO_PROGRESS": "1"})
        self.env.start()
        self.output = contextlib.redirect_stdout(io.StringIO())
        self.output.__enter__()
        core.register("test.1", title="测试数字")(lambda answer: core.expect_equal(answer, 3))

    def tearDown(self):
        self.output.__exit__(None, None, None)
        self.env.stop()
        core._REGISTRY.clear()
        core._REGISTRY.update(self.registry)
        core._LOADED = self.loaded

    def test_correct_and_wrong_answers(self):
        self.assertTrue(core.check("test.1", 3))
        self.assertFalse(core.check("test.1", 4))
        self.assertFalse(core.check("test.1", "3"))

    def test_blank_and_unknown_are_guided(self):
        self.assertFalse(core.check("test.1", ...))
        self.assertFalse(core.check("test.1", {"answer": [...]}))
        self.assertFalse(core.check("missing.1", 3))

    def test_strict_mode_rejects_failed_and_blank_checks(self):
        with patch.dict(os.environ, {"DACHECK_STRICT": "1"}):
            with self.assertRaises(core.CheckFail):
                core.check("test.1", 4)
            with self.assertRaises(core.CheckFail):
                core.check("test.1", ...)
            with self.assertRaises(core.CheckFail):
                core.check("missing.1", 3)

    def test_no_progress_mode_preserves_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "progress.json"
            path.write_text('{"existing.1": 123}', encoding="utf-8")
            with patch.object(core, "PROGRESS_FILE", path):
                core.check("test.1", 3)
                self.assertEqual(path.read_text(encoding="utf-8"), '{"existing.1": 123}')

    def test_dataframe_values_missing_and_order(self):
        expected = pd.DataFrame({"name": ["a", "b"], "value": [1.2, None]})
        core.expect_df(expected.copy(), expected)
        core.expect_df(expected[["value", "name"]], expected)
        with self.assertRaisesRegex(core.CheckFail, "行的顺序"):
            core.expect_df(expected.iloc[::-1], expected)
        core.expect_df(expected.iloc[::-1], expected, check_order=False)
        with self.assertRaises(core.CheckFail):
            core.expect_df(pd.DataFrame({"name": ["a", "b"], "value": [2, None]}), expected)

    def test_series_checks_labels_and_numeric_tolerance(self):
        expected = pd.Series([1.0, 2.0], index=["a", "b"])
        core.expect_series(expected + 1e-8, expected)
        with self.assertRaises(core.CheckFail):
            core.expect_series(expected.reset_index(drop=True), expected)


class NotebookSourceTests(unittest.TestCase):
    def test_student_and_solution_separate(self):
        source = 'before = 1\n### BEGIN SOLUTION\nanswer = 3\n### STUDENT\nanswer = ...\n### END SOLUTION\ncheck("test.1", answer)'
        student, solution, has_block = nb.split_solution(source)
        self.assertTrue(has_block)
        self.assertIn("answer = ...", student)
        self.assertNotIn("answer = 3", student)
        self.assertIn("answer = 3", solution)
        self.assertNotIn("...", solution)
        self.assertIn("before = 1", student)
        self.assertIn("check(", solution)

    def test_unclosed_solution_fails(self):
        with self.assertRaises(ValueError):
            nb.split_solution("### BEGIN SOLUTION\nx = 1")

    def test_other_fences_are_markdown(self):
        cells = nb.parse("# Title\n```text\nnot executable\n```\n+++\n```python\nx = 1\n```\n")
        self.assertEqual([kind for kind, _, _ in cells], ["markdown", "code"])
        self.assertIn("not executable", cells[0][1])

    def test_only_tags_and_output_metadata(self):
        source = '# Example\n```python student-only\nstudent = 1\n```\n```python solution-only\nsolution = 2\n```\n'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.md"
            path.write_text(source, encoding="utf-8")
            student, solution, _ = nb.build(path)
        student_code = "\n".join(c.source for c in student.cells if c.cell_type == "code")
        solution_code = "\n".join(c.source for c in solution.cells if c.cell_type == "code")
        self.assertIn("student = 1", student_code)
        self.assertNotIn("solution = 2", student_code)
        self.assertIn("solution = 2", solution_code)
        self.assertNotIn("student = 1", solution_code)
        self.assertEqual(student.metadata.kernelspec.name, "da-course")
        self.assertTrue(all(not c.get("outputs") for c in student.cells))


class SiteSourceTests(unittest.TestCase):
    def setUp(self):
        site.WARNINGS.clear()

    def render(self, source):
        ctx = site.Ctx("test")
        return site.postprocess(site.md_to_html(site.process_containers(source, ctx)), {}, ctx, "../")

    def test_nested_containers_and_fenced_literals(self):
        source = ':::cards\n:::card First\nText\n:::fold Answer\n```python\ns = ":::warn"\n```\n:::\n:::\n:::\n'
        result = self.render(source)
        self.assertIn('class="cards"', result)
        self.assertIn('class="card"', result)
        self.assertIn('<details class="fold">', result)
        self.assertIn('s =', result)
        self.assertNotIn("DAPLACEHOLDER", result)
        self.assertFalse(site.WARNINGS)

    def test_steps_tables_quiz_and_unicode_heading(self):
        result = self.render('## 中文标题\n:::steps\n:::step Start\nOne\n:::\n:::\n\n| a | b |\n|---|---|\n| 1 | 2 |\n\n:::quiz\nQuestion?\n- [ ] Wrong\n- [x] Right\n---\nExplanation\n:::\n')
        self.assertIn('<li class="step">', result)
        self.assertIn('class="table-wrap"', result)
        self.assertEqual(result.count('data-correct="1"'), 1)
        self.assertFalse(site.WARNINGS)

    def test_quiz_title_is_not_lost(self):
        result = self.render(':::quiz 哪一步才是激活环境？\n- [ ] create\n- [x] activate\n---\n解释\n:::\n')
        self.assertIn('<p class="quiz-q">哪一步才是激活环境？</p>', result)
        self.assertEqual(result.count('data-correct="1"'), 1)


if __name__ == "__main__":
    unittest.main()
