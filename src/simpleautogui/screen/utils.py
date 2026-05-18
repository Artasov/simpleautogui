import re

import webcolors


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.strip().lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join(channel * 2 for channel in hex_color)
    if len(hex_color) != 6:
        raise ValueError(f'Invalid hex color: {hex_color}')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def parse_color(color: str | tuple[int, int, int] | list[int]) -> tuple[int, int, int]:
    if isinstance(color, (tuple, list)):
        if len(color) != 3:
            raise ValueError(f'Color must contain exactly 3 channels: {color}')
        rgb = tuple(int(channel) for channel in color)
    elif isinstance(color, str):
        color = color.strip()
        if color.startswith('#'):
            rgb = hex_to_rgb(color)
        elif color.lower().startswith('rgb'):
            channels = re.findall(r'\d+', color)
            if len(channels) != 3:
                raise ValueError(f'Invalid rgb color: {color}')
            rgb = tuple(int(channel) for channel in channels)
        else:
            rgb = webcolors.name_to_rgb(color.lower())
            rgb = (rgb.red, rgb.green, rgb.blue)
    else:
        raise TypeError(f'{color} color is not a tuple(r, g, b) or string color')

    if any(channel < 0 or channel > 255 for channel in rgb):
        raise ValueError(f'Color channels must be between 0 and 255: {rgb}')
    return rgb
