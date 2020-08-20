# from PIL import Image, ImageDraw, ImageFont, features
# print(features.check('raqm'))
# font = ImageFont.truetype(
#     'werk24/assets/fonts/STIX2Text-Regular.otf',
#     30,
#     # layout_engine=ImageFont.LAYOUT_RAQM
# )

# text = "⌖"
# img = Image.new('RGB', (100, 100))
# draw = ImageDraw.Draw(img)
# draw.text((0, 0), text, "white", font=font)
# img.show()

from werk24.models.gdt import W24GDTCharacteristic
blurb = "[⌓|A|B]"
trans_table = str.maketrans(
    {k.value: k.name for k in W24GDTCharacteristic if len(k.value) == 1})
blurb = blurb.translate(trans_table)
#     str.maketrans({k.value: k.name for k in W24GDTCharacteristic}))
print(blurb)
