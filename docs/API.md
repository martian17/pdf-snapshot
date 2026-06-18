# PDF Grid Snapshotter - Developer & API Documentation

## Installation & Setup

Ensure you have Python 3.8+ installed.

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Install Package Locally
```bash
pip install -e .
```

---

## Python API Usage

You can use this library directly inside Python scripts:

```python
from pdf_snapshot import create_snapshot

rows, cols, final_ratio, img_w, img_h = create_snapshot(
    pdf_path="sample.pdf",
    output_path="output_grid.png",
    target_ratio=1.618,
    page_width=120,
    render_dpi=150,
    bg_color="#f0f2f5",
    layout_preset="reference",
    demarcated_pages=[1, 2],
    demarcation_style={"color": "blue", "width": 4, "padding": 6}
)

print(f"Generated a {rows}x{cols} grid snapshot ({img_w}x{img_h}) with ratio {final_ratio:.3f}.")
```

---

## API Reference

### `create_snapshot(...)`
Exposes the core grid layout and snapshotting rendering:

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `pdf_path` | `str` | *Required* | Path to the input PDF file. |
| `output_path` | `str` | *Required* | Path where the output PNG should be saved. |
| `target_ratio` | `float` | `1.618` | Target aspect ratio of the grid (landscape golden ratio). |
| `page_width` | `int` | `120` | Width of each page thumbnail in pixels. Height scales automatically. |
| `render_dpi` | `int` | `150` | Resolution for rendering PDF pages before scaling down. |
| `bg_color` | `str`/`tuple` | `"#f0f2f5"` | Canvas background color. |
| `layout_preset` | `str` | `"reference"` | Preset spacing: `"reference"`, `"compact"`, or `"custom"`. |
| `custom_gap_x` | `int`/`None` | `None` | Horizontal spacing between page columns (for `"custom"` preset). |
| `custom_gap_y` | `int`/`None` | `None` | Vertical spacing between page rows (for `"custom"` preset). |
| `custom_margin` | `int`/`None` | `None` | Margin around the canvas boundary (for `"custom"` preset). |
| `custom_margin_x` | `int`/`None` | `None` | Horizontal margin (for `"custom"` preset). |
| `custom_margin_y` | `int`/`None` | `None` | Vertical margin (for `"custom"` preset). |
| `demarcated_pages` | `list` | `[]` | List of 1-indexed page indices to highlight. |
| `demarcated_grid_blocks` | `list` | `[]` | List of tuples `(r1, c1, r2, c2)` specifying grid blocks to highlight. |
| `demarcation_style` | `dict` | `{}` | Style configurations: `{"color": "#dc3545", "width": 3, "padding": 4}`. |

---

## Building Standalone Binary

You can compile this tool into a standalone binary using PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile --name pdf-snapshot pdf_snapshot/__main__.py
```

The compiled binary will be located in the `dist/` directory.
