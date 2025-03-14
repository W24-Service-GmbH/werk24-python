"""Definition of all W24Ask types that are understood by the Werk24 API.
"""

from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Set, Tuple, Type, Union

from pydantic import UUID4, BaseModel, Field, HttpUrl, model_validator
from pydantic_extra_types.color import Color

from .alignment import W24AlignmentHorizontal, W24AlignmentVertical
from .alphabet import W24Alphabet
from .angle import W24Angle
from .balloon import W24Balloon
from .file_format import (
    W24FileFormatTable,
    W24FileFormatThumbnail,
    W24FileFormatVariantCAD,
)
from .font import W24Font, W24FontMap
from .gdt import W24GDT
from .general_tolerances import W24GeneralTolerances
from .geometric_shape import W24GeometricShapeCuboid, W24GeometricShapeCylinder
from .icon import W24Icon
from .leader import W24Leader
from .material import W24Material
from .measure import W24Measure
from .note import W24Note
from .part_family import W24PartFamilyCharacterization
from .process import W24Process
from .projection_method import W24ProjectionMethod
from .radius import W24Radius
from .revision_table import W24RevisionTable
from .roughness import W24GeneralRoughness, W24Roughness, W24RoughnessReference
from .thread_element import W24ThreadElement
from .title_block import W24TitleBlock
from .unit import W24UnitSpecification


class W24AskType(str, Enum):
    """List of all Ask Type supported by the current
    API version. This list will grow with future releases.

    """

    CANVAS_THUMBNAIL = "CANVAS_THUMBNAIL"
    """Thumbnail of the canvas (i.e., the part of the
    sheet that contains the geometry)
    """

    NOTES = "NOTES"
    """Notes of the Sectional and the Canvas
    """

    PAGE_THUMBNAIL = "PAGE_THUMBNAIL"
    """Thumbnail of the overall page - rotated and with
    surrounding white space removed
    """

    PART_FAMILY_CHARACTERIZATION = "PART_FAMILY_CHARACTERIZATION"
    """Ask that triggers a post processor corresponding to the
    part family
    """
    PRODUCT_PMI_EXTRACT = "PRODUCT_PMI_EXTRACT"
    """Ask for the PMI Extract Product
    """

    REVISION_TABLE = "REVISION_TABLE"
    """Ask for the Revision Table
    """

    SECTIONAL_THUMBNAIL = "SECTIONAL_THUMBNAIL"
    """Thumbnail of a sectional on the canvas.
    Here the sectional describes both cuts and perspectives
    """

    SHEET_THUMBNAIL = "SHEET_THUMBNAIL"
    """Thumbnail of the sheet (i.e., the part of the
    page that is described by the surrounding frame)
    """

    SHEET_ANONYMIZATION = "SHEET_ANONYMIZATION"
    """Thumbnail of the sheet with all references to
    the original author removed.
    """

    SHEET_REBRANDING = "SHEET_REBRANDING"
    """Full rebranding of the sheet.
    """

    TITLE_BLOCK = "TITLE_BLOCK"
    """Ask for all information that is available on the
    title block
    """

    TRAIN = "TRAIN"
    """Supplying the request for training only without
    expecting a response.
    """

    VARIANT_ANGLES = "VARIANT_ANGLES"
    """Requests the all Angles on the variant
    """

    VARIANT_CAD = "VARIANT_CAD"
    """Requests the generation of a CAD file
    """

    VARIANT_GDTS = "VARIANT_GDTS"
    """List of Geometric Dimensions and Tolerances detected
    on the Sectionals associated with the variant
    """

    VARIANT_LEADERS = "VARIANT_LEADERS"
    """List of Leaders that were detected on the Sectional
    """

    VARIANT_MATERIAL = "VARIANT_MATERIAL"
    """Material that was detected on the data cells of the
    drawing or within a variant table
    """

    VARIANT_MEASURES = "VARIANT_MEASURES"
    """List of Measures that were found on the Sectionals
    associated with the variant
    """

    VARIANT_RADII = "VARIANT_RADII"
    """List of all Radii that were found on teh Sectionals
    associated with the variant
    """

    VARIANT_ROUGHNESSES = "VARIANT_ROUGHNESSES"
    """List of Roughnesses that were found on the Sectionals
    associated with the variant
    """

    VARIANT_EXTERNAL_DIMENSIONS = "VARIANT_EXTERNAL_DIMENSIONS"
    """Ask for the external dimensions
    """

    VARIANT_THREAD_ELEMENTS = "VARIANT_THREAD_ELEMENTS"
    """Ask for the thread elements of the variant
    """

    VARIANT_TOLERANCE_ELEMENTS = "VARIANT_TOLERANCE_ELEMENTS"
    """Ask for the tolerance elements of the variant
    """

    VARIANT_PROCESSES = "VARIANT_PROCESSES"
    """Ask for the Processes associated with the variant.
    """

    INTERNAL_SCREENING = "INTERNAL_SCREENING"
    """Ask for internal screening - not available through public API
    """

    DEBUG = "DEBUG"
    """ Ask for internal debugging - internal use only
    """

    EXCEL_SUMMARY = "EXCEL_SUMMARY"
    """ Ask to obtain an excel summary of the document.
    """

    CANVAS_TABLES = "CANVAS_TABLES"
    """ Ask to obtain the tables from the canvas.
    """


class W24Ask(BaseModel):
    """Base model from which all Asks inherit

    Attributes:

        ask_type: Type of the requested Ask. Used
            for de-serialization.

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

    version: Literal["v1"] = "v1"
    ask_type: W24AskType
    is_training: bool = False


class W24AskThumbnail(W24Ask):
    """Base model for features that request a thumbnail.

    Attributes:

        file_format: File format in which you wish to obtain
            the result. Currently only JPEG is supported.

        balloons: List of the balloons to add to the thumbnail.
            By default that's an empty list.

    !!! note
        At this stage, the API will return a high-resolution
        gray-level image. Future releases might allow you to
        request color images or to set a resolution limit.
        If this is a priority to you, please let us know.
    """

    file_format: W24FileFormatThumbnail = W24FileFormatThumbnail.JPEG
    balloons: List[W24Balloon] = []


class W24AskPageThumbnail(W24AskThumbnail):
    """Requests a thumbnail for each page in the document;
    rotated, and with the surrounding white-space removed.

    !!! note
        We preprocess the page so that it is always white-on-black,
        even when the Technical Drawing that you submitted was
        black-on-white.
    """

    ask_type: W24AskType = W24AskType.PAGE_THUMBNAIL


class W24AskSheetThumbnail(W24AskThumbnail):
    """Requests a thumbnail of each sheet on each page in
    the document. The sheet will only contain the pixels within
    the main frame that surrounds the canvas and header cells.

    !!! note
        We preprocess the sheet so that it is always white-on-black,
        even when the Technical Drawing that you submitted was
        black-on-white.
    """

    ask_type: W24AskType = W24AskType.SHEET_THUMBNAIL


class W24AskSheetAnonymization(W24AskThumbnail):
    """Requests an ANONYMIZED thumbnail of each sheet on each page
    in the document. The sheet will only contain the pixels within
    the main frame that surrounds the canvas and header cells.

    !!! note
        We preprocess the sheet so that it is always white-on-black,
        even when the Technical Drawing that you submitted was
        black-on-white.

    Attributes:

        replacement_logo (bytes): SVG version of the logo that
            shall be used to replace the logo on the drawing.

        identification_snippets (List[str]): List of string values
            that might identify the authoring company. The software
            will actively look for such text segments in the data
            and replace them with white pixels.

        redact_employee_names (bool): Redact the employee names
            when they are indicated by a caption such as
            "Drawn by"

        redact_cage_code (bool): Redact the CAGE Code (
            Commercial and Government Entity Code) typically
            used for US-government suppliers

        fill_color (Tuple[int,int,int]): Color that shall be used
            to fill the pixels that are to be redacted. Currently
            only grayscale is supported.

        output_format (W24FileFormatThumbnail): Output format in
            which to generate the anonymized sheet.

        pagewise_response (bool): If set to True, the response will be pagewise.
            If set to False, the response will correspond to the complete document.
            This option is only available for output formats that support document responses.

    """

    ask_type: W24AskType = W24AskType.SHEET_ANONYMIZATION

    replacement_logo_url: Optional[HttpUrl] = None

    identification_snippets: List[str] = []

    redact_employee_names: bool = False

    redact_cage_code: bool = False

    fill_color: Tuple[int, int, int] = (255, 255, 255)

    output_format: W24FileFormatThumbnail = Field(
        description="Output format in which to generate the anonymized sheet.",
        examples=[W24FileFormatThumbnail.PNG, W24FileFormatThumbnail.PDF],
        default=W24FileFormatThumbnail.PNG,
    )

    pagewise_response: bool = Field(
        description=(
            "If set to True, the response will be pagewise. "
            "If set to False, the response will correspond to the complete document. "
            " This option is only available for output formats that support document responses."
        ),
        default=True,
    )


class W24AskPartFamilyCharacterization(W24Ask):
    """Triggers a post-processor that turns the raw data into a
    dictionary of attributes characteristic for the part family.

    E.g. a Screw could have the following attributes:
    * Drive Type
    * Head diameter
    * Head length
    * Thread
    * Thread length

    The definition of a part family can be done in a Part Family
    Template and is implemented by Werk24 on the backend - where
    it has access to more granular data.

    Attributes:

        part_family_id (UUID4): Unique part family identifier
            that we will provide to you after the part family
            post processor is implemented.
    """

    ask_type: W24AskType = W24AskType.PART_FAMILY_CHARACTERIZATION

    part_family_id: UUID4


class W24AskPartFamilyCharacterizationResponse(BaseModel):
    """Response object corresponding to a PartFamilyCharacterization request.


    Attributes:

        page_id (UUID4): Id of the page that specified the part_family

        sheet_id (UUID4):Id of the sheet
    """

    page_id: UUID4
    sheet_id: UUID4
    part_family_characterizations: List[W24PartFamilyCharacterization]


class W24AskCanvasThumbnail(W24AskThumbnail):
    """Requests a thumbnail of each canvas in each sheet.
    The canvas describes the "drawing area" of the sheet.

    !!! note
        We preprocess the canvas so that it is always white-on-black,
        even when the Technical Drawing that you submitted was
        black-on-white.

    Attributes:

        remove_canvas_notes__dangerous (bool): Remove the canvas
            notes from the canvas thumbnail.

            !!! DANGEROUS: chances are that you are removing
            !!! important information. Run a risk analysis
            !!! before using this attribute
    """

    ask_type: W24AskType = W24AskType.CANVAS_THUMBNAIL

    remove_canvas_notes__dangerous: bool = False


class W24AskSectionalThumbnail(W24AskThumbnail):
    """The W24AskPlaneThumbnail requests a thumbnail
    of each sectional on each sheet in the document.

    !!! note
        We preprocess the sectional so that it is always white-on-black,
        even when the Technical Drawing that you submitted was
        black-on-white.
    """

    ask_type: W24AskType = W24AskType.SECTIONAL_THUMBNAIL


class W24AskVariantAngles(W24Ask):
    """With this Ask you are requesting the list of all
    measures that were detected on all sectionals of a
    variant.
    """

    ask_type: W24AskType = W24AskType.VARIANT_ANGLES


class W24AskVariantAnglesResponse(BaseModel):
    """ResponseType associated with the
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


class W24AskVariantRoughnesses(W24Ask):
    """With this Ask you are requesting the list of all
    roughnesses (surface symbols) that were detected for
    the variant.
    """

    ask_type: W24AskType = W24AskType.VARIANT_ROUGHNESSES


class W24AskVariantRoughnessesResponse(BaseModel):
    """Response object corresponding to the
    W24AskVariantRoughnesses ask.

    Attributes:

        variant_id: Unique ID of the variant detected on
            the Technical Drawing. Refer to the documentation
            on Variants for details.

        sectional_id: Unique ID of the sectional on which the
            Measure was detected. This allows you to associate
            the Measure to the SectionalThumbnail (should you
            have requested it).

        roughnesses: List of Roughnesses that were found for the
            Variant on the Sectional.
    """

    variant_id: UUID4
    sectional_id: UUID4
    roughnesses: List[W24Roughness]


class W24AskVariantRadii(W24Ask):
    """With this Ask you are requesting the list of all
    radii that were detected for the variant.
    """

    ask_type: W24AskType = W24AskType.VARIANT_RADII


class W24AskVariantRadiiResponse(BaseModel):
    """Response object corresponding to the
    W24AskVariantRadii ask.

    Attributes:

        variant_id: Unique ID of the variant detected on
            the Technical Drawing. Refer to the documentation
            on Variants for details.

        sectional_id: Unique ID of the sectional on which the
            Measure was detected. This allows you to associate
            the Measure to the SectionalThumbnail (should you
            have requested it).

        radii: List of Radii that were found for the
            Variant on the Sectional.
    """

    variant_id: UUID4
    sectional_id: UUID4
    radii: List[W24Radius]


class W24AskVariantMeasures(W24Ask):
    """With this Ask you are requesting the complete
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

    ask_type: W24AskType = W24AskType.VARIANT_MEASURES

    confidence_min: float = 0.2


class W24AskVariantMeasuresResponse(BaseModel):
    """Response object corresponding to the
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
    """With this Ask you are requesting the complete
    list of all leaders that were detected on the
    variant

    !!! danger
        This feature is currently in invitation-only beta
        and will only be answered if this features has been
        activated for your account. Otherwise the request
        will be ignored.
    """

    ask_type: W24AskType = W24AskType.VARIANT_LEADERS


class W24AskVariantLeadersResponse(BaseModel):
    """Response object corresponding to the
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
    """This ask requests the material of the individual variant.
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

    ask_type: W24AskType = W24AskType.VARIANT_MATERIAL

    material_hint: Optional[str] = None


class W24AskTitleBlock(W24Ask):
    """This ask requests all information that
    we can obtain from the title block
    """

    ask_type: Literal[W24AskType.TITLE_BLOCK] = W24AskType.TITLE_BLOCK


class W24AskRevisionTable(W24Ask):
    """With this Ask you are requesting the list of all
    revision tables in the document
    """

    ask_type: W24AskType = W24AskType.REVISION_TABLE


class W24AskRevisionTableResponse(BaseModel):
    """Response object corresponding toi the
    W24AskRevisionTable

    Attributes:

        revision_table: RevisionTable object with all
            the content that was extracted from the
            drawing
    """

    revision_table: W24RevisionTable


class W24AskVariantGDTs(W24Ask):
    """This Ask requests the list of all
    Geometric Dimensions and Tolerances
    that were detected for the Variant.
    """

    ask_type: W24AskType = W24AskType.VARIANT_GDTS


class W24AskVariantGDTsResponse(BaseModel):
    """Response object corresponding to the
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
    """If you submit this Ask, we will use your request
    to train and improve our models. It does not trigger a response.

    !!! danger
        This is deprecated. Please use the attribute is_training=True
        instead.
    """

    ask_type: W24AskType = W24AskType.TRAIN


class W24AskVariantCAD(W24Ask):
    """By sending this Ask, you are requesting
    an associated CAD model

    Attributes:

        output_format: Output format in which to generate
            the CAD file.

    !!! note
        This Ask will currently return a DXF approximation
        of a flat part and can only be used for 2 dimensional
        applications (e.g. sheet metal).
    """

    ask_type: W24AskType = W24AskType.VARIANT_CAD

    output_format: W24FileFormatVariantCAD = W24FileFormatVariantCAD.DXF


class W24AskVariantCADResponse(BaseModel):
    """Response object corresponding to the W24AskVariantCad.

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
        The attributes num_sectionals and num_angles will be deprecated
        soon in favor of a part classifier. Please reach out to us
        before using these two attributes.

    """

    variant_id: UUID4

    num_sectionals: int = 0

    num_angles: int = 0


class W24AskVariantExternalDimensions(W24Ask):
    """Ask object to request the external dimensions of each
    variant on the Document.
    """

    ask_type: W24AskType = W24AskType.VARIANT_EXTERNAL_DIMENSIONS


class W24AskVariantExternalDimensionsResponse(BaseModel):
    """Response object corresponding to the W24AskVariantExternalDimensions

    Attributes:

        variant_id (UUID4): Unique ID of the variant detected on the
            Technical Drawing. Refer to the documentation on Variants
            for details.

        enclosing_cuboid (W24GeometricShapeCuboid): Cuboid that encloses
            the complete geometric shape of the part

        enclosing_cylinder (W24GeometricShapeCuboid): Cylinder that encloses
            the complete geometric shape of the part

        confidence (float): Confidence that the reading is correct.

        !!! the cuboid and cylinder are not necessarily aligned. So might
        !!! receive different depths of the cuboid and the cylinder.
    """

    variant_id: UUID4
    enclosing_cuboid: Optional[W24GeometricShapeCuboid]
    enclosing_cylinder: Optional[W24GeometricShapeCylinder]
    confidence: float


class W24AskProductPMIExtract(W24Ask):
    """Ask object to request the PMIExtract Product."""

    ask_type: W24AskType = W24AskType.PRODUCT_PMI_EXTRACT


class W24AskProductPMIExtractResponse(BaseModel):
    """Response object corresponding to the W24AskProduct PMIExtract

    Attributes:

        variant_id (UUID4): Unique ID of the variant detected on the
            Technical Drawing. Refer to the documentation on Variants
            for details.

        material (Optional[W24Material]): Material that was detected on
            the technical drawing. If no material was detected,
            this is set to None.

        general_tolerances (Optional[W24GeneralTolerances]): General tolerances
            detected on the drawing. This will automatically translate the
            general tolerances detected on the canvas notes to an ISO-2768
            class. None if no general tolerances are detected.

        measures (List[W24Measure]): List of the available measures on
            the drawing. Note: in the PMIExtract, the position will not be
            returned.

        gdts (List[W24GDT]): List of the detected GD&Ts. Note: in the
            PMIExtract, the position will not be returned.

        radii (List[W24Radius]): List of the detected Radii. Note: in the
            PMIExtract, the position will not be returned.

        roughnesses (List[W24Roughness]): List of the detected
            roughnesses. Note: in the PMIExtract, the position will not
            be returned.

        general_roughnesses (List[W24GeneralRoughness]): List of the detected
            general roughnesses. Note: in the PMIExtract, the position will not
            be returned.

        reference_roughnesses (List[W24RoughnessReference]): List of the
            detected reference roughnesses. Note: in the PMIExtract, the position will not
            be returned.

        unit_specifications (List[W24UnitSpecification]): List of the detected
            unit specifications.

        projection_method (Optional[W24ProjectionMethod]): Projection method
            indicated on the drawing. None if no projection method was detected.
    """

    variant_id: UUID4
    material: Optional[W24Material]
    general_tolerances: Optional[W24GeneralTolerances]
    measures: List[W24Measure]
    gdts: List[W24GDT]
    radii: List[W24Radius]
    roughnesses: List[W24Roughness]
    general_roughnesses: List[W24GeneralRoughness] = []
    reference_roughnesses: List[W24RoughnessReference] = []
    unit_specifications: List[W24UnitSpecification] = []
    projection_method: Optional[W24ProjectionMethod] = Field(
        None,
        description="Projection method indicated on the drawing. None if no projection method was detected.",
        examples=[W24ProjectionMethod.FIRST_ANGLE, W24ProjectionMethod.THIRD_ANGLE],
    )


class W24AskVariantThreadElements(W24Ask):
    """Ask object to obtain the thread elements"""

    ask_type: W24AskType = W24AskType.VARIANT_THREAD_ELEMENTS


class W24AskVariantThreadElementsResponse(BaseModel):
    """Response object corresponding to the W24AskVariantThreadElements

    Attributes:

        variant_id (UUID4): Unique ID of the variant detected on the
            Technical Drawing. Refer to the documentation on Variants
            for details.

    """

    variant_id: UUID4
    sectional_id: UUID4
    thread_elements: List[W24ThreadElement]


class W24AskNotes(W24Ask):
    """Ask all the notes on the Canvas and the sectionals"""

    ask_type: W24AskType = W24AskType.NOTES


class W24AskNotesResponse(BaseModel):
    """Response to the W24AskNotes

    Attributes:

        notes(List[W24Ask]): List of the notes that were
            identified.
    """

    notes: List[W24Note]


class W24AskInternalScreening(W24Ask):
    """Internal Ask to trigger the file screening.

    NOTE: not available on the public API.
    """

    ask_type: W24AskType = W24AskType.INTERNAL_SCREENING


class W24AskVariantProcesses(W24Ask):
    """Ask to receive the processes associated with the Variant."""

    ask_type: W24AskType = W24AskType.VARIANT_PROCESSES


class W24AskVariantProcessesResponse(BaseModel):
    """Response Model for the processes.

    Attributes:
        processes (List[W24Process]): List of all the
            processes that were identified on the drawing.
    """

    processes: List[W24Process]


class W24AskDebug(W24Ask):
    """Internal object

    Attributes:
        debug_key (str): Debugging type that you want
            to trigger.
    """

    ask_type: W24AskType = W24AskType.DEBUG
    debug_key: str = ""


class W24AskDebugResponse(BaseModel):
    repsonse_url: HttpUrl


# class W24AskVariantToleranceElements(W24Ask):
#     """Ask object to obtain the tolerance elements
#     """
#     ask_type: W24AskType = W24AskType.VARIANT_TOLERANCE_ELEMENTS

# class W24AskVariantToleranceElementsResponse(BaseModel):
#     """Response object corresponding to the W24AskVariantThreadElements

#     Attributes:

#         variant_id (UUID4): Unique ID of the variant detected on the
#             Technical Drawing. Refer to the documentation on Variants
#             for details.

#     """
#     variant_id: UUID4
#     thread_elements: List[W24ToleranceElement]


class W24SheetRebrandingColorCell(BaseModel):
    """Configuration for Color Fields on a W24AskSheetRebranding

    Tells the algorithms which color cells exist on the
    template and how to replace them. This can either be
    a text element or an image.
    """

    color: Color = Field(
        description="RGB color of the Color cell.",
    )
    text: Optional[str] = Field(
        description="Text by which the color cell shall be replaced.",
        examples=["Steel C45"],
        default=None,
    )
    font_map: Optional[W24FontMap] = Field(
        description="Object that maps alphabets to fonts",
        default=None,
    )
    icon: Optional[W24Icon] = Field(
        description="Icon that can be used instead of the text", default=None
    )
    horizontal_alignment: W24AlignmentHorizontal = W24AlignmentHorizontal.LEFT
    vertical_alignment: W24AlignmentVertical = W24AlignmentVertical.BOTTOM

    @model_validator(mode="after")
    def check_text_or_icon(self):
        if self.text is None and self.icon is None:
            raise ValueError("`text` or `icon` is required")
        if self.text is not None and self.icon is not None:
            raise ValueError("Cannot set `text` or `icon` together")
        return self


class W24SheetRebrandingCanvasPartition(BaseModel):
    """Partition of the Template Canvas.

    Specifies how the canvas in the template
    shall be partitioned. The rectangle of
    color `canvas_color` will be used to paste
    the canvas of the original drawing. The
    """

    canvas_color: Color = Field(
        description=(
            "Color of the rectangle on the template that "
            "can be used to paste the drawing content of "
            "the input drawing."
        ),
        # examples=[Color((58, 7, 26)), Color((97, 12, 43))],
    )
    additional_cells_colors: List[Color] = Field(
        description=(
            "Rectangle colors that can be used to paste the "
            "cells of the original drawings that are not "
            "inserted (in one of the color cells) or suppressed."
        ),
        # examples=[Color((37, 26, 0)), Color((64, 45, 0))],
    )


class W24RebrandingMetaData(BaseModel):
    """MetaData of the PDF file that is generated during the Rebranding."""

    title: str = Field(
        description=("Title of the resulting PDF file."),
        default="",
    )
    author: str = Field(
        description=("Author of the resulting PDF file."),
        default="",
    )
    subject: str = Field(
        description=("Subject of the resulting PDF file."),
        default="",
    )
    keywords: str = Field(
        description=("Keywords associated with the resulting PDF file"),
        default="",
    )
    creator: str = Field(
        description=("Creator of the resulting PDF file."),
        default="",
    )


class W24AskSheetRebranding(W24Ask):
    ask_type: W24AskType = W24AskType.SHEET_REBRANDING

    template_url: HttpUrl = Field(
        description=(
            "Publically available url from which the SVG Template can "
            "be downloaded. Please be aware that we are caching the "
            "template with a TTL of 30 min."
        ),
    )
    canvas_partitions: List[W24SheetRebrandingCanvasPartition] = Field(
        description=(
            "List of different canvas partitions. This allows you "
            "to specify how the canvas of the template shall be split. "
            "The algorithm chooses the first option that is able to "
            "accommodate all `additional` cells into the rectangles "
            "of color additional_cells_colors."
        ),
        default=[
            W24SheetRebrandingCanvasPartition(
                canvas_color=Color((58, 7, 26)),
                additional_cells_colors=[(37, 26, 0)],
            ),
            W24SheetRebrandingCanvasPartition(
                canvas_color=Color((97, 12, 43)),
                additional_cells_colors=[Color((37, 26, 0)), Color((64, 45, 0))],
            ),
        ],
    )
    color_cells: List[W24SheetRebrandingColorCell] = Field(
        description=(
            "Specifies which colored rectangles exist on the template "
            "and how they should be replaces."
        ),
        examples=[
            W24SheetRebrandingColorCell(
                color=Color((1, 30, 45)),
                text="New text",
            )
        ],
    )
    color_cell_fonts: W24FontMap = Field(
        description=(
            "Font Map that is used by default to the text elements "
            "that are inserted into the color cells. Note that you "
            "can overwrite this for each cell."
        ),
        default=(
            W24FontMap(
                font_map={
                    W24Alphabet.LATIN: W24Font(font_family="WorkSans", font_size=10),
                }
            )
        ),
    )
    additional_cell_fonts: W24FontMap = Field(
        description=("Font Map that is used when an `additional` cell is regenerated."),
        default=(
            W24FontMap(
                font_map={
                    W24Alphabet.LATIN: W24Font(font_family="WorkSans", font_size=10),
                }
            )
        ),
    )

    suppress_cell_types: Set[str] = Field(
        description=(
            "List of Field Types that shall be suppressed, i.e., not "
            "ported to the rebranded Sheet. Please get in touch with "
            "us if you wish to deviate from the default values. "
        ),
        default={
            # General Blocks
            "approval_block/*",
            "bom_block/*",
            "reference_block/*",
            "revision_block/*",
            # Identifiers
            # This includes project name etc.
            "identifier/name/*",
            "identifier/number/*",
            # Telling attributes
            "address/*",
            "cage_codes",
            "copyright",
            "department",
            "filename_drawing",
            "filename_model",
            "owner",
            "logo",
            # Standard info that you would inject into the
            # color cells.
            "designation",
            "drawing_number",
            "part_number",
            "material",
            # Misc.
            "do_not_scale_drawing",
            "software",
            "sheet_number",
            "scale",
            "version",
            "paper_size",
        },
    )

    meta_data: W24RebrandingMetaData = Field(
        description=("Metadata that you want to set for the resulting pdf file."),
        default=W24RebrandingMetaData(),
    )


class W24AskExcelSummary(W24Ask):
    ask_type: W24AskType = W24AskType.EXCEL_SUMMARY


class W24AskCanvasTables(W24Ask):
    """Ask to obtain all the canvas tables from the drawing."""

    ask_type: W24AskType = W24AskType.CANVAS_TABLES

    split_min_max_columns: bool = Field(
        description=("Split range columns into min and max columns."),
        default=False,
    )

    output_format: W24FileFormatTable = Field(
        description=("Output format in which to generate the tables."),
        default=W24FileFormatTable.CSV,
    )


W24AskUnion = Union[
    W24AskCanvasThumbnail,
    W24AskNotes,
    W24AskPageThumbnail,
    W24AskPartFamilyCharacterization,
    W24AskProductPMIExtract,
    W24AskRevisionTable,
    W24AskSectionalThumbnail,
    W24AskSheetAnonymization,
    W24AskSheetRebranding,
    W24AskSheetThumbnail,
    W24AskTitleBlock,
    W24AskTrain,
    W24AskVariantExternalDimensions,
    W24AskVariantCAD,
    W24AskVariantGDTs,
    W24AskVariantLeaders,
    W24AskVariantMaterial,
    W24AskVariantMeasures,
    W24AskVariantRadii,
    W24AskVariantRoughnesses,
    W24AskVariantThreadElements,
    W24AskInternalScreening,
    W24AskVariantProcesses,
    W24AskDebug,
    W24AskExcelSummary,
    W24AskCanvasTables,
    # W24AskVariantToleranceElements
]
"""Union of all W24Asks to ensure proper de-serialization """


def deserialize_ask_v1(
    raw: Union[Dict[str, Any], W24Ask],
) -> W24Ask:
    """Deserialize a specific ask in its raw form

    Args:
        raw (Dict[str, Any]): Raw Ask as it arrives from the
            json deserializer

    Returns:
        W24AskUnion: Corresponding ask type
    """
    if isinstance(raw, dict):
        ask_type = _deserialize_ask_type(raw.get("ask_type", ""))
        return ask_type.parse_obj(raw)

    if isinstance(raw, W24Ask):
        return raw

    raise ValueError(f"Unsupported value type '{type(raw)}'")


def _deserialize_ask_type(ask_type: str) -> Type[W24Ask]:
    """Get the Ask Class from the ask type

    Args:

        ask_type (str): Ask type in question

    Raises:

        ValueError: Raised if ask type is unknown

    Returns:

        str: Name of the AskObject
    """
    class_ = {
        "CANVAS_THUMBNAIL": W24AskCanvasThumbnail,
        "INTERNAL_SCREENING": W24AskInternalScreening,
        "NOTES": W24AskNotes,
        "PAGE_THUMBNAIL": W24AskPageThumbnail,
        "PART_FAMILY_CHARACTERIZATION": W24AskPartFamilyCharacterization,
        "PRODUCT_PMI_EXTRACT": W24AskProductPMIExtract,
        "REVISION_TABLE": W24AskRevisionTable,
        "SECTIONAL_THUMBNAIL": W24AskSectionalThumbnail,
        "SHEET_ANONYMIZATION": W24AskSheetAnonymization,
        "SHEET_THUMBNAIL": W24AskSheetThumbnail,
        "SHEET_REBRANDING": W24AskSheetRebranding,
        "TITLE_BLOCK": W24AskTitleBlock,
        "TRAIN": W24AskTrain,
        "VARIANT_EXTERNAL_DIMENSIONS": W24AskVariantExternalDimensions,
        "VARIANT_GDTS": W24AskVariantGDTs,
        "VARIANT_LEADERS": W24AskVariantLeaders,
        "VARIANT_MATERIAL": W24AskVariantMaterial,
        "VARIANT_MEASURES": W24AskVariantMeasures,
        "VARIANT_RADII": W24AskVariantRadii,
        "VARIANT_ROUGHNESSES": W24AskVariantRoughnesses,
        "VARIANT_CAD": W24AskVariantCAD,
        "VARIANT_THREAD_ELEMENTS": W24AskVariantThreadElements,
        # "VARIANT_TOLERANCE_ELEMENTS":W24AskVariantToleranceElements,
        "VARIANT_PROCESSES": W24AskVariantProcesses,
        "EXCEL_SUMMARY": W24AskExcelSummary,
        "DEBUG": W24AskDebug,
        "CANVAS_TABLES": W24AskCanvasTables,
    }.get(ask_type, None)

    if class_ is None:
        raise ValueError(f"Unknown Ask Type '{ask_type}'")

    return class_


W24AskResponse = Union[
    W24AskNotesResponse,
    W24AskPartFamilyCharacterizationResponse,
    W24AskProductPMIExtractResponse,
    W24AskRevisionTableResponse,
    W24TitleBlock,
    W24AskVariantExternalDimensionsResponse,
    W24AskVariantGDTsResponse,
    W24AskVariantLeadersResponse,
    W24AskVariantMaterial,
    W24AskVariantMeasuresResponse,
    W24AskVariantRadiiResponse,
    W24AskVariantRoughnessesResponse,
    W24AskVariantCADResponse,
    W24AskVariantThreadElementsResponse,
    W24AskVariantProcessesResponse,
]


def deserialize_ask_response(v, info) -> Optional[W24AskResponse]:
    def is_type(t):
        return info.data["message_subtype"] == t

    if is_type(W24AskType.NOTES):
        return W24AskNotesResponse.model_validate(v)

    if is_type(W24AskType.PART_FAMILY_CHARACTERIZATION):
        return W24AskPartFamilyCharacterizationResponse.model_validate(v)

    if is_type(W24AskType.PRODUCT_PMI_EXTRACT):
        return W24AskProductPMIExtractResponse.model_validate(v)

    if is_type(W24AskType.REVISION_TABLE):
        return W24AskRevisionTableResponse.model_validate(v)

    if is_type(W24AskType.TITLE_BLOCK):
        return W24TitleBlock.model_validate(v)

    if is_type(W24AskType.VARIANT_EXTERNAL_DIMENSIONS):
        return W24AskVariantExternalDimensionsResponse.model_validate(v)

    if is_type(W24AskType.VARIANT_GDTS):
        return W24AskVariantGDTsResponse.model_validate(v)

    if is_type(W24AskType.VARIANT_LEADERS):
        return W24AskVariantLeadersResponse.model_validate(v)

    if is_type(W24AskType.VARIANT_MATERIAL):
        return W24AskVariantMaterial.model_validate(v)

    if is_type(W24AskType.VARIANT_MEASURES):
        return W24AskVariantMeasuresResponse.model_validate(v)

    if is_type(W24AskType.VARIANT_RADII):
        return W24AskVariantRadiiResponse.model_validate(v)

    if is_type(W24AskType.VARIANT_ROUGHNESSES):
        return W24AskVariantRoughnessesResponse.model_validate(v)

    if is_type(W24AskType.VARIANT_CAD):
        return W24AskVariantCADResponse.model_validate(v)

    if is_type(W24AskType.VARIANT_THREAD_ELEMENTS):
        return W24AskVariantThreadElementsResponse.model_validate(v)

    if is_type(W24AskType.VARIANT_PROCESSES):
        return W24AskVariantProcessesResponse.model_validate(v)

    return v
