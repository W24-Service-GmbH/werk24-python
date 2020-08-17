import io
from typing import Any, Dict, List, Tuple

from PIL import Image, ImageDraw, ImageFont
from werk24.models.gdt import W24GDT
from werk24.models.measure import W24Measure

try:
    font = ImageFont.truetype('arial.ttf', 30)
except IOError:
    font = ImageFont.load_default()


def _load_image(image_bytes: bytes) -> Tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    draw = ImageDraw.Draw(img)
    return img, draw


def illustrate_sectional_gdts(
        sectional_bytes: bytes,
        gdts: List[W24GDT]
) -> bytes:

    # open the image from the bytes buffer
    # and dervice the height and width
    img, draw = _load_image(sectional_bytes)
    width, height = img.size

    for cur_gdt_obj in gdts:
        cur_gdt = W24GDT.parse_obj(cur_gdt_obj)

        # make a shorter handle for the polygon, and
        # make sure that the polygon does exist and
        # has at least 4 points
        poly = cur_gdt.bounding_polygon
        if not poly or len(poly) < 4:
            continue

        # then draw the polygon onto the image
        for pt1, pt2 in zip(poly, poly[1:] + [poly[0]]):
            draw.line(
                [pt1[0] * width, pt1[1] * height,
                 pt2[0] * width, pt2[1] * height],
                fill=(0, 255, 0),
                width=4)

        # now... we want to have a measure label
        # that is on the center coordinate of the
        # measure
        left = min([float("inf")] + [pt[0] for pt in poly])
        top = min([float("inf")] + [pt[1] for pt in poly])
        right = max([0.0] + [pt[0] for pt in poly])
        bottom = max([0.0] + [pt[1] for pt in poly])
        x_center = (left + right) / 2 * width
        y_center = (top + bottom) / 2 * height
        if left == float("inf") or top == float("inf"):
            continue

        # cur_measure.label.blurb
        draw.text(
            [x_center, y_center],
            cur_gdt.frame.blurb,
            fill=(0, 200, 0),
            font=font)

    return img.tobytes("jpeg", "RGB")


def illustrate_sectional_measures(
        sectional_bytes: bytes,
        measures: List[Dict[str, Any]]
) -> bytes:

    # open the image from the bytes buffer
    # and dervice the height and width
    img, draw = _load_image(sectional_bytes)
    width, height = img.size

    for cur_measure_obj in measures:
        # parse the measure as local W24Measure
        cur_measure = W24Measure.parse_obj(cur_measure_obj)
        cur_line = cur_measure.line

        # draw a line that corresponds to the
        # measure line
        draw.line(
            [cur_line[0][0] * width,
             cur_line[0][1] * height,
             cur_line[1][0] * width,
             cur_line[1][1] * height],
            fill=(0, 255, 0),
            width=4)

        # now... we want to have a measure label
        # that is on the center coordinate of the
        # measure
        x_center = (cur_line[0][0] + cur_line[1][0]) / 2 * width
        y_center = (cur_line[0][1] + cur_line[1][1]) / 2 * height
        # cur_measure.label.blurb
        draw.text(
            [x_center, y_center],
            cur_measure.label.blurb,
            fill=(0, 200, 0),
            font=font)

    return img.tobytes("jpeg", "RGB")
