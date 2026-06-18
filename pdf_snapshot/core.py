import os
import math
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFilter

def calculate_grid_layout(num_pages, page_w, page_h, target_ratio=1.618, margin_x=40, margin_y=40, gap_x=20, gap_y=20):
    """
    Finds the optimal number of rows and columns to layout `num_pages` of size page_w x page_h
    such that the total grid aspect ratio is closest to target_ratio.
    """
    best_rows = 1
    best_cols = num_pages
    best_diff = float('inf')
    best_ratio = 1.0
    
    for r in range(1, num_pages + 1):
        c = math.ceil(num_pages / r)
        # Calculate resulting grid dimensions
        width = c * page_w + (c - 1) * gap_x + 2 * margin_x
        height = r * page_h + (r - 1) * gap_y + 2 * margin_y
        ratio = width / height
        diff = abs(ratio - target_ratio)
        if diff < best_diff:
            best_diff = diff
            best_rows = r
            best_cols = c
            best_ratio = ratio
            
    return best_rows, best_cols, best_ratio

def draw_shadow(bg_image, box, radius=6, offset=(2, 3), opacity=60):
    """
    Draws a soft drop shadow behind the page box on bg_image.
    box is (x1, y1, x2, y2).
    """
    x1, y1, x2, y2 = box
    w = x2 - x1
    h = y2 - y1
    
    pad = radius * 2
    # Create shadow mask image
    shadow = Image.new('RGBA', (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)
    # Draw filled rectangle representing the shadow
    draw.rectangle([pad, pad, pad + w, pad + h], fill=(0, 0, 0, opacity))
    # Apply Gaussian blur
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius))
    
    # Paste shadow onto background using its alpha channel as a mask
    bg_image.paste(shadow, (x1 + offset[0] - pad, y1 + offset[1] - pad), shadow)

def parse_page_ranges(range_str):
    """
    Parses comma-separated list of page numbers and ranges.
    E.g. "1-5,10,12-15" -> [1, 2, 3, 4, 5, 10, 12, 13, 14, 15]
    Raises ValueError on invalid formats or negative/zero page numbers.
    """
    pages = set()
    if not range_str:
        return []
    for part in range_str.split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            parts = part.split('-')
            if len(parts) != 2:
                raise ValueError(f"Invalid range format: '{part}'. Must be 'start-end'.")
            start_str, end_str = parts
            try:
                start = int(start_str.strip())
                end = int(end_str.strip())
            except ValueError:
                raise ValueError(f"Invalid page numbers in range: '{part}'.")
            if start > end:
                raise ValueError(f"Range start cannot be greater than end: '{part}'.")
            if start < 1 or end < 1:
                raise ValueError(f"Page numbers must be positive integers: '{part}'.")
            pages.update(range(start, end + 1))
        else:
            try:
                val = int(part)
                if val < 1:
                    raise ValueError()
                pages.add(val)
            except ValueError:
                raise ValueError(f"Invalid page number: '{part}'. Must be a positive integer.")
    return sorted(list(pages))

def parse_demarcation_style(style_str):
    """
    Parses demarcation style string like "color=red,width=3,padding=4".
    Raises ValueError on invalid keys or format.
    """
    style = {}
    if not style_str:
        return style
    for item in style_str.split(','):
        item = item.strip()
        if not item:
            continue
        if '=' not in item:
            raise ValueError(f"Invalid style component '{item}'. Must be in key=value format.")
        key, val = item.split('=', 1)
        key = key.strip().lower()
        val = val.strip()
        if key == 'color':
            style['color'] = val
        elif key in ('width', 'padding'):
            try:
                style[key] = int(val)
            except ValueError:
                raise ValueError(f"Invalid integer value for '{key}': '{val}'")
        else:
            raise ValueError(f"Unknown demarcation style option: '{key}'")
    return style

def create_snapshot(
    pdf_path,
    output_path,
    target_ratio=1.618,
    page_width=120,
    render_dpi=150,
    bg_color="#f0f2f5",
    layout_preset="reference",
    custom_gap_x=None,
    custom_gap_y=None,
    custom_margin=None,
    custom_margin_x=None,
    custom_margin_y=None,
    demarcated_pages=None,
    demarcated_grid_blocks=None,
    demarcation_style=None
):
    """
    Generates a single grid snapshot image of all pages in a PDF.
    """
    if demarcated_pages is None:
        demarcated_pages = []
    if demarcated_grid_blocks is None:
        demarcated_grid_blocks = []
    if demarcation_style is None:
        demarcation_style = {}
        
    # Input parameter validations
    if target_ratio <= 0:
        raise ValueError("target_ratio must be a positive number.")
    if page_width <= 0:
        raise ValueError("page_width must be a positive integer.")
    if render_dpi <= 0:
        raise ValueError("render_dpi must be a positive integer.")
        
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Input PDF file not found: '{pdf_path}'")
        
    # Open the PDF document
    with fitz.open(pdf_path) as doc:
        num_pages = len(doc)
        if num_pages == 0:
            raise ValueError("PDF is empty or cannot be opened.")
            
        # Render first page to get aspect ratio
        zoom = render_dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)
        pix = doc[0].get_pixmap(matrix=mat, colorspace=fitz.csRGB)
        pdf_w, pdf_h = pix.width, pix.height
        
        # Calculate target page size in pixels based on page_width
        pw = page_width
        ph = int(pw * (pdf_h / pdf_w))
        if ph <= 0:
            raise ValueError("Calculated page height must be a positive integer. Check first page aspect ratio.")
        
        # Determine gaps and margins based on layout preset
        if layout_preset == "reference":
            gap_x = int(pw * (68 / 96))
            gap_y = int(pw * (16 / 96))
            margin_x = int(pw * (20 / 96))
            margin_y = int(pw * (15 / 96))
        elif layout_preset == "compact":
            gap_x = int(pw * (20 / 96))
            gap_y = int(pw * (20 / 96))
            margin_x = int(pw * (20 / 96))
            margin_y = int(pw * (20 / 96))
        else:  # custom
            gap_x = custom_gap_x if custom_gap_x is not None else 20
            gap_y = custom_gap_y if custom_gap_y is not None else 20
            if custom_margin is not None:
                margin_x = custom_margin
                margin_y = custom_margin
            else:
                margin_x = custom_margin_x if custom_margin_x is not None else 20
                margin_y = custom_margin_y if custom_margin_y is not None else 20
            
        # Optimize layout
        rows, cols, final_ratio = calculate_grid_layout(num_pages, pw, ph, target_ratio, margin_x, margin_y, gap_x, gap_y)
        
        # Calculate target image dimensions
        img_w = cols * pw + (cols - 1) * gap_x + 2 * margin_x
        img_h = rows * ph + (rows - 1) * gap_y + 2 * margin_y
        
        # Create background image
        snapshot = Image.new('RGB', (img_w, img_h), bg_color)
        
        # Render and downsample all pages (handling potential orientation/size differences via letterboxing)
        pages_imgs = []
        for idx in range(num_pages):
            page = doc[idx]
            p_pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
            p_img = Image.frombytes("RGB", [p_pix.width, p_pix.height], p_pix.samples)
            
            # Scale preserving aspect ratio within (pw, ph) bounding box
            ratio_w = pw / p_pix.width
            ratio_h = ph / p_pix.height
            scale = min(ratio_w, ratio_h)
            new_w = max(1, int(p_pix.width * scale))
            new_h = max(1, int(p_pix.height * scale))
            
            p_img_resized = p_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            # Create a uniform cell container filled with white (standard page color)
            p_cell = Image.new("RGB", (pw, ph), "white")
            dx = (pw - new_w) // 2
            dy = (ph - new_h) // 2
            p_cell.paste(p_img_resized, (dx, dy))
            pages_imgs.append(p_cell)
            
        # Position page cells
        page_coords = {}
        for idx in range(num_pages):
            r = idx // cols
            c = idx % cols
            x1 = margin_x + c * (pw + gap_x)
            y1 = margin_y + r * (ph + gap_y)
            x2 = x1 + pw
            y2 = y1 + ph
            page_coords[idx] = (x1, y1, x2, y2)
            
        # Draw all drop shadows first (prevents any shadow overlapping neighboring page contents)
        for idx in range(num_pages):
            x1, y1, x2, y2 = page_coords[idx]
            shadow_radius = max(3, int(pw * (5 / 96)))
            shadow_offset = (max(1, int(pw * (2 / 96))), max(2, int(pw * (3 / 96))))
            draw_shadow(snapshot, (x1, y1, x2, y2), radius=shadow_radius, offset=shadow_offset, opacity=45)
            
        # Draw page thumbnails and borders
        draw = ImageDraw.Draw(snapshot)
        for idx in range(num_pages):
            x1, y1, x2, y2 = page_coords[idx]
            snapshot.paste(pages_imgs[idx], (x1, y1))
            draw.rectangle([x1, y1, x2 - 1, y2 - 1], outline=(200, 200, 200), width=1)
            
        # Draw demarcations
        # Determine defaults for demarcation style based on layout preset
        if layout_preset == "reference":
            default_color = '#c90601'  # exact reference red
            default_width = 3
            default_padding = 8
        else:
            default_color = '#dc3545'
            default_width = 3
            default_padding = 4
            
        border_color = demarcation_style.get('color', default_color)
        border_width = demarcation_style.get('width', default_width)
        border_padding = demarcation_style.get('padding', default_padding)
        
        # 1. Page-level demarcations
        for p_num in demarcated_pages:
            idx = p_num - 1
            if 0 <= idx < num_pages:
                x1, y1, x2, y2 = page_coords[idx]
                bx1 = x1 - border_padding
                by1 = y1 - border_padding
                bx2 = x2 + border_padding
                by2 = y2 + border_padding
                draw.rectangle([bx1, by1, bx2 - 1, by2 - 1], outline=border_color, width=border_width)
                
        # 2. Block-level demarcations (grid coordinates: r1, c1, r2, c2)
        for r1, c1, r2, c2 in demarcated_grid_blocks:
            # Sort inputs to handle r1 > r2 or c1 > c2 correctly
            r_start, r_end = min(r1, r2), max(r1, r2)
            c_start, c_end = min(c1, c2), max(c1, c2)
            
            # Clamp coordinates to actual grid dimensions to prevent out-of-bounds drawing
            r1_idx = max(0, min(r_start - 1, rows - 1))
            c1_idx = max(0, min(c_start - 1, cols - 1))
            r2_idx = max(0, min(r_end - 1, rows - 1))
            c2_idx = max(0, min(c_end - 1, cols - 1))
            
            bx1 = margin_x + c1_idx * (pw + gap_x) - border_padding
            by1 = margin_y + r1_idx * (ph + gap_y) - border_padding
            bx2 = margin_x + c2_idx * (pw + gap_x) + pw + border_padding
            by2 = margin_y + r2_idx * (ph + gap_y) + ph + border_padding
            
            draw.rectangle([bx1, by1, bx2 - 1, by2 - 1], outline=border_color, width=border_width)
            
        # Save the output image
        snapshot.save(output_path)
        return rows, cols, final_ratio, img_w, img_h
