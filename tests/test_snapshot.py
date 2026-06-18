import unittest
import os
import tempfile
from pdf_snapshot.core import calculate_grid_layout, parse_page_ranges, parse_demarcation_style, create_snapshot

class TestPdfSnapshot(unittest.TestCase):
    def test_calculate_grid_layout(self):
        # 69 pages, golden ratio (1.618), reference preset spacing
        rows, cols, ratio = calculate_grid_layout(
            num_pages=69,
            page_w=96,
            page_h=124,
            target_ratio=1.618,
            margin_x=20,
            margin_y=15,
            gap_x=68,
            gap_y=16
        )
        self.assertEqual(rows, 7)
        self.assertEqual(cols, 10)
        self.assertAlmostEqual(ratio, 1.6217303, places=4)
        
    def test_parse_page_ranges(self):
        self.assertEqual(parse_page_ranges("1-3,5"), [1, 2, 3, 5])
        self.assertEqual(parse_page_ranges("10,12-14"), [10, 12, 13, 14])
        self.assertEqual(parse_page_ranges(""), [])
        
        # Exception cases
        with self.assertRaises(ValueError):
            parse_page_ranges("invalid")
        with self.assertRaises(ValueError):
            parse_page_ranges("1-abc")
        with self.assertRaises(ValueError):
            parse_page_ranges("5-1")
        with self.assertRaises(ValueError):
            parse_page_ranges("-1")
            
    def test_parse_demarcation_style(self):
        self.assertEqual(
            parse_demarcation_style("color=blue,width=4,padding=6"),
            {"color": "blue", "width": 4, "padding": 6}
        )
        self.assertEqual(
            parse_demarcation_style("color=#ff0000,width=5"),
            {"color": "#ff0000", "width": 5}
        )
        self.assertEqual(parse_demarcation_style(""), {})
        
        # Exception cases
        with self.assertRaises(ValueError):
            parse_demarcation_style("color=blue,width=abc")
        with self.assertRaises(ValueError):
            parse_demarcation_style("invalid_format")
        with self.assertRaises(ValueError):
            parse_demarcation_style("unknown_key=val")
            
    def test_create_snapshot(self):
        pdf_path = "2601.20927v1.pdf"
        if not os.path.exists(pdf_path):
            self.skipTest("Sample PDF not found")
            
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = os.path.join(tmpdir, "output.png")
            
            # Test successful creation with demarcations and grid blocks (also verifies coord sorting)
            rows, cols, ratio, w, h = create_snapshot(
                pdf_path=pdf_path,
                output_path=out_path,
                target_ratio=1.618,
                page_width=96,
                layout_preset="reference",
                demarcated_grid_blocks=[(7, 2, 1, 1)]  # test coordinates sorting/normalization
            )
            self.assertTrue(os.path.exists(out_path))
            self.assertEqual(rows, 7)
            self.assertEqual(cols, 10)
            self.assertEqual(w, 1612)
            self.assertEqual(h, 994)

            # Test input validation errors
            with self.assertRaises(ValueError):
                create_snapshot(pdf_path, out_path, target_ratio=-1)
            with self.assertRaises(ValueError):
                create_snapshot(pdf_path, out_path, page_width=0)
            with self.assertRaises(ValueError):
                create_snapshot(pdf_path, out_path, render_dpi=-150)
            with self.assertRaises(FileNotFoundError):
                create_snapshot("nonexistent.pdf", out_path)

if __name__ == '__main__':
    unittest.main()
