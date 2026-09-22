"""Generate a print-ready QR code for the site URL.

Usage:
    pip install "qrcode[pil]"
    python scripts/generate_qr.py             # uses SITE_URL and EVENT_CODE from env
    python scripts/generate_qr.py --url https://foo.example  --code MYCODE

Outputs:
    scripts/out/capture_qr.png  (branded PNG, ~1200x1600, ready to print)
    scripts/out/capture_qr.svg  (vector, best for banners)
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from urllib.parse import urlencode, urlparse

try:
    import qrcode
    from qrcode.image.styledpil import StyledPilImage
    from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer
    from qrcode.image.styles.colormasks import SolidFillColorMask
    from qrcode.image.svg import SvgPathImage
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print(
        'Missing dependency. Run: pip install "qrcode[pil]" Pillow',
        file=sys.stderr,
    )
    sys.exit(1)


BLACK = (0, 0, 0)
GOLD = (212, 175, 55)  # #D4AF37
WHITE = (255, 255, 255)


def compose_url(url: str, event_code: str | None) -> str:
    if not event_code:
        return url
    parsed = urlparse(url)
    sep = "&" if parsed.query else "?"
    return f"{url}{sep}{urlencode({'e': event_code})}"


def load_font(size: int) -> ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "/Library/Fonts/Georgia.ttf",
        "C:\\Windows\\Fonts\\georgiab.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def make_png(url: str, out_path: Path, event_name: str) -> None:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=20,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        color_mask=SolidFillColorMask(back_color=WHITE, front_color=BLACK),
    ).convert("RGB")

    # Canvas
    W, H = 1200, 1600
    canvas = Image.new("RGB", (W, H), BLACK)
    draw = ImageDraw.Draw(canvas)

    # gold border
    border = 30
    draw.rectangle(
        [border, border, W - border, H - border],
        outline=GOLD,
        width=6,
    )

    # header
    title_font = load_font(72)
    sub_font = load_font(38)
    action_font = load_font(52)

    title = event_name.upper()
    t_w = draw.textlength(title, font=title_font)
    draw.text(((W - t_w) / 2, 100), title, fill=GOLD, font=title_font)

    sub = "Capture the Moment"
    s_w = draw.textlength(sub, font=sub_font)
    draw.text(((W - s_w) / 2, 200), sub, fill=WHITE, font=sub_font)

    # QR panel: white card with gold rule
    qr_size = 850
    qr_scaled = qr_img.resize((qr_size, qr_size), Image.LANCZOS)
    qr_x = (W - qr_size) // 2
    qr_y = 300
    card_pad = 30
    draw.rectangle(
        [qr_x - card_pad, qr_y - card_pad, qr_x + qr_size + card_pad, qr_y + qr_size + card_pad],
        fill=WHITE,
        outline=GOLD,
        width=4,
    )
    canvas.paste(qr_scaled, (qr_x, qr_y))

    # tagline
    tagline = "SCAN  →  SNAP  →  SHARE"
    t_w = draw.textlength(tagline, font=action_font)
    draw.text(((W - t_w) / 2, qr_y + qr_size + 90), tagline, fill=GOLD, font=action_font)

    canvas.save(out_path, format="PNG", optimize=True)


def make_svg(url: str, out_path: Path) -> None:
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=20,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(image_factory=SvgPathImage)
    with open(out_path, "wb") as fh:
        img.save(fh)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=os.environ.get("SITE_URL"))
    parser.add_argument("--code", default=os.environ.get("EVENT_CODE"))
    parser.add_argument(
        "--event-name", default=os.environ.get("EVENT_NAME") or "Grace's Graduation"
    )
    parser.add_argument("--out-dir", default="scripts/out")
    args = parser.parse_args()

    if not args.url:
        print("Missing --url (or SITE_URL env).", file=sys.stderr)
        return 1

    full_url = compose_url(args.url, args.code)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    png_path = out_dir / "capture_qr.png"
    svg_path = out_dir / "capture_qr.svg"

    make_png(full_url, png_path, args.event_name)
    make_svg(full_url, svg_path)

    print(f"URL encoded: {full_url}")
    print(f"PNG: {png_path}")
    print(f"SVG: {svg_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
