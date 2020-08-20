import io
import os
from typing import List, Tuple

from PIL import Image, ImageDraw, ImageFont
from werk24.models.gdt import W24GDT, W24GDTCharacteristic
from werk24.models.measure import W24Measure

path_cur = os.path.dirname(os.path.abspath(__file__))
path_font = os.path.join(
    path_cur,
    "..",
    "assets",
    "fonts",
    "STIX2Text-Regular.otf")
font = ImageFont.truetype(path_font, 30)


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

    for cur_gdt in gdts:

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

        # replace the special characters by something
        # that is more easily digestable
        blurb = cur_gdt.frame.blurb
        trans_table = str.maketrans(
            {k.value: k.name
             for k in W24GDTCharacteristic
             if len(k.value) == 1})
        blurb = blurb.translate(trans_table)

        # cur_measure.label.blurb
        draw.text(
            [x_center, y_center],
            blurb,
            fill=(0, 200, 0),
            font=font)

    return img.tobytes("jpeg", "RGB")


def illustrate_sectional_measures(
        sectional_bytes: bytes,
        measures: List[W24Measure]
) -> bytes:

    # open the image from the bytes buffer
    # and dervice the height and width
    img, draw = _load_image(sectional_bytes)
    width, height = img.size

    for cur_measure in measures:

        # draw a line that corresponds to the
        # measure line
        cur_line = cur_measure.line
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
