"""Image validation using magic bytes. No system libmagic needed."""

# 4MB soft cap below Vercel's 4.5MB body limit.
MAX_SIZE = 4 * 1024 * 1024


def sniff(data: bytes) -> tuple[str, str] | None:
    if len(data) >= 3 and data.startswith(b"\xff\xd8\xff"):
        return ("image/jpeg", "jpg")
    if len(data) >= 8 and data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ("image/png", "png")
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ("image/webp", "webp")
    return None


def validate(data: bytes) -> str:
    """Return the sniffed MIME type or raise ValueError."""
    if not data:
        raise ValueError("empty file")
    if len(data) > MAX_SIZE:
        raise ValueError(
            f"file too large: {len(data)} bytes (max {MAX_SIZE // 1024 // 1024} MB)"
        )
    hit = sniff(data)
    if not hit:
        raise ValueError("unsupported image type (must be JPEG / PNG / WebP)")
    return hit[0]
