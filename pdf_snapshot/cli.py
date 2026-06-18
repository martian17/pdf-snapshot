import argparse
import sys
from .core import create_snapshot, parse_page_ranges, parse_demarcation_style

def parse_grid_block(block_str):
    try:
        parts = block_str.split(',')
        if len(parts) != 4:
            raise argparse.ArgumentTypeError("Grid block must be 4 integers in format: r1,c1,r2,c2")
        coords = tuple(int(x.strip()) for x in parts)
        if any(c < 1 for c in coords):
            raise argparse.ArgumentTypeError("Grid block coordinates must be positive integers starting from 1")
        return coords
    except argparse.ArgumentTypeError:
        raise
    except Exception:
        raise argparse.ArgumentTypeError("Grid block must be 4 integers separated by commas (e.g., 1,1,7,2)")

def main():
    parser = argparse.ArgumentParser(
        description="PDF Grid Snapshotter: Generates a slide-ready 'grids eye view' of a PDF document."
    )
    
    parser.add_argument("pdf_path", help="Path to the input PDF file.")
    parser.add_argument(
        "output_path",
        nargs="?",
        help="Path where the output PNG should be saved. If not specified, defaults to the input PDF filename with a .png extension."
    )
    
    parser.add_argument(
        "-r", "--ratio",
        type=float,
        default=1.618,
        help="Target aspect ratio of the grid (default: 1.618, the landscape golden ratio)."
    )
    parser.add_argument(
        "-w", "--page-width",
        type=int,
        default=120,
        help="Target page thumbnail width in pixels (default: 120)."
    )
    parser.add_argument(
        "-d", "--dpi",
        type=int,
        default=150,
        help="Resolution in DPI for rendering PDF pages before downscaling (default: 150)."
    )
    parser.add_argument(
        "-b", "--bg-color",
        help="Background canvas color. Hex values (e.g., '#ffffff') or color names (e.g., 'white') are supported. Defaults to 'white' for 'reference' preset, and '#f0f2f5' otherwise."
    )
    parser.add_argument(
        "--preset",
        choices=["reference", "compact", "custom"],
        default=None,
        help="Layout preset for grid gaps and margins. 'reference' matches the reference spacing, 'compact' is a standard tight spacing, 'custom' allows manually overriding gap/margin sizes (default: 'reference' or 'custom' if custom spacing is provided)."
    )
    parser.add_argument(
        "-gx", "--gap-x",
        type=int,
        help="Custom horizontal spacing between page columns (only used with --preset custom)."
    )
    parser.add_argument(
        "-gy", "--gap-y",
        type=int,
        help="Custom vertical spacing between page rows (only used with --preset custom)."
    )
    parser.add_argument(
        "-m", "--margin",
        type=int,
        help="Custom outer margin around the entire grid canvas (sets both margin-x and margin-y; only used with --preset custom)."
    )
    parser.add_argument(
        "-mx", "--margin-x",
        type=int,
        help="Custom horizontal outer margin (only used with --preset custom)."
    )
    parser.add_argument(
        "-my", "--margin-y",
        type=int,
        help="Custom vertical outer margin (only used with --preset custom)."
    )
    parser.add_argument(
        "-p", "--demarcate-pages",
        help="Page numbers/ranges to outline individually. Supports comma-separated lists and ranges (e.g., '1-5,10,12-14')."
    )
    parser.add_argument(
        "-g", "--demarcate-grid-block",
        type=parse_grid_block,
        action="append",
        dest="demarcated_grid_blocks",
        help="Outline a block of pages in grid coordinates (row_start,col_start,row_end,col_end, 1-indexed). Can be specified multiple times."
    )
    parser.add_argument(
        "-s", "--demarcate-style",
        help="Custom outline styling for page/block demarcation. Format: 'color=hex_or_name,width=int,padding=int' (e.g., 'color=blue,width=4,padding=5')."
    )
    parser.add_argument(
        "--row-major",
        action="store_true",
        help="Layout pages in row-major order (left-to-right, top-to-bottom). Default is column-major order."
    )
    
    args = parser.parse_args()
    
    # Process pages/ranges
    try:
        pages = parse_page_ranges(args.demarcate_pages)
    except ValueError as e:
        parser.error(f"Failed to parse demarcate-pages: {e}")
    
    # Process styling
    try:
        style = parse_demarcation_style(args.demarcate_style)
    except ValueError as e:
        parser.error(f"Failed to parse demarcate-style: {e}")
    
    # Auto-detect preset if not explicitly provided but custom options are specified
    preset = args.preset
    has_custom_opts = any(
        opt is not None for opt in [args.gap_x, args.gap_y, args.margin, args.margin_x, args.margin_y]
    )
    if preset is None:
        preset = "custom" if has_custom_opts else "reference"
    elif preset != "custom" and has_custom_opts:
        parser.error("Custom layout options (--gap-x, --gap-y, --margin, --margin-x, --margin-y) can only be used when --preset is set to 'custom' (or omitted).")
        
    # Dynamic background color selection
    bg_color = args.bg_color
    if bg_color is None:
        bg_color = "white" if preset == "reference" else "#f0f2f5"
        
    output_path = args.output_path
    if not output_path:
        import os
        base, _ = os.path.splitext(args.pdf_path)
        output_path = base + ".png"

    try:
        rows, cols, ratio, w, h = create_snapshot(
            pdf_path=args.pdf_path,
            output_path=output_path,
            target_ratio=args.ratio,
            page_width=args.page_width,
            render_dpi=args.dpi,
            bg_color=bg_color,
            column_major=not args.row_major,
            layout_preset=preset,
            custom_gap_x=args.gap_x,
            custom_gap_y=args.gap_y,
            custom_margin=args.margin,
            custom_margin_x=args.margin_x,
            custom_margin_y=args.margin_y,
            demarcated_pages=pages,
            demarcated_grid_blocks=args.demarcated_grid_blocks,
            demarcation_style=style
        )
        print(f"\nSuccessfully generated PDF Snapshot!")
        print(f"  Grid Dimensions: {rows} rows x {cols} columns")
        print(f"  Canvas Size: {w}px width x {h}px height")
        print(f"  Final Aspect Ratio: {ratio:.3f} (target: {args.ratio})")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
