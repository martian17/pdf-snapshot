# PDF Grid Snapshotter

Generate beautiful, slide-ready grid snapshots ("grids eye view") of PDF documents.

## Standalone Usage

Download or build the standalone binary, then run:

```bash
./pdf-snapshot <input_pdf_path> [output_png_path]
```

- If `output_png_path` is not specified, the snapshot is automatically saved in the same directory as the input PDF with a `.png` extension (e.g. `slides.pdf` -> `slides.png`).

### Examples

Generate a snapshot with default optimal layout matching the landscape golden ratio (`1.618`):
```bash
./pdf-snapshot document.pdf
```

Highlight a block of pages in grid coordinates (e.g. outline columns 1 and 2 in red):
```bash
./pdf-snapshot sample.pdf output_grid.png --preset reference --demarcate-grid-block 1,1,1,2
```

## Building the Binary

To compile the standalone executable yourself:

```bash
# 1. Install dependencies and PyInstaller
pip install -r requirements.txt pyinstaller

# 2. Build the executable
pyinstaller --onefile --name pdf-snapshot pdf_snapshot/__main__.py
```

The compiled binary will be generated at `dist/pdf-snapshot`. You can copy it to the root of the project to run it locally:
```bash
cp dist/pdf-snapshot .
```

## Options

Run with `--help` to view all CLI options:
```bash
./pdf-snapshot --help
```

- `-r, --ratio`: Target aspect ratio of the grid (default: 1.618).
- `-w, --page-width`: Thumbnail page width in pixels (default: 120).
- `-d, --dpi`: DPI for rendering PDF pages before downscaling (default: 150).
- `-b, --bg-color`: Background color (hex or color name).
- `--preset`: Layout preset (`reference`, `compact`, or `custom`).
- `-p, --demarcate-pages`: Page ranges to outline (e.g. `1-3,5`).
- `-g, --demarcate-grid-block`: Outline rectangular blocks of pages (e.g. `1,1,7,2`).
- `-s, --demarcate-style`: Custom highlight borders (e.g. `color=blue,width=4,padding=6`).

Refer to [docs/API.md](docs/API.md) for full programmatic Python API usage and development/build details.
