from .ask import W24Ask


class W24AskThumbnail(W24Ask):
    """ Base model for features that request a
    thumbnail.

    maximal_width and maximal_height describe the maximal
    dimensions of the thumbnail (in pixel).

    Beware that the resulting image dimensions depend
    on many factors, such as:
    (i) resolution of the original image,
    (ii) rotation of the sheet on the page,
    (iii) noise level of the image, etc.

    Setting auto_rotate to True will rotate the image for
    "human-consumption" (the human rotation algorithm is
    more complext than you'd expect)
    """
    # maximal_width: int = 512
    # maximal_height: int = 512
    # auto_rotate: bool = False
