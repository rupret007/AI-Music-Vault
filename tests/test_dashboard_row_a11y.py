"""Parse actual JS-rendered rows; no browser or third-party dependencies."""
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Element:
    def __init__(self, tag, attrs=(), parent=None):
        self.tag = tag
        self.attrs = dict(attrs)
        self.parent = parent
        self.children = []

    def descendants(self):
        for child in self.children:
            yield child
            yield from child.descendants()

    def has_class(self, name):
        return name in self.attrs.get("class", "").split()

    def interactive(self):
        return (self.tag in {"button", "input", "select", "textarea", "a"}
                or "tabindex" in self.attrs or self.attrs.get("role") == "button")


class Tree(HTMLParser):
    def __init__(self, markup):
        super().__init__()
        self.root = self.current = Element("root")
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        node = Element(tag, attrs, self.current)
        self.current.children.append(node)
        if tag not in {"br", "hr", "input", "meta", "link", "img"}:
            self.current = node

    def handle_endtag(self, tag):
        if self.current.tag != tag:
            raise AssertionError(f"Invalid nesting: closing {tag} inside {self.current.tag}")
        self.current = self.current.parent


class DashboardRowA11yTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "Jeff Story Song Vault Dashboard.html").read_text()
        rendered = subprocess.check_output(
            ["node", str(ROOT / "tests/render_dashboard_fixture.js")], text=True
        )
        cls.rows = list(Tree(rendered).root.children)

    def test_expand_has_no_nested_controls_and_memos_are_siblings(self):
        for row in self.rows:
            head = next(el for el in row.descendants() if "data-toggle-song" in el.attrs)
            self.assertFalse(any(el.interactive() for el in head.descendants()))
            self.assertEqual(head.attrs["role"], "button")
            self.assertEqual(head.attrs["tabindex"], "0")
            self.assertEqual(head.attrs["aria-expanded"], "false")
            detail = next(el for el in row.descendants() if el.has_class("detail"))
            self.assertIn("hidden", detail.attrs)
            self.assertEqual(head.attrs["aria-controls"], detail.attrs["id"])
            siblings = [el for el in head.parent.children if "data-open-memos" in el.attrs]
            self.assertEqual(len(siblings), 1 if row.attrs["data-song-id"] == "TEST-1" else 0)

    def test_dom_tab_order_reaches_memos_then_copy_controls(self):
        controls = [el for el in self.rows[0].descendants() if el.interactive()]
        self.assertIn("data-toggle-song", controls[0].attrs)
        self.assertIn("data-open-memos", controls[1].attrs)
        for control, attr in zip(controls[2:5], ["data-copy-logic", "data-copy-file", "data-copy-work"]):
            self.assertEqual(control.tag, "button")
            self.assertIn(attr, control.attrs)
        self.assertGreaterEqual(len(controls), 5)
        self.assertTrue(all("disabled" not in el.attrs and el.attrs.get("tabindex") != "-1" for el in controls))

    def test_score_names_and_numbers_remain_without_table_roles(self):
        self.assertFalse('role="columnheader"' in self.html, "Score labels must not use table-only roles")
        head = next(el for el in self.rows[0].descendants() if "data-toggle-song" in el.attrs)
        self.assertIn("Potential 75, readiness 40, momentum 65", head.attrs["aria-label"])
        self.assertEqual(len([el for el in head.descendants() if el.has_class("score-lab")]), 3)

    def test_skip_targets_focusable_work_heading_before_work_buttons(self):
        tree = Tree(self.html.split("<script>")[0])
        elements = list(tree.root.descendants())
        skip = next(el for el in elements if el.has_class("skip-link"))
        target = next(el for el in elements if el.attrs.get("id") == skip.attrs["href"][1:])
        self.assertEqual(target.tag, "h2")
        self.assertEqual(target.attrs.get("tabindex"), "-1")
        self.assertEqual(target.attrs["id"], "workNowTitle")
        starts = next(el for el in elements if el.attrs.get("id") == "workStarts")
        self.assertLess(elements.index(target), elements.index(starts))


if __name__ == "__main__":
    unittest.main()
