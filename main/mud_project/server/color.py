import re

def convert_ansi_color(match: re.Match, supportansi: bool = False, support256: bool = False, supportRGB: bool = False) -> str:
    escapecode: str = match.group(1)
    base = 40 if escapecode.startswith('#') else 30
    escapecode = escapecode.lstrip('#')
    bold = escapecode.isupper()
    color_map = {
        'r': 1, 'g': 2, 'b': 4, 'y': 3, 'm': 5, 'c': 6, 'd': 0, 'w': 7
    }
    special_chars = {
        '{': '{', '\\': '\\', 'n': '\n', 't': '\t',
        'x': '\x1b[0m' if supportansi else "",
        '!': '\x1b[7m' if supportansi else "",
        '*': '\x1b[5m' if supportansi else "",
        'f': '\x1b[5m' if supportansi else "",
        '_': '\x1b[4m' if supportansi else ""
    }
    
    if escapecode.lower() in special_chars:
        return special_chars[escapecode.lower()]
    
    if escapecode.lower().startswith('e'):
        return convert_256_color(escapecode[1:], base, support256)
    
    if escapecode.lower().startswith('&'):
        return convert_rgb_color(escapecode[1:], base, supportRGB)
    
    color = color_map.get(escapecode.lower())
    if color is not None:
        if not supportansi:
            return ""
        else:
            return f"\x1b[{1 if bold else 0};{base + color}m"
    
    return match.group(0)  # Return the original match if no conversion is possible

def convert_256_color(color_code: str, base: int,  support256: bool) -> str:
    if not support256:
        return ""
    color = int(color_code.split(';')[0])
    base += 8
    return f"\x1b[{base};5;{color:02d}m"

def convert_rgb_color(color_code: str, base:int, supportRGB: bool) -> str:
    if not supportRGB:
        return ""
    color_code = color_code.rstrip(";")
    color = int(color_code, 16)
    r, g, b = color >> 16 & 0xFF, color >> 8 & 0xFF, color & 0xFF
    base += 8
    return f"\x1b[{base};2;{r:02d};{g:02d};{b:02d}m"

def colorize(text: str, supportansi: bool = True, support256: bool = True, supportRGB: bool = True) -> str:
    if '\\' in text or '{' in text:
        pattern = r'[\\{](#?[ntdrgybcmwx\\{*f!_|[NTDRGYBCMWX]|#?e\d{1,3};?|#?&[0-9A-Fa-f]{6};?)'
        colorized = re.sub(pattern, lambda m: convert_ansi_color(m, supportansi, support256, supportRGB), text)
        return colorized
    return text

def escape_color(text: str) -> str:
    return text.replace('\\', '\\\\').replace("{", "{{")