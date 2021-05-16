""" Defintion of all W24Ask types that are understood by the Werk24 API.
"""
from enum import Enum
from typing import List, Optional, Union

from pydantic import UUID4, BaseModel

from .angle import W24Angle
from .file_format import W24FileFormatThumbnail, W24FileFormatVariantCAD
from .gdt import W24GDT
from .leader import W24Leader
from .measure import W24Measure


class W24AskType(str, Enum):
    """ List of all Ask Type supported by the current
    API version. This list will grow with future releases.

    """
    CANVAS_THUMBNAIL = "CANVAS_THUMBNAIL"
    """ Thumbnail of the canvas (i.e., the part of the
    sheet that contains the geometry)
    """

    PAGE_THUMBNAIL = "PAGE_THUMBNAIL"
    """ Thumbnail of the overall page - rotated and with
    surrounding white space removed
    """

    SECTIONAL_THUMBNAIL = "SECTIONAL_THUMBNAIL"
    """ Thumbnail of a sectional on the canvas.
    Here the sectional describes both cuts and perspectives
    """

    SHEET_THUMBNAIL = "SHEET_THUMBNAIL"
    """ Thumbnail of the sheet (i.e., the part of the
    page that is described by the surrounding frame)
    """

    TRAIN = "TRAIN"
    """ Supplying the request for training only without
    expecting a response.
    """

    VARIANT_ANGLES = "VARIANT_ANGLES"
    """ Requests the all Angles on the variant
    """

    VARIANT_CAD = "VARIANT_CAD"
    """ Requests the generation of a CAD file
    """

    VARIANT_GDTS = "VARIANT_GDTS"
    """ List of Geometric Dimensions and Tolerations detected
    on the Sectionals associated with the variant
    """

    VARIANT_LEADERS = "VARIANT_LEADERS"
    """ List of Leaders that were detected on the Sectional
    """

    VARIANT_MATERIAL = "VARIANT_MATERIAL"
    """ Material that was detected on the data fields of the
    drawing or within a variant table
    """

    VARIANT_MEASURES = "VARIANT_MEASURES"
    """ List of Measures that were found on the Sectionals
    associated with the variant
    """

    TITLE_BLOCK = "TITLE_BLOCK"
    """ Ask for all information that is available on the
    title block
    """


class W24Ask(BaseModel):
    """ Base model from wich all Asks inherit

    Attributes:
        ask_type: Type of the requested Ask. Used
            for deserialization.

        is_training: Flag that indicates that your request
            is a pure training request and that you are not
            expecting to obtain a response.

    !!! note
        When you send a request with the attribute is_training=True
        you are directly improving the quality of our Machine
        Learning Models with regards to your domain. These requests
        are not charged, but they also do not generate a response.
        The connection is immediately closed after you submit the
        request; our system them processes the drawing when the
        system load is low.
    """
    ask_type: W24AskType

    is_training: bool = False


class W24AskThumbnail(W24Ask):
    """ Base model for features that request a thumbnail.

    Attributes:
        file_format: File format in which you wish to obtain
            the result. Currently only JPEG is supported.

    !!! note
        At this stage, the API will return a high-resolution
        gray-level image. Future releases might allow you to
        request color images or to set a resolution limit.
        If this is a priority to you, please let us know.
    """
    file_format: W24FileFormatThumbnail = W24FileFormatThumbnail.JPEG


class W24AskPageThumbnail(W24AskThumbnail):
    """ Requests a thumbnail for each page in the document;
    rotated, and with the surrounding white-space removed.

    !!! note
        We preprocess the page so that it is always white-on-black,
        even when the Technical Drawing that you submitted was
        black-on-white.
    """
    ask_type = W24AskType.PAGE_THUMBNAIL


class W24AskSheetThumbnail(W24AskThumbnail):
    """ Requests a thumbnail of each sheet on each page in
    the document. The sheet will only contain the pixels within
    the main frame that surrounds the canvas and header fields.

    !!! note
        We preprocess the sheet so that it is always white-on-black,
        even when the Technical Drawing that you submitted was
        black-on-white.
    """
    ask_type = W24AskType.SHEET_THUMBNAIL


class W24AskCanvasThumbnail(W24AskThumbnail):
    """ Requests a thumbnail of each canvas in each sheet.
    The canvas describes the "drawing area" of the sheet.

    !!! note
        We preprocess the canvas so that it is always white-on-black,
        even when the Technical Drawing that you submitted was
        black-on-white.
    """
    ask_type = W24AskType.CANVAS_THUMBNAIL


class W24AskSectionalThumbnail(W24AskThumbnail):
    """ The W24AskPlaneThumbnail requests a thumbnail
    of each sectional on each sheet in the document.

    !!! note
        We preprocess the sectional so that it is always white-on-black,
        even when the Technical Drawing that you submitted was
        black-on-white.
    """
    ask_type = W24AskType.SECTIONAL_THUMBNAIL


class W24AskVariantAngles(W24Ask):
    """ With this Ask you are requesting the list of all
    measures that were detected on all sectionals of a
    variant.
    """
    ask_type = W24AskType.VARIANT_ANGLES


class W24AskVariantAnglesResponse(BaseModel):
    """ ResponseType associated with the
    W24AskVariantAngles.

    Attributes:
        variant_id: Unique ID of the variant detected on
            the Technical Drawing. Refer to the documentation
            on Variants for details.

        sectional_id: Unique ID of the sectional on which the
            Angle was detected. This allows you to associate
            the Angle to the SectionalThumbnail (should you
            have requested it).

        angles: List of Angles that were found for the Variant
            on the Sectional.
    """
    variant_id: UUID4
    sectional_id: UUID4
    angles: List[W24Angle]


class W24AskVariantMeasures(W24Ask):
    """ With this Ask you are requesting the complete
    list of all measures that were detected for the
    variant.

    Attributes:
        confidence_min: Werk24 calculates internal
            confidence scores for each measure. Depending
            on your use-case you might want to consider or
            discard low-confidence results. This parameter
            allows you to filter the results. The resulting
            W24Measure objects also contain a confidence score
            that allows you to filter even further.
    """
    ask_type = W24AskType.VARIANT_MEASURES

    confidence_min: float = 0.2


class W24AskVariantMeasuresResponse(BaseModel):
    """ Response object corresponding to the
    W24AskVariantMeasures ask.

    Attributes:
        variant_id: Unique ID of the variant detected on
            the Technical Drawing. Refer to the documentation
            on Variants for details.

        sectional_id: Unique ID of the sectional on which the
            Measure was detected. This allows you to associate
            the Measure to the SectionalThumbnail (should you
            have requested it).

        measures: List of Measures that were found for the
            Variant on the Sectional.

    !!! note
        Be aware that requesting the measures will
        yield one responds for each variant and sectional
    """
    variant_id: UUID4
    sectional_id: UUID4
    measures: List[W24Measure]


class W24AskVariantLeaders(W24Ask):
    """ With this Ask you are requesting the complete
    list of all leaders that were detected on the
    variant

    !!! danger
        This feature is currently in invitation-only beta
        and will only be answered if this features has been
        activated for your account. Otherwise the request
        will be ignored.
    """
    ask_type = W24AskType.VARIANT_LEADERS


class W24AskVariantLeadersResponse(BaseModel):
    """ Response object corresponding to the
    W24AskVariantLeaders.


    Attributes:
        variant_id: Unique ID of the variant detected on
            the Technical Drawing. Refer to the documentation
            on Variants for details.

        sectional_id: Unique ID of the sectional on which the
            Leader was detected. This allows you to associate
            the Leader to the SectionalThumbnail (should you
            have requested it).

        leaders: List of Leaders that were found for the
            Variant on the Sectional.
    """
    variant_id: UUID4
    sectional_id: UUID4
    leaders: List[W24Leader]


class W24AskVariantMaterial(W24Ask):
    """ This ask requests the material of the individual variant.
    It will now only consider the material that is listed on the
    TitleBlock, but also consider material information that is
    found as text on the Canvas.

    Attributes:
        material_hint: If already know the material that "should"
            be indicated on the drawing, you are welcome to submit
            it here as hint. This will allow us to improve the
            accuracy of our algorithms. Feel free to use any material
            designation that is convenient.

    !!! danger
        This feature is currently in invitation-only beta
        and will only be answered if this features has been
        activated for your account. Otherwise the request
        will be ignored.
    """
    ask_type = W24AskType.VARIANT_MATERIAL

    material_hint: Optional[str] = None


class W24AskTitleBlock(W24Ask):
    """ This ask requests all information that
    we can obtain from the title block
    """
    ask_type = W24AskType.TITLE_BLOCK


class W24AskVariantGDTs(W24Ask):
    """ This Ask requests the list of all
    Geometric Dimensions and Tolerations
    that were detected for the Variant.
    """
    ask_type = W24AskType.VARIANT_GDTS


class W24AskVariantGDTsResponse(BaseModel):
    """ Response object corresponding to the
    W24AskVariantGDTs.

    Attributes:
        variant_id: Unique ID of the variant detected on
            the Technical Drawing. Refer to the documentation
            on Variants for details.

        sectional_id: Unique ID of the sectional on which the
            GD&T was detected. This allows you to associate
            the Leader to the SectionalThumbnail (should you
            have requested it).

        gdts: List of GD&Ts that were found for the
            Variant on the Sectional.
    """
    variant_id: UUID4
    sectional_id: UUID4
    gdts: List[W24GDT]


class W24AskTrain(W24Ask):
    """ If you submit this Ask, we will use your request
    to train and improve our models. It does not trigger a response.

    !!! danger
        This is deprected. Please use the attribute is_training=True
        instead.
    """
    ask_type = W24AskType.TRAIN


class W24AskVariantCAD(W24Ask):
    """ By sending this Ask, you are requesting
    an associated CAD model

    Attributes:
        output_format: Output format in which to generate
            the CAD file.

    !!! note
        This Ask will currently return a DXF approximation
        of a flat part and can only be used for 2 dimensional
        applications (e.g. sheet metal).
    """
    ask_type = W24AskType.VARIANT_CAD

    output_format: W24FileFormatVariantCAD = W24FileFormatVariantCAD.DXF


class W24AskVariantCADResponse(BaseModel):
    """ Response object corresponding to the W24AskVariantCad.

    Attributes:
        variant_id: Unique ID of the variant detected on
            the Technical Drawing. Refer to the documentation
            on Variants for details.

        num_sectionals: Number of sectionals that were detected
            on the Variant. This allows you to better classify
            the type of file you are dealing with.

        num_angles: Number of  angles that were detected on the Variant.
            This allows you to better classify the type of file you are
            dealing with.



    !!!! note
        Be aware that requesting the measures will yield one response
        for each variant. Refer to the Variant documentation for
        details

    !!! note
        The cad file will be returned as part of the payload_bytes
        and needs to be accessed directly. If you are using your own
        client implementation, you need to obtain the information from
        the payload_url (and submit the correct token).


    !!! danger
        The attributes num_sectionals and num_angles will be deprected
        soon in favor of a part classifier. Please reach out to us
        before using these two attributes.

    """
    variant_id: UUID4

    num_sectionals: int = 0

    num_angles: int = 0


W24AskUnion = Union[
    W24AskCanvasThumbnail,
    W24AskPageThumbnail,
    W24AskSectionalThumbnail,
    W24AskSheetThumbnail,
    W24AskTitleBlock,
    W24AskTrain,
    W24AskVariantGDTs,
    W24AskVariantLeaders,
    W24AskVariantMaterial,
    W24AskVariantMeasures,
    W24AskVariantCAD,
]
""" Union of all W24Asks to ensure proper deserialization """
