from __future__ import annotations

from io import BytesIO
import re


def qr_svg(value: str) -> str:
    if not value.strip():
        raise ValueError("label value must be nonblank")
    import segno
    out = BytesIO()
    segno.make(value, error="m").save(out, kind="svg", scale=5, border=2)
    return out.getvalue().decode("utf-8")


def code128_svg(value: str) -> str:
    if not value.strip():
        raise ValueError("label value must be nonblank")
    import barcode
    from barcode.writer import SVGWriter
    out = BytesIO()
    barcode.get("code128", value, writer=SVGWriter()).write(out, options={"write_text": True})
    return out.getvalue().decode("utf-8")


def safe_label_kind(kind: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "", (kind or "").lower())
    if normalized in {"qr", "qrcode"}:
        return "qr"
    if normalized in {"barcode", "code128"}:
        return "code128"
    raise ValueError("label kind must be qr or code128")
