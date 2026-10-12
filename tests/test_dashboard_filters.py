"""In-flow filter layout contracts for the template and generated dashboard.

Browser geometry and keyboard coverage lives in test_dashboard_filters.js.
These standard-library checks also run in the project's offline unittest gate.
"""
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from catalog_surface import dashboard_phone_layout_covers  # noqa: E402


class DashboardFilterLayoutTests(unittest.TestCase):
    def surfaces(self):
        for name in ("scripts/build_dashboard.py", "Jeff Story Song Vault Dashboard.html"):
            yield name, (ROOT / name).read_text()

    @staticmethod
    def rules(text, selector):
        return [dict(re.findall(r"([\w-]+)\s*:\s*([^;{}]+)", body))
                for body in re.findall(re.escape(selector) + r"\s*\{([^{}]*)\}", text)]

    def test_menu_is_in_normal_flow_on_every_surface(self):
        for name, text in self.surfaces():
            with self.subTest(surface=name):
                rules = self.rules(text, ".advanced-menu")
                self.assertTrue(rules)
                for rule in rules:
                    self.assertIn(rule.get("position", "static"), ("static", "relative"))
                    for offset in ("top", "right", "bottom", "left"):
                        self.assertIn(rule.get(offset, "auto"), ("auto", "0"))
                    self.assertNotIn("transform", rule)
                self.assertEqual(rules[0]["width"], "100%")

    def test_expanded_details_reserve_full_row_and_song_toolbar_scrolls(self):
        for name, text in self.surfaces():
            with self.subTest(surface=name):
                self.assertTrue('<div class="controls song-controls">' in text)
                self.assertEqual(self.rules(text, ".song-controls")[0]["position"], "static")
                expanded = self.rules(text, ".advanced-filters[open]")[0]
                self.assertEqual(expanded["flex-basis"], "100%")
                self.assertTrue('<details class="advanced-filters" id="advancedFilters"><summary>More filters</summary>' in text)
                self.assertLess(text.index('id="advancedFilters"'), text.index('id="list"'))

    def test_phone_menu_and_controls_fit_the_available_width(self):
        for name, text in self.surfaces():
            with self.subTest(surface=name):
                self.assertNotIn("@media(max-width:375px)", text)
                self.assertTrue(dashboard_phone_layout_covers(text, 390))
                phone = text.split("@media(max-width:640px){", 1)[1].split("</style>", 1)[0]
                self.assertEqual(self.rules(phone, ".advanced-filters")[0]["width"], "100%")
                self.assertEqual(self.rules(phone, ".advanced-menu")[0].get("grid-template-columns"), "minmax(0,1fr)")
                selects = self.rules(text, ".advanced-menu select")[0]
                self.assertEqual(selects["width"], "100%")
                self.assertEqual(selects["min-width"], "0")

    def test_existing_filter_controls_and_honesty_remain(self):
        for name, text in self.surfaces():
            with self.subTest(surface=name):
                details = text.split('id="advancedFilters"', 1)[1].split("</details>", 1)[0]
                self.assertEqual(re.findall(r'<select id="([^"]+)"', details),
                                 ["proj", "scored", "scope", "evidence", "work", "logicReady"])
                self.assertEqual(len(re.findall(r'<select[^>]+aria-label="[^"]+"', details)), 6)
                for copy in ("Catalog rows are not the official set.",
                             "This page does not open audio.", "WAVs/AIFF/MIDI"):
                    self.assertTrue(copy in text, copy)


if __name__ == "__main__":
    unittest.main()
