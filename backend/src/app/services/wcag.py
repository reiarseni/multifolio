import re

EXTERNAL_ASSET_PATTERN = re.compile(r"(url\s*\(|https?://)", re.IGNORECASE)

WCAG_PAIRS = [
    ("primary", "background"),
    ("text_heading", "background"),
    ("text_body", "background"),
    ("text_muted", "background"),
    ("accent", "background"),
    ("primary", "surface"),
    ("text_heading", "surface"),
    ("text_body", "surface"),
]


def luminance(hex_color: str) -> float:
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    r, g, b = (int(hex_color[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
    linear = []
    for c in (r, g, b):
        linear.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(color1: str, color2: str) -> float:
    l1 = luminance(color1)
    l2 = luminance(color2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def validate_wcag(tokens: dict) -> list[str]:
    errors = []
    color_tokens = tokens.get("color", {})

    for fg_key, bg_key in WCAG_PAIRS:
        fg = color_tokens.get(fg_key)
        bg = color_tokens.get(bg_key)
        if not fg or not bg:
            continue
        ratio = contrast_ratio(fg, bg)
        if ratio < 4.5:
            errors.append(
                f"Par {fg_key}/{bg_key} no cumple WCAG AA "
                f"(ratio {ratio:.1f}, minimo 4.5:1)"
            )

    return errors


def validate_external_assets(tokens: dict) -> list[str]:
    errors = []
    for group_name, group in tokens.items():
        if not isinstance(group, dict):
            continue
        for key, value in group.items():
            if isinstance(value, str) and EXTERNAL_ASSET_PATTERN.search(value):
                errors.append(
                    f"Token {group_name}.{key} contiene asset externo: {value}"
                )
    return errors
