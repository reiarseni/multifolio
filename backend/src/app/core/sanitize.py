import re

_DANGEROUS_TAG = re.compile(
    r"<\s*(script|iframe|object|embed|form|input|button|link|style|meta)[^>]*>.*?<\s*/\s*\1\s*>",
    re.IGNORECASE | re.DOTALL,
)
_HTML_TAG = re.compile(r"<[^>]*>")


def sanitize_text(text: str | None) -> str | None:
    if text is None:
        return None
    cleaned = _DANGEROUS_TAG.sub("", text)
    return cleaned


def strip_html(text: str | None) -> str:
    if not text:
        return ""
    return _HTML_TAG.sub("", text)
